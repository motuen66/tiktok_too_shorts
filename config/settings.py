from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DOWNLOADS_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "app.log"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3

ASPECT_RATIO_TOLERANCE = 0.05
MAX_DURATION_SECONDS = 60
MIN_WIDTH = 720

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_CATEGORY_ID = "22"
DEFAULT_CHUNK_SIZE = 1024 * 1024
UPLOAD_RETRIES = 3
