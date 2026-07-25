# Execution Plan: TikTok-to-YouTube-Shorts Automation Tool

## EXECUTIVE SUMMARY

**Objective:** Build a Python-based web tool that accepts a TikTok video URL, downloads it without a watermark, validates it meets YouTube Shorts requirements (9:16 vertical, <=60s), and uploads it automatically to YouTube as a Short — all through a simple Gradio web GUI.

**Proposed Tech Stack:**
| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web UI | Gradio 4.x |
| Downloader | yt-dlp (TikTok-specific extractor) |
| Video Processing | moviepy + ffmpeg |
| YouTube API | google-api-python-client (YouTube Data API v3) |
| Auth | google-auth-oauthlib (OAuth 2.0 desktop flow) |
| Config | python-dotenv + JSON |
| Logging | Python logging (file + console) |

---

## EXECUTION PLAN

### Phase 1: Project Scaffolding & Environment Setup

- [ ] Task 1.1: Initialize project structure — create folders (`src/`, `config/`, `logs/`, `downloads/`) and virtual environment `venv/`.
- [ ] Task 1.2: Create `requirements.txt` with all dependencies (gradio, yt-dlp, moviepy, google-api-python-client, google-auth-oauthlib, python-dotenv).
- [ ] Task 1.3: Create `.env.example` for YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN. Create `config/settings.py` as single source of truth.
- [ ] Task 1.4: Set up rotating file logger in `src/logger.py`.

### Phase 2: YouTube OAuth 2.0 Authentication Module

- [ ] Task 2.1: Implement `src/auth/youtube_auth.py` — class handling OAuth 2.0 desktop flow: get_credentials() loads existing refresh token, launches browser consent if missing.
- [ ] Task 2.2: Create `setup_oauth.py` — one-time CLI script for admin to generate refresh token.

### Phase 3: TikTok Downloader Module

- [ ] Task 3.1: Implement `src/downloader/tiktok_downloader.py` — download_tiktok_video(url) using yt-dlp with watermark-free format selection.
- [ ] Task 3.2: Add error handling for invalid URL, network error, private video.

### Phase 4: Video Validator Module

- [ ] Task 4.1: Implement `src/validator/video_validator.py` — validate_for_shorts(path) checks aspect ratio (~9:16) and duration (<=60s) via moviepy.
- [ ] Task 4.2: Return ValidationResult dataclass with errors and warnings list.

### Phase 5: YouTube Uploader Module

- [ ] Task 5.1: Implement `src/uploader/youtube_uploader.py` — YouTubeUploader class with upload_as_short() method.
- [ ] Task 5.2: Resumable media upload with progress callback and exponential backoff retry (3 attempts).

### Phase 6: Gradio Web UI

- [ ] Task 6.1: Implement `src/ui/app.py` — Gradio Blocks with inputs (URL, title, description, tags, privacy) and outputs (progress bar, success/error message).
- [ ] Task 6.2: Implement `src/ui/callbacks.py` — pipeline orchestrator chaining all 4 steps with progress updates.

### Phase 7: Main Entry Point & Integration

- [ ] Task 7.1: Create `app.py` — loads .env, initializes auth, launches Gradio demo.
- [ ] Task 7.2: End-to-end integration test with real TikTok URL.

### Phase 8: Error Handling, Logging & Polish

- [ ] Task 8.1: Domain-specific exceptions (AuthError, DownloadError, ValidationError, UploadError).
- [ ] Task 8.2: Detailed logging at each pipeline step.
- [ ] Task 8.3: Cleanup function to remove downloaded files after upload.

---

## SYSTEM ARCHITECTURE / DATA FLOW

```
User (Browser) -> Gradio UI @ :7860
    |
    1. Submit TikTok URL
    v
orchestrator/callbacks.py (sequential pipeline)
    |   2.          3.            4.              5.
    v    v           v             v               v
[URL Validate] -> [Downloader (yt-dlp)] -> [Validator (moviepy)] -> [Uploader (YouTube API)]
                                                                        |
                                                                        v
                                                                   YouTube Server
                                                                   (Short detected automatically)
                                                                        |
                                                                        v
                                                                   Return videoID
                                                                   -> https://youtu.be/...
```

**Step-by-step:**
1. User enters TikTok URL in Gradio -> clicks "Start"
2. URL validated for basic format (tiktok.com/)
3. yt-dlp downloads highest quality MP4 without watermark
4. moviepy opens file -> checks 9:16 ratio & <=60s duration
5. If valid, google-api-python-client uploads via videos.insert() with resumable media
6. On success, YouTube video ID returned as clickable link
7. Downloaded file deleted from disk

---

## RISKS & CONSIDERATIONS

| Risk | Impact | Mitigation |
|---|---|---|
| YouTube API Quota | ~1600 units/upload; default 10,000/day (~6 uploads) | Validate before upload; request higher quota; daily counter |
| TikTok anti-scraping / yt-dlp breakage | Watermark removal stops working | Pin yt-dlp version; monitor releases; retries; modular downloader adapter |
| YouTube Short auto-detection failure | Upload not classified as Short | Enforce exact 9:16; correct categoryId; monitor via YouTube Studio |
| OAuth token expiry | Refresh token invalidated | Handle re-auth gracefully; prompt user when refresh fails |
| Concurrent uploads | Race conditions on file paths | UUID-based filenames per session |

---

## EXECUTION ORDER

Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7 -> Phase 8
