# Contributing to ClipDude

Thanks for considering a contribution. Keep changes focused, tested, and consistent with the local-first purpose of ClipDude.

## Development setup

1. Install Python 3.10+, FFmpeg and FFprobe.
2. Run `setup.bat` on Windows or `./setup.sh` on Linux/macOS.
3. Review `.profile` for local configuration.
4. Run the test suite:

```bash
python -m pytest
```

## Guidelines

- Keep video processing local unless a feature explicitly requires an optional provider.
- Never add social-platform publishing, account OAuth, or automatic posting.
- Keep secrets out of source control and browser code.
- Validate user-controlled paths, settings, and request data.
- Add or update tests for backend behavior and rendering settings.
- Keep the interface responsive, accessible, and usable with keyboard navigation.
- Preserve bundled font and dependency license notices.
- Update `README.md` when adding or changing user-facing functionality.

## Pull requests

Describe the behavior change, the reason for it, and how it was tested. Include screenshots for significant interface changes where practical.
