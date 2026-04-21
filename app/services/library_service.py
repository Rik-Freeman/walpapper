"""
Library service for Semantic Wallpaper application.
Manages local wallpaper library: scanning, metadata, filtering, favorites, blacklist.
"""

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image


@dataclass
class WallpaperInfo:
    """Information about a wallpaper file."""
    path: str
    filename: str
    size_bytes: int
    width: int
    height: int
    created_date: datetime
    modified_date: datetime
    file_hash: str
    is_favorite: bool = False
    is_blacklisted: bool = False
    categories: List[str] = None
    source: str = "local"
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []

    @property
    def resolution(self) -> str:
        """Return resolution as string (e.g., '1920x1080')."""
        return f"{self.width}x{self.height}"

    @property
    def size_mb(self) -> float:
        """Return file size in megabytes."""
        return round(self.size_bytes / (1024 * 1024), 2)


class LibraryService:
    """Service for managing the local wallpaper library."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

    def __init__(self, library_path: str, config_service=None):
        """
        Initialize library service.
        
        Args:
            library_path: Path to the wallpaper library directory
            config_service: Optional ConfigService instance for favorites/blacklist
        """
        self.library_path = Path(library_path)
        self.config_service = config_service
        self._cache: Dict[str, WallpaperInfo] = {}

    def scan_library(self, force_rescan: bool = False) -> List[WallpaperInfo]:
        """
        Scan the library directory for wallpaper files.
        
        Args:
            force_rescan: If True, rescan all files even if cached
            
        Returns:
            List of WallpaperInfo objects
        """
        if not self.library_path.exists():
            return []

        wallpapers = []
        
        # Load favorites and blacklist from config
        favorites = set()
        blacklist = set()
        if self.config_service:
            favorites = set(self.config_service.get("favorites", []))
            blacklist = set(self.config_service.get("blacklist", []))

        for file_path in self.library_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                info = self._get_wallpaper_info(file_path, favorites, blacklist, force_rescan)
                if info:
                    wallpapers.append(info)
                    self._cache[str(file_path)] = info

        return wallpapers

    def _get_wallpaper_info(
        self, 
        file_path: Path, 
        favorites: set, 
        blacklist: set,
        force_rescan: bool = False
    ) -> Optional[WallpaperInfo]:
        """Get detailed information about a wallpaper file."""
        path_str = str(file_path)
        
        # Check cache
        if not force_rescan and path_str in self._cache:
            return self._cache[path_str]

        try:
            stat = file_path.stat()
            
            # Get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Determine favorite and blacklist status
            is_favorite = path_str in favorites or file_hash in favorites
            is_blacklisted = path_str in blacklist or file_hash in blacklist

            return WallpaperInfo(
                path=path_str,
                filename=file_path.name,
                size_bytes=stat.st_size,
                width=width,
                height=height,
                created_date=datetime.fromtimestamp(stat.st_ctime),
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                file_hash=file_hash,
                is_favorite=is_favorite,
                is_blacklisted=is_blacklisted,
                categories=[],
                source="local"
            )
        except Exception as e:
            print(f"Error reading wallpaper {file_path}: {e}")
            return None

    def _calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_usable_wallpapers(
        self, 
        wallpapers: List[WallpaperInfo],
        min_width: int = 1920,
        min_height: int = 1080,
        exclude_recent: List[str] = None
    ) -> List[WallpaperInfo]:
        """
        Filter wallpapers to get usable ones based on criteria.
        
        Args:
            wallpapers: List of all wallpapers
            min_width: Minimum width in pixels
            min_height: Minimum height in pixels
            exclude_recent: List of recently used wallpaper paths to exclude
            
        Returns:
            Filtered list of usable wallpapers
        """
        if exclude_recent is None:
            exclude_recent = []

        usable = []
        for wp in wallpapers:
            # Skip blacklisted
            if wp.is_blacklisted:
                continue
            
            # Skip too small images
            if wp.width < min_width or wp.height < min_height:
                continue
            
            # Skip recently used
            if wp.path in exclude_recent:
                continue
            
            usable.append(wp)

        return usable

    def mark_favorite(self, wallpaper_path: str) -> bool:
        """Mark a wallpaper as favorite."""
        if self.config_service:
            return self.config_service.add_to_favorites(wallpaper_path)
        return False

    def unmark_favorite(self, wallpaper_path: str) -> bool:
        """Remove favorite status from a wallpaper."""
        if self.config_service:
            return self.config_service.remove_from_favorites(wallpaper_path)
        return False

    def add_to_blacklist(self, wallpaper_path: str) -> bool:
        """Add a wallpaper to the blacklist."""
        if self.config_service:
            success = self.config_service.add_to_blacklist(wallpaper_path)
            if success and wallpaper_path in self._cache:
                self._cache[wallpaper_path].is_blacklisted = True
            return success
        return False

    def remove_from_blacklist(self, wallpaper_path: str) -> bool:
        """Remove a wallpaper from the blacklist."""
        if self.config_service:
            success = self.config_service.remove_from_blacklist(wallpaper_path)
            if success and wallpaper_path in self._cache:
                self._cache[wallpaper_path].is_blacklisted = False
            return success
        return False

    def delete_wallpaper(self, wallpaper_path: str, permanent: bool = False) -> bool:
        """
        Delete a wallpaper file.
        
        Args:
            wallpaper_path: Path to the wallpaper file
            permanent: If True, permanently delete. If False, move to trash (not implemented)
            
        Returns:
            True if deletion was successful
        """
        try:
            path = Path(wallpaper_path)
            if not path.exists():
                return False
            
            if permanent:
                path.unlink()
            else:
                # For now, just delete permanently. Could implement trash later.
                path.unlink()
            
            # Remove from cache
            if wallpaper_path in self._cache:
                del self._cache[wallpaper_path]
            
            return True
        except Exception as e:
            print(f"Error deleting wallpaper {wallpaper_path}: {e}")
            return False

    def get_library_stats(self, wallpapers: List[WallpaperInfo]) -> Dict[str, Any]:
        """
        Generate statistics about the library.
        
        Args:
            wallpapers: List of wallpapers to analyze
            
        Returns:
            Dictionary with library statistics
        """
        if not wallpapers:
            return {
                "total_count": 0,
                "total_size_mb": 0,
                "favorites_count": 0,
                "blacklisted_count": 0,
                "avg_width": 0,
                "avg_height": 0,
                "min_resolution": "N/A",
                "max_resolution": "N/A",
            }

        total_size = sum(wp.size_bytes for wp in wallpapers)
        favorites_count = sum(1 for wp in wallpapers if wp.is_favorite)
        blacklisted_count = sum(1 for wp in wallpapers if wp.is_blacklisted)
        avg_width = sum(wp.width for wp in wallpapers) // len(wallpapers)
        avg_height = sum(wp.height for wp in wallpapers) // len(wallpapers)
        
        resolutions = [(wp.width, wp.height) for wp in wallpapers]
        min_res = min(resolutions, key=lambda x: x[0] * x[1])
        max_res = max(resolutions, key=lambda x: x[0] * x[1])

        return {
            "total_count": len(wallpapers),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "favorites_count": favorites_count,
            "blacklisted_count": blacklisted_count,
            "avg_width": avg_width,
            "avg_height": avg_height,
            "min_resolution": f"{min_res[0]}x{min_res[1]}",
            "max_resolution": f"{max_res[0]}x{max_res[1]}",
        }

    def find_duplicates(self, wallpapers: List[WallpaperInfo]) -> List[List[str]]:
        """
        Find duplicate wallpapers based on file hash.
        
        Args:
            wallpapers: List of wallpapers to check
            
        Returns:
            List of lists, where each inner list contains paths of duplicate files
        """
        hash_map: Dict[str, List[str]] = {}
        
        for wp in wallpapers:
            if wp.file_hash not in hash_map:
                hash_map[wp.file_hash] = []
            hash_map[wp.file_hash].append(wp.path)

        # Return only groups with duplicates
        return [paths for paths in hash_map.values() if len(paths) > 1]
