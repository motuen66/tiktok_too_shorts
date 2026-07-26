import time
from pathlib import Path

import gradio as gr

from src.auth.youtube_auth import get_credentials, run_oauth_flow
from src.downloader.tiktok_downloader import download_tiktok_video
from src.exceptions import AuthError, DownloadError, ValidationError, UploadError
from src.logger import setup_logger
from src.uploader.youtube_uploader import YouTubeUploader
from src.validator.video_validator import validate_for_shorts

logger = setup_logger(__name__)


def _ensure_auth():
    creds = get_credentials()
    if creds is None:
        raise AuthError(
            "YouTube not authenticated. Run 'python setup_oauth.py' first."
        )
    return creds


def process_pipeline(
    url: str,
    title: str,
    description: str,
    tags: str,
    privacy_status: str,
    progress: gr.Progress = gr.Progress(),
) -> tuple[str, str]:
    video_path: Path | None = None

    try:
        progress(0.05, desc="Checking authentication...")
        creds = _ensure_auth()

        if not url or "tiktok.com/" not in url:
            raise ValueError("Invalid TikTok URL")

        progress(0.1, desc="Downloading video...")
        video_path = download_tiktok_video(url)

        progress(0.5, desc="Validating video...")
        validation = validate_for_shorts(video_path)
        if not validation.is_valid:
            errors = "; ".join(validation.errors)
            warnings = "; ".join(validation.warnings) if validation.warnings else ""
            msg = f"Validation failed: {errors}"
            if warnings:
                msg += f"\nWarnings: {warnings}"
            raise ValidationError(msg)

        progress(0.6, desc="Uploading to YouTube...")

        def _on_upload_progress(pct: float):
            progress(0.6 + pct * 0.35, desc=f"Uploading... {pct:.0%}")

        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        uploader = YouTubeUploader(creds)
        video_id = uploader.upload_as_short(
            video_path=video_path,
            title=title,
            description=description,
            tags=tag_list,
            privacy_status=privacy_status,
            progress_callback=_on_upload_progress,
        )

        progress(1.0, desc="Done!")
        video_url = f"https://youtu.be/{video_id}"
        return video_url, ""

    except (AuthError, DownloadError, ValidationError, UploadError, ValueError) as e:
        logger.error("Pipeline failed: %s", e)
        return "", str(e)
    except Exception as e:
        logger.exception("Unexpected pipeline error")
        return "", f"Unexpected error: {e}"
    finally:
        if video_path and video_path.exists():
            for attempt in range(3):
                try:
                    video_path.unlink(missing_ok=True)
                    logger.info("Cleaned up %s", video_path)
                    break
                except PermissionError:
                    if attempt < 2:
                        time.sleep(1)
                    else:
                        logger.warning("Could not delete %s (in use)", video_path)
