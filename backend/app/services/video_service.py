"""
Module: services.video_service
Description: Video validation helpers — format checking and duration measurement using OpenCV
"""
import pathlib
import cv2
from app.config import settings

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi"}


def validate_extension(filename: str) -> str:
    """
    Extract and validate the file extension.
    Returns the extension (with dot, lowercase) or raises ValueError.
    """
    ext = pathlib.Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: '{ext}'. Usa MP4, MOV o AVI.")
    return ext


def get_video_duration_seconds(video_path: pathlib.Path) -> float:
    """
    Measure video duration in seconds using OpenCV.
    Returns 0.0 if the file cannot be opened or FPS is invalid.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        return 0.0

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    if fps <= 0 or frame_count <= 0:
        return 0.0

    return frame_count / fps


def validate_duration(video_path: pathlib.Path) -> float:
    """
    Validate that the video does not exceed MAX_VIDEO_DURATION_SECONDS.
    Returns the measured duration if valid.
    Raises ValueError if the duration is exceeded.
    """
    duration = get_video_duration_seconds(video_path)
    max_seconds = settings.MAX_VIDEO_DURATION_SECONDS

    if duration > max_seconds:
        raise ValueError(
            f"El vídeo dura {duration:.1f}s y supera el máximo de {max_seconds}s."
        )
    return duration
