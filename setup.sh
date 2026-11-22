# Copyright (c) 2026 Tanvir.
#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null 2>&1 || echo "WARNING: ffmpeg not found. Install it (brew install ffmpeg / sudo apt install ffmpeg)."
command -v python3.12 >/dev/null 2>&1 || { echo "Python 3.12 is required. Install Python 3.12 and run setup.sh again."; exit 1; }
if [ -d .venv ]; then
  if [ ! -x .venv/bin/python ] || ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)' 2>/dev/null; then
    echo "Existing .venv is not a valid Python 3.12 environment. Recreating it..."
    rm -rf .venv
  fi
fi
if [ ! -d .venv ]; then
  echo "Creating Python 3.12 environment..."
  python3.12 -m venv .venv
fi
echo "Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
[ -f .profile ] || cp .profile.example .profile
echo
echo "Done. If you have not downloaded the AI model: ollama pull qwen3.5:4b"
echo "Then run: ./run.sh"
