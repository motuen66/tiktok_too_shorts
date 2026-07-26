import time
import uuid
from pathlib import Path

import requests

from config.settings import DOWNLOADS_DIR
from src.exceptions import DownloadError
from src.logger import setup_logger

logger = setup_logger(__name__)

TIKWM_API_URL = "https://www.tikwm.com/api/"
REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 120
MAX_RETRIES = 3


def download_tiktok_video(url: str) -> Path:
    file_id = str(uuid.uuid4())
    output_path = DOWNLOADS_DIR / f"{file_id}.mp4"

    video_url = _fetch_video_url(url)

    _download_file(video_url, output_path)

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise DownloadError("Download completed but file is missing or empty")

    logger.info("Downloaded to %s (%d bytes)", output_path, output_path.stat().st_size)
    return output_path


def _fetch_video_url(tiktok_url: str) -> str:
    params = {"url": tiktok_url, "hd": 1}

    for attempt in range(MAX_RETRIES):
        try:
            logger.info("Fetching video info from TikWM (attempt %d/%d)", attempt + 1, MAX_RETRIES)
            resp = requests.get(TIKWM_API_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != 0:
                msg = data.get("msg", "Unknown API error")
                raise DownloadError(f"TikWM API error: {msg}")

            video_data = data.get("data")
            if not video_data:
                raise DownloadError("TikWM API returned no video data")

            video_url = video_data.get("hdplay") or video_data.get("play")
            if not video_url:
                raise DownloadError("No video URL found in TikWM response")

            return video_url

        except requests.Timeout:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning("TikWM API timeout, retrying in %ds...", wait)
                time.sleep(wait)
                continue
            raise DownloadError("TikWM API timed out after retries")
        except requests.RequestException as e:
            raise DownloadError(f"Failed to reach TikWM API: {e}") from e
        except (KeyError, ValueError, TypeError) as e:
            raise DownloadError(f"Invalid TikWM API response: {e}") from e

    raise DownloadError("Failed to fetch video URL after retries")


def _download_file(video_url: str, output_path: Path):
    try:
        logger.info("Downloading video from %s", video_url)
        resp = requests.get(video_url, timeout=DOWNLOAD_TIMEOUT, stream=True)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

    except requests.RequestException as e:
        raise DownloadError(f"Failed to download video content: {e}") from e
