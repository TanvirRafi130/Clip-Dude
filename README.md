# ClipDude

**ClipDude is a local-first video clipping and captioning studio.** Turn a long video into AI-selected highlights or split the complete video into sequential, captioned parts. Choose the output aspect ratio, caption style, caption pacing, watermark, and AI model, then export MP4 files locally.

**Project owner:** Tanvir  
**Copyright:** Copyright (c) 2026 Tanvir  
**License:** MIT — see [`LICENSE`](LICENSE).

ClipDude does not include a social-platform publishing or account-connection feature. It creates local video files for you to review and upload yourself wherever you choose.

---

## What ClipDude does

### 1. AI-selected clips
- Reads the source video transcript and proposes the strongest standalone moments.
- Supports a custom number of clips and custom minimum/maximum clip durations.
- Supports a topic focus, a time range, and optional extra editing instructions.
- Uses Ollama locally by default, with optional Gemini, Claude, or rule-based selection.
- Can trim long pauses and common filler words in AI-selected mode.

### 2. Split the entire video
- Cuts the complete source from the beginning to the end into consecutive segments.
- Set any positive segment duration in seconds.
- The final segment is shorter when the remaining source duration is less than one full segment.
- Keeps the split boundaries sequential and does not apply pause trimming.
- Select a caption style separately from the AI-selected clip style.
- Optionally burns a `PART 01 / 08` sequence label into each exported segment.

### 3. Caption studio
- Twelve built-in caption looks, including bold yellow, green pop, comic, impact, tall, clean white, progressive reveal, electric cyan, neon pink, minimal subtitle, neon glow, and classic subtitle.
- Choose lower-third, center, or upper-third caption placement.
- Control the number of words grouped together and the maximum caption line length.
- Adjust minimum word-display time to reduce rapid visual changes.
- Romanize non-Latin captions into Latin letters without translating the language.
- Select a separate installed Ollama model for romanization.

### 4. Branding and output
- Burn a text watermark into the entire rendered video.
- Pin the watermark to any corner or animate it around the frame.
- Choose from eight output ratios: `9:16`, `3:4`, `4:5`, `1:1`, `5:4`, `4:3`, `16:9`, and `21:9`.
- Preview videos without cropping their aspect ratio in the dashboard.
- Download individual clips or a ZIP containing all finished clips.
- MP4 files include embedded copyright/creator metadata identifying Tanvir and ClipDude.

### 5. Local-first processing
- Video files are processed on your computer.
- Ollama is the default local AI provider and does not require an API key.
- Whisper transcription is used when suitable source captions are not available. Silent videos can still be sequentially split; AI highlight selection requires a usable transcript.
- The app runs as a local web interface at `http://127.0.0.1:8765`.

---

## Requirements

| Requirement | Purpose |
|---|---|
| Python 3.10 or newer | Web application and processing pipeline |
| FFmpeg + FFprobe | Video/audio inspection, cutting, caption burn-in and encoding |
| Ollama (recommended) | Local AI clip selection and romanization |
| Internet connection | Required for downloading a video from a public URL and installing dependencies/models |
| Sufficient free disk space | Source videos, temporary files, rendered clips and Whisper models |

A GPU is optional. CPU-only processing works, but transcription and rendering can take substantially longer. Longer videos require more time and temporary storage. ClipDude does not impose a fixed four-hour source-duration ceiling or a fixed application-level upload byte ceiling; practical limits are determined by your hardware, disk space, codecs, and available memory.

### Install FFmpeg

**Windows**
1. Install FFmpeg using a trusted Windows package manager or the official FFmpeg download guidance.
2. Ensure both `ffmpeg` and `ffprobe` are available on `PATH`.
3. Open a new terminal and verify:
   ```powershell
   ffmpeg -version
   ffprobe -version
   ```

**Ubuntu / Debian / Kubuntu**
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
ffprobe -version
```

**macOS with Homebrew**
```bash
brew install ffmpeg
ffmpeg -version
ffprobe -version
```

### Install Ollama and a model

Install Ollama for your operating system, start it, and download a model:

```bash
ollama pull qwen3.5:4b
ollama list
```

You may use any model already installed in Ollama that follows structured JSON instructions reliably. Larger models may select more coherent moments but need more memory and processing time. The installed-model dropdown in ClipDude is populated from the local Ollama server.

---

## Installation

### Windows

1. Extract the complete ClipDude project folder to a location with enough free disk space.
2. Install Python 3.10+ and FFmpeg.
3. Install Ollama if you want local AI selection and romanization.
4. Double-click `setup.bat`.
5. Open `.profile` in a text editor and review the settings.
6. Double-click `run.bat`.
7. Open `http://127.0.0.1:8765` in your browser if it does not open automatically.

### Linux / macOS

1. Extract the complete project folder.
2. Install Python 3.10+, FFmpeg, and optionally Ollama.
3. Open a terminal in the project directory.
4. Run:
   ```bash
   chmod +x setup.sh run.sh
   ./setup.sh
   ```
5. Edit `.profile` if you want to change the AI provider or model defaults.
6. Start the application:
   ```bash
   ./run.sh
   ```
7. Open `http://127.0.0.1:8765`.

### Manual installation

If you prefer to install the environment yourself:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

Then install and run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

---

## Configuration: `.profile`

ClipDude uses `.profile` instead of `.env` for its project-specific settings. The setup script creates `.profile` from `.profile.example` the first time it runs. The file is local configuration and is excluded from source control by `.gitignore`.

### Default local configuration

```ini
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:4b
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_CTX=8192
WHISPER_MODEL=small
```

### Optional separate romanization model

```ini
OLLAMA_MODEL=qwen3.5:4b
ROMANIZATION_OLLAMA_MODEL=qwen3.5:4b
```

The webpage allows selecting an installed model for the current job. Leaving the romanization model on its configured default uses `ROMANIZATION_OLLAMA_MODEL`, which falls back to `OLLAMA_MODEL` when not set.

### Optional cloud providers

ClipDude supports optional providers for AI moment selection. Their credentials are read from `.profile` and are not sent to the browser.

**Gemini**
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

**Claude**
```ini
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-sonnet-4-5
```

**Rule-based selection without a generative AI provider**
```ini
AI_PROVIDER=none
```

When changing providers, remove or comment out conflicting `AI_PROVIDER` entries so only one is active.

---

## Using the interface

### Choose a source
- Paste a public YouTube video URL, or
- Upload a local video file in MP4, MOV, MKV, or WebM format.

The app accepts a local file without a URL. Video URL downloads use the source downloader and may depend on the source site's availability, access rules, and format support.

### AI-selected clips
1. Choose **AI-selected clips**.
2. Set the clip count and length presets, or enter custom values.
3. Choose the output aspect ratio and framing behavior.
4. Choose the caption style.
5. Select the Ollama model if local AI selection is enabled.
6. Optionally set a topic, a source time range, and extra editing instructions.
7. Set caption pacing, romanization, and watermark options.
8. Press **Get clips**.

### Split entire video
1. Choose **Split entire video**.
2. Set the segment duration in seconds.
3. Choose the split-mode caption style independently.
4. Choose the output aspect ratio.
5. Enable part numbering if you want sequence labels.
6. Configure captions, romanization, and watermark options.
7. Press **Split full video**.

Every segment is cut in source order. For example, a 305-second video split into 60-second parts produces five 60-second parts and one 5-second final part (subject to the source container's exact duration and frame boundaries).

### Caption pace and readability
- Reduce **Words shown together** for shorter on-screen groups.
- Reduce **Maximum characters per caption line** to avoid overly wide captions.
- Increase **Minimum word display time** if the highlight changes too quickly.
- Use **Caption placement** to avoid covering faces, game HUDs, or important visual content.

The minimum display setting affects caption timing only; it does not slow down the video or alter the original audio. Larger hold times can make captions trail the speech slightly, so preview the result and choose a comfortable balance.

### Watermark
Enter the exact text to burn into the output. Select one of the four corners, or enable movement to animate it around the video frame. Leave the text empty to disable the watermark.

### Processing queue
Only one source video is processed at a time. The interface disables starting another job while the active job is running. This avoids multiple simultaneous model loads and competing video encodes.

### Results
- Play the preview directly in the dashboard.
- Use the browser's video controls for playback and fullscreen.
- The preview uses `contain` sizing so the whole output frame and its original ratio remain visible.
- Download one MP4 or use **Download all** to get a ZIP archive.
- Remove old jobs to reclaim disk space.

---

## Project structure

```text
ClipDude/
├── app/
│   ├── config.py          # Paths, .profile configuration and model settings
│   ├── local_llm.py       # Ollama connection, model discovery and JSON calls
│   ├── main.py            # FastAPI routes and single-job processing queue
│   ├── ownership.py       # Project identity and copyright metadata
│   ├── render.py          # Aspect ratios, captions, watermark and FFmpeg output
│   ├── romanize.py        # Timestamp-preserving Latin-script transliteration
│   ├── selector.py        # AI and heuristic clip selection
│   ├── source.py          # Video download, local upload and transcription
│   └── trim.py            # Pause and filler trimming
├── data/                  # Generated jobs, models and temporary work (not committed)
├── fonts/                 # Caption fonts and their license notices
├── static/
│   └── index.html         # Responsive ClipDude web interface
├── tests/                 # Automated tests
├── .profile.example       # Safe starter configuration
├── requirements.txt
├── setup.bat / setup.sh
├── run.bat / run.sh
├── LICENSE
└── README.md
```

---

## Troubleshooting

**The app says FFmpeg or FFprobe is missing**
- Install FFmpeg and ensure both commands are on `PATH`.
- Restart the terminal and ClipDude after installing.

**Ollama models do not appear in the dropdown**
- Start Ollama.
- Run `ollama list` and confirm at least one model is installed.
- Check `OLLAMA_URL` and any custom `OLLAMA_EXE` / `OLLAMA_MODELS` settings in `.profile`.
- Refresh the ClipDude page after Ollama is available.

**The selected model cannot be found**
- The selected tag must match an installed Ollama model.
- Pull it first with `ollama pull model:tag`.

**Transcription is slow**
- Whisper runs locally and can be CPU-intensive.
- Choose a smaller `WHISPER_MODEL` such as `tiny` or `base` in `.profile` if speed matters more than transcription accuracy.
- Ensure enough disk space is available for model downloads and temporary files.

**A very long source fails**
- There is no fixed four-hour duration ceiling in ClipDude, but the source still has to be readable by FFmpeg and fit within available storage and system resources.
- Try processing on a drive with more free space.
- If the source is damaged or uses an unsupported codec, convert it to a standard MP4 first.

**Captions look too fast or cover the subject**
- Increase minimum word display time.
- Reduce words per caption group and maximum characters.
- Move captions to the upper or lower third depending on the content.

**A render stops unexpectedly**
- Check free disk space.
- Check that FFmpeg can decode the original file.
- Review the terminal output for the exact FFmpeg or transcription error.

---

## Privacy, rights, and responsible use

ClipDude is designed for local processing. A public video URL is downloaded to the computer running the app; local uploads remain in the project data folder while jobs are retained. Optional cloud AI providers receive transcript/prompt data needed for selection when configured. Do not use a cloud provider if you need all processing to remain offline.

Only process videos you own or have permission to use. Respect copyright, platform terms, privacy, and applicable laws. ClipDude does not grant rights to source videos or guarantee that an exported clip is eligible for monetization.

---

## Ownership

ClipDude project source and project-specific modifications are attributed to **Tanvir**. Exported MP4 files include creator/copyright metadata. Bundled third-party fonts retain their required license notices in `fonts/`; dependencies retain their own licenses.

**Copyright (c) 2026 Tanvir.**
