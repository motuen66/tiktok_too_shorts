from dataclasses import dataclass, field
from pathlib import Path

from moviepy import VideoFileClip

from config.settings import ASPECT_RATIO_TOLERANCE, MAX_DURATION_SECONDS, MIN_WIDTH
from src.exceptions import ValidationError
from src.logger import setup_logger

logger = setup_logger(__name__)

SHORTS_RATIO = 9 / 16


@dataclass
class ValidationResult:
    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_for_shorts(video_path: Path) -> ValidationResult:
    result = ValidationResult()

    try:
        clip = VideoFileClip(str(video_path))
    except Exception as e:
        raise ValidationError(f"Failed to open video file: {e}") from e

    try:
        duration = clip.duration
        width = clip.size[0]
        height = clip.size[1]
        ratio = width / height if height else 0

        logger.info("Video: %dx%d, duration=%.2fs, ratio=%.4f", width, height, duration, ratio)

        if height <= width:
            result.errors.append(
                f"Video is not vertical ({width}x{height}). YouTube Shorts require 9:16 portrait orientation."
            )

        target_ratio = SHORTS_RATIO
        if abs(ratio - target_ratio) > ASPECT_RATIO_TOLERANCE:
            result.errors.append(
                f"Aspect ratio {ratio:.4f} is outside tolerance "
                f"({target_ratio:.4f} ± {ASPECT_RATIO_TOLERANCE}). "
                f"Video is {width}x{height}. Shorts require 9:16."
            )

        if duration > MAX_DURATION_SECONDS:
            result.errors.append(
                f"Duration {duration:.1f}s exceeds maximum {MAX_DURATION_SECONDS}s for YouTube Shorts."
            )

        if width < MIN_WIDTH:
            result.warnings.append(
                f"Resolution {width}x{height} is below recommended {MIN_WIDTH}px width."
            )

    finally:
        clip.close()

    result.is_valid = len(result.errors) == 0
    return result
