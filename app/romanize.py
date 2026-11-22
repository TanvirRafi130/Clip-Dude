# Copyright (c) 2026 Tanvir. ClipDude project source.
"""Romanize non-Latin transcript words while preserving word timings."""
from __future__ import annotations

import re
from dataclasses import replace

from . import local_llm
from .source import Word

_LATIN = re.compile(r"^[\x00-\x7F]*$")


def _schema() -> dict:
    return {
        "type": "object",
        "properties": {"words": {"type": "array", "items": {"type": "string"}}},
        "required": ["words"],
        "additionalProperties": False,
    }


def _clean_token(value: object) -> str:
    import unicodedata
    token = unicodedata.normalize("NFKC", str(value)).strip().strip('"\'`')
    # Keep punctuation but reject whitespace (one source token must remain one token).
    return token


def romanize_words(words: list[Word], style: str = "natural", progress=None,
                   model: str | None = None) -> list[Word]:
    """Romanize non-Latin transcript tokens without changing timestamps.

    Uses a dedicated Ollama model when configured. Invalid batch answers are
    retried, then the problematic tokens are sent individually for recovery.
    """
    if style not in {"natural", "pronunciation"}:
        raise ValueError("Unknown romanization style.")
    result = [replace(w) for w in words]
    indexes = [i for i, w in enumerate(words) if not _LATIN.fullmatch(w.text)]
    if not indexes:
        return result
    batch_size = 24
    batches = [indexes[i:i + batch_size] for i in range(0, len(indexes), batch_size)]
    mode = ("Use natural, commonly understood Roman spelling." if style == "natural"
            else "Prioritize pronunciation fidelity over conventional spelling.")
    system = ("You are a transliteration engine, NOT a translator. Convert each input token "
              "to Latin/English letters while preserving the spoken language and exact order. "
              "Do not translate, summarize, merge, split, or omit words. Output exactly one "
              "Latin-script token per input token, preserving punctuation. " + mode)

    def request(tokens: list[str], attempt: int) -> list[str]:
        import json
        prompt = ("Return JSON only with a 'words' array. The array must contain exactly "
                  f"{len(tokens)} strings, one per input token, in order. No explanation.\n"
                  "INPUT TOKENS: " + json.dumps(tokens, ensure_ascii=False))
        raw = (local_llm.chat_json(system, prompt, _schema(), model=model) if model
               else local_llm.chat_json(system, prompt, _schema()))
        try:
            data = json.loads(raw)
            values = data["words"]
            if not isinstance(values, list) or len(values) != len(tokens):
                raise ValueError("wrong token count")
            cleaned = [_clean_token(v) for v in values]
            if any(not x or any(ch.isspace() for ch in x) or not _LATIN.fullmatch(x) for x in cleaned):
                raise ValueError("non-Latin or multiword output")
            return cleaned
        except Exception as exc:
            raise ValueError(f"invalid transliteration output: {exc}") from exc

    try:
        for batch_no, ids in enumerate(batches, start=1):
            tokens = [words[i].text for i in ids]
            converted = None
            last_error = None
            # Retry whole batch once with an even more explicit instruction.
            for attempt in range(2):
                try:
                    converted = request(tokens, attempt)
                    break
                except Exception as exc:
                    last_error = exc
            if converted is None:
                # Recover token-by-token: smaller responses are much easier for 4B models.
                converted = []
                for token in tokens:
                    try:
                        converted.append(request([token], 1)[0])
                    except Exception as exc:
                        raise RuntimeError(
                            f"Could not romanize token {token!r} with model {model or 'configured Ollama model'}. "
                            "Try a dedicated multilingual model or disable Romanization. "
                            f"Last error: {exc}"
                        ) from exc
            for idx, token in zip(ids, converted):
                result[idx].text = token
            if progress:
                progress(batch_no, len(batches))
    finally:
        local_llm.unload(model)
    return result


def romanize_text(text: str, style: str = "natural", model: str | None = None) -> str:
    """Romanize a short hook while preserving its whitespace-separated structure."""
    if not text or _LATIN.fullmatch(text):
        return text
    parts = text.split()
    synthetic = [Word(part, float(i), float(i) + 0.5) for i, part in enumerate(parts)]
    return " ".join(w.text for w in romanize_words(synthetic, style, model=model))
