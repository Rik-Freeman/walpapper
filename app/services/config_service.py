"""
Configuration service for Semantic Wallpaper application.
Manages loading, saving, validation, and defaults for app settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigService:
    """Service for managing application configuration."""

    DEFAULT_CONFIG = {
        "library_path": str(Path.home() / ".semantic_wallpaper" / "wallpapers"),
        "cache_path": str(Path.home() / ".semantic_wallpaper" / "cache"),
        "selected_categories": ["nature", "architecture", "abstract"],
        "enabled_sources": ["picsum", "akspic"],
        "auto_change_enabled": False,
        "auto_change_interval_minutes": 30,
        "lockscreen_enabled": True,
        "notifications_enabled": True,
        "blacklist": [],
        "favorites": [],
        "recent_history": [],
        "min_resolution_width": 1920,
        "min_resolution_height": 1080,
        "theme": "dark",
        "max_cache_size_mb": 500,
        "history_size": 10,
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize config service with optional custom config path."""
        if config_path:
            self.config_path = Path(config_path)
        else:
            config_dir = Path.home() / ".semantic_wallpaper" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"

        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load configuration from file, applying defaults for missing fields."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults to ensure all fields exist
                self._config = {**self.DEFAULT_CONFIG, **loaded_config}
                self._ensure_directories()
                return self._config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}. Using defaults.")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self._ensure_directories()
            self.save()
        
        return self._config

    def save(self) -> bool:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def _ensure_directories(self):
        """Ensure all configured directories exist."""
        dirs_to_create = [
            self._config.get("library_path"),
            self._config.get("cache_path"),
            str(Path.home() / ".semantic_wallpaper" / "logs"),
            str(Path.home() / ".semantic_wallpaper" / "thumbnails"),
            str(Path.home() / ".semantic_wallpaper" / "data"),
        ]
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value and save."""
        if key in self.DEFAULT_CONFIG or key.startswith("_"):
            self._config[key] = value
            return self.save()
        return False

    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values at once."""
        for key, value in updates.items():
            if key in self.DEFAULT_CONFIG:
                self._config[key] = value
        return self.save()

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        library_path = self.get("library_path")
        if not library_path or not Path(library_path).exists():
            errors.append(f"Library path does not exist: {library_path}")
        
        cache_path = self.get("cache_path")
        if not cache_path:
            errors.append("Cache path is not configured")
        
        interval = self.get("auto_change_interval_minutes", 0)
        if interval < 1:
            errors.append("Auto change interval must be at least 1 minute")
        
        min_width = self.get("min_resolution_width", 0)
        min_height = self.get("min_resolution_height", 0)
        if min_width < 100 or min_height < 100:
            errors.append("Minimum resolution values are too low")
        
        return errors

    def add_to_blacklist(self, wallpaper_id: str) -> bool:
        """Add a wallpaper to the blacklist."""
        blacklist = self.get("blacklist", [])
        if wallpaper_id not in blacklist:
            blacklist.append(wallpaper_id)
            return self.set("blacklist", blacklist)
        return False

    def remove_from_blacklist(self, wallpaper_id: str) -> bool:
        """Remove a wallpaper from the blacklist."""
        blacklist = self.get("blacklist", [])
        if wallpaper_id in blacklist:
            blacklist.remove(wallpaper_id)
            return self.set("blacklist", blacklist)
        return False

    def add_to_favorites(self, wallpaper_id: str) -> bool:
        """Add a wallpaper to favorites."""
        favorites = self.get("favorites", [])
        if wallpaper_id not in favorites:
            favorites.append(wallpaper_id)
            return self.set("favorites", favorites)
        return False

    def remove_from_favorites(self, wallpaper_id: str) -> bool:
        """Remove a wallpaper from favorites."""
        favorites = self.get("favorites", [])
        if wallpaper_id in favorites:
            favorites.remove(wallpaper_id)
            return self.set("favorites", favorites)
        return False

    def add_to_history(self, wallpaper_path: str) -> bool:
        """Add a wallpaper to recent history."""
        history = self.get("recent_history", [])
        max_size = self.get("history_size", 10)
        
        # Remove if already exists
        if wallpaper_path in history:
            history.remove(wallpaper_path)
        
        # Add to front
        history.insert(0, wallpaper_path)
        
        # Trim to max size
        history = history[:max_size]
        
        return self.set("recent_history", history)

    def get_recent_history(self) -> List[str]:
        """Get list of recently used wallpapers."""
        return self.get("recent_history", [])

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._ensure_directories()
        return self.save()
