"""Windows platform services for Semantic Wallpaper application."""

from .wallpaper_service import (
    WallpaperService,
    LockscreenService,
    set_wallpaper_and_lockscreen,
)

__all__ = [
    "WallpaperService",
    "LockscreenService",
    "set_wallpaper_and_lockscreen",
]