# AGENTS.md — TikTok-to-YouTube-Shorts Tool

## Project Overview

Automation tool: TikTok URL -> download (no watermark) -> validate (9:16, <=60s) -> upload to YouTube as Short. Web GUI via Gradio.

## Architecture (Sequential Pipeline)

```
Gradio UI -> URLValidator -> TikTokDownloader(yt-dlp) -> VideoValidator(moviepy) -> YouTubeUploader(API v3) -> Return link
```

## Directory Layout

```
app.py                  # Entry point: loads env, launches Gradio
src/
  __init__.py
  exceptions.py         # AuthError, DownloadError, ValidationError, UploadError
  logger.py             # Rotating file + console logger
  auth/
    __init__.py
    youtube_auth.py     # OAuth 2.0 desktop flow, refresh token persistence
  downloader/
    __init__.py
    tiktok_downloader.py # yt-dlp wrapper, targets -no_wm format
  validator/
    __init__.py
    video_validator.py   # moviepy: aspect ratio + duration
  uploader/
    __init__.py
    youtube_uploader.py  # google-api-python-client, videos.insert(), resumable media
  ui/
    __init__.py
    app.py               # Gradio Blocks layout
    callbacks.py         # Pipeline orchestrator
config/
  settings.py            # All thresholds, paths, API scopes
downloads/               # Temp storage (auto-cleaned)
logs/                    # Rotating log output
.env                     # YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN (git-ignored)
requirements.txt
setup_oauth.py           # One-time CLI to generate refresh token
```

## Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# OAuth setup (one-time, run BEFORE launching app)
python setup_oauth.py

# Run
python app.py            # Launches Gradio at http://localhost:7860
```

## Key Technical Details

### TikTok Download (yt-dlp)
- Target format without watermark: filter for `"watermark": false` in formats list via `--format-sort`.
- Fallback: if no watermark-free format found, best available + log warning.
- Output template: `downloads/{uuid}.mp4` (unique per session).

### YouTube OAuth
- Scope: `https://www.googleapis.com/auth/youtube.upload`
- Flow: `InstalledAppFlow` -> saves `refresh_token` to `.env`.
- Google Cloud: enable YouTube Data API v3, create OAuth 2.0 Desktop credentials, publish app to "Testing" with test user email.

### Validation Thresholds (config/settings.py)
- ASPECT_RATIO_TOLERANCE = 0.05
- MAX_DURATION_SECONDS = 60
- MIN_WIDTH = 720 (soft warning)

### YouTube Upload
- Category ID "22" = People & Blogs.
- `privacyStatus` from dropdown (public/unlisted/private).
- `MediaFileUpload` with `resumable=True`, `chunksize=1MB`.
- No special Short flag — YouTube auto-detects from 9:16 + <=60s.

### Error Handling
- Domain exceptions: `AuthError`, `DownloadError`, `ValidationError`, `UploadError`.
- Central try/except in `callbacks.py` for user-friendly Gradio messages.
- Exponential backoff (3 retries) on YouTube API transient failures.

## Convention Notes
- All paths use `pathlib.Path`.
- Downloaded files deleted after upload via `finally` block.
- No hardcoded secrets; everything in `.env` loaded via `python-dotenv`.
