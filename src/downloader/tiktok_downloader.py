import uuid
from pathlib import Path

import yt_dlp

from config.settings import DOWNLOADS_DIR
from src.exceptions import DownloadError
from src.logger import setup_logger

logger = setup_logger(__name__)


def download_tiktok_video(url: str) -> Path:
    file_id = str(uuid.uuid4())
    output_path = DOWNLOADS_DIR / f"{file_id}.mp4"

    ydl_opts = {
        "format": "best[ext=mp4]",
        "format_sort": ["res", "~watermark", "codec:avc1"],
        "outtmpl": str(output_path),
        "quiet": True,
        "no_warnings": False,
        "extract_flat": False,
        "retries": 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Starting download for %s", url)
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        raise DownloadError(f"Failed to download video: {e}") from e
    except Exception as e:
        raise DownloadError(f"Unexpected download error: {e}") from e

    if not output_path.exists():
        raise DownloadError("Download completed but file not found on disk")

    logger.info("Downloaded to %s", output_path)
    return output_path
