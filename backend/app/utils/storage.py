"""
Module: utils.storage
Description: File system path helpers using pathlib.Path for Windows/Linux compatibility.
             All functions return Path objects and create the parent directories if needed.
"""
import pathlib
from app.config import settings


def _ensure(path: pathlib.Path) -> pathlib.Path:
    """Create all parent directories and return the path unchanged."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_storage_root() -> pathlib.Path:
    return pathlib.Path(settings.STORAGE_PATH)


def get_user_video_dir(user_id: int) -> pathlib.Path:
    base = get_storage_root() / "videos" / f"user_{user_id}"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_original_video_path(user_id: int, analysis_id: int, extension: str) -> pathlib.Path:
    """
    Return the filesystem path for the original uploaded video.
    extension must include the leading dot, e.g. '.mp4'
    """
    base = get_user_video_dir(user_id) / "original"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"analysis_{analysis_id}_original{extension}"


def get_overlay_video_path(user_id: int, analysis_id: int) -> pathlib.Path:
    """Return the filesystem path for the MediaPipe overlay video (always .mp4)."""
    base = get_user_video_dir(user_id) / "overlay"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"analysis_{analysis_id}_overlay.mp4"


def get_avatar_path(user_id: int, extension: str) -> pathlib.Path:
    """
    Return the filesystem path for a user avatar image.
    extension must include the leading dot, e.g. '.jpg'
    """
    base = get_storage_root() / "avatars"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"avatar_{user_id}{extension}"


def init_storage_dirs() -> None:
    """Create all required storage directories at application startup."""
    for subdir in ["videos", "avatars"]:
        (get_storage_root() / subdir).mkdir(parents=True, exist_ok=True)
