"""Platform-specific services for Semantic Wallpaper application."""

from .windows import (
    WallpaperService,
    LockscreenService,
    set_wallpaper_and_lockscreen,
)

__all__ = [
    "WallpaperService",
    "LockscreenService",
    "set_wallpaper_and_lockscreen",
]