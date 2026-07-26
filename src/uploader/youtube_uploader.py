import time
from pathlib import Path
from typing import Callable

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from config.settings import (
    DEFAULT_CHUNK_SIZE,
    UPLOAD_RETRIES,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    YOUTUBE_CATEGORY_ID,
)
from src.exceptions import UploadError
from src.logger import setup_logger

logger = setup_logger(__name__)


ProgressCallback = Callable[[float], None]


class YouTubeUploader:
    def __init__(self, credentials: Credentials):
        self.service = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            credentials=credentials,
            cache_discovery=False,
        )

    def upload_as_short(
        self,
        video_path: Path,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        privacy_status: str = "public",
        progress_callback: ProgressCallback | None = None,
    ) -> str:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": YOUTUBE_CATEGORY_ID,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            chunksize=DEFAULT_CHUNK_SIZE,
            resumable=True,
        )

        request = self.service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        last_error = None

        for attempt in range(UPLOAD_RETRIES):
            try:
                while response is None:
                    status, response = request.next_chunk()
                    if status and progress_callback:
                        progress_callback(status.progress())
            except HttpError as e:
                last_error = e
                if e.resp.status in (500, 502, 503, 504):
                    wait = 2 ** attempt
                    logger.warning(
                        "YouTube API transient error (attempt %d/%d): %s. "
                        "Retrying in %ds...",
                        attempt + 1, UPLOAD_RETRIES, e, wait,
                    )
                    time.sleep(wait)
                    continue
                raise UploadError(f"YouTube API error: {e}") from e
            except Exception as e:
                raise UploadError(f"Upload failed: {e}") from e
            else:
                if response:
                    video_id = response.get("id", "")
                    logger.info("Uploaded video ID: %s", video_id)
                    if progress_callback:
                        progress_callback(1.0)
                    return video_id

        raise UploadError(
            f"Upload failed after {UPLOAD_RETRIES} retries. "
            f"Last error: {last_error}"
        )
