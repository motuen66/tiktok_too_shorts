# TikTok to YouTube Shorts

Automation tool that downloads a TikTok video without watermark, validates it for YouTube Shorts criteria, and uploads it to YouTube — all through a simple web GUI.

## Pipeline

```
TikTok URL → TikWM API → Download video → Validate (9:16, ≤60s) → Upload to YouTube as Short
```

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (bundled with moviepy dependency)
- Google Cloud project with YouTube Data API v3 enabled
- YouTube OAuth 2.0 credentials (Desktop app type)

## Setup

```powershell
# Clone and enter the project directory
cd tiktok_to_shorts_tool

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a project (or select existing)
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 Desktop** credentials
5. Copy `.env.example` to `.env` and fill in your `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`

### One-Time OAuth Setup

```powershell
python setup_oauth.py
```

This opens a browser window to authenticate with Google and grants upload permission. The refresh token is saved to `.env`.

## Usage

```powershell
venv\Scripts\activate
python app.py
```

Open `http://localhost:7860` in your browser.

1. Paste a TikTok video URL
2. Enter a title, description, and tags
3. Choose privacy (public / unlisted / private)
4. Click **Start**

The tool downloads the video, validates it, and uploads to YouTube. A link to the uploaded video is shown on success.

## Notes

- TikTok videos with HD available are downloaded at 1080p; otherwise the highest available resolution is used.
- Videos over 60 seconds or with incorrect aspect ratio are rejected before upload.
- Downloaded files are automatically cleaned up after upload.
- YouTube Shorts are auto-detected from 9:16 aspect ratio and ≤60s duration — no special flag is needed.
