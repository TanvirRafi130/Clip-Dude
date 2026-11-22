# Copyright (c) 2026 Tanvir. ClipDude project tests.
import json

from app import romanize
from app.source import Word


def test_romanize_preserves_timing_and_english(monkeypatch):
    calls = []

    def fake_chat(system, prompt, schema, model=None):
        calls.append((system, prompt, schema, model))
        tokens = json.loads(prompt.split("INPUT TOKENS: ", 1)[1])
        mapping = {"কোথায়": "Kothay", "যাচ্ছো?": "jaccho?"}
        return json.dumps({"words": [mapping.get(token, token) for token in tokens]})

    monkeypatch.setattr(romanize.local_llm, "chat_json", fake_chat)
    source = [Word("কোথায়", 1.0, 1.3), Word("যাচ্ছো?", 1.3, 1.8), Word("today", 1.8, 2.0)]
    result = romanize.romanize_words(source, model="qwen3.5:4b")

    assert [w.text for w in result] == ["Kothay", "jaccho?", "today"]
    assert [(w.start, w.end) for w in result] == [(1.0, 1.3), (1.3, 1.8), (1.8, 2.0)]
    assert len(calls) == 1
    assert "NOT a translator" in calls[0][0]


def test_romanize_skips_latin_transcript(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("LLM should not be called for Latin-only text")

    monkeypatch.setattr(romanize.local_llm, "chat_json", unexpected)
    source = [Word("Hello", 0.0, 0.2), Word("world!", 0.2, 0.5)]
    result = romanize.romanize_words(source)
    assert [w.text for w in result] == ["Hello", "world!"]


def test_romanize_text_leaves_english_unchanged(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("LLM should not be called for Latin-only text")

    monkeypatch.setattr(romanize.local_llm, "chat_json", unexpected)
    assert romanize.romanize_text("This is English!") == "This is English!"
