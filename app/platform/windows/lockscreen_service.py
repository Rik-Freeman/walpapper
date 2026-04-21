"""
Lockscreen service module for Windows platform.
Re-export from wallpaper_service for backward compatibility.
"""

from .wallpaper_service import LockscreenService, WallpaperService, set_wallpaper_and_lockscreen

__all__ = ["LockscreenService", "WallpaperService", "set_wallpaper_and_lockscreen"]
