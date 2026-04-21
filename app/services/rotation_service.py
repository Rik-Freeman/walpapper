"""
Rotation service for Semantic Wallpaper application.
Handles wallpaper selection logic with time-of-day preferences and repeat avoidance.
"""

import random
from datetime import datetime
from typing import List, Optional

from .library_service import WallpaperInfo


class RotationService:
    """Service for selecting the next wallpaper based on various criteria."""

    def __init__(self, config_service=None):
        """
        Initialize rotation service.
        
        Args:
            config_service: Optional ConfigService instance for configuration
        """
        self.config_service = config_service

    def get_time_of_day_category(self) -> str:
        """
        Determine the current time of day category.
        
        Returns:
            String category: 'morning', 'day', 'evening', or 'night'
        """
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "day"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def select_next_wallpaper(
        self,
        available_wallpapers: List[WallpaperInfo],
        recent_history: List[str] = None,
        prefer_favorites: bool = True,
        use_time_of_day: bool = True
    ) -> Optional[WallpaperInfo]:
        """
        Select the next wallpaper to display.
        
        Args:
            available_wallpapers: List of usable wallpapers to choose from
            recent_history: List of recently used wallpaper paths
            prefer_favorites: If True, give preference to favorite wallpapers
            use_time_of_day: If True, consider time-of-day categories
            
        Returns:
            Selected WallpaperInfo or None if no wallpapers available
        """
        if not available_wallpapers:
            return None

        if recent_history is None:
            recent_history = []

        # Filter out recently used wallpapers
        candidates = [
            wp for wp in available_wallpapers 
            if wp.path not in recent_history
        ]

        # If all wallpapers are in recent history, use all available
        if not candidates:
            candidates = available_wallpapers

        # Apply time-of-day filtering if enabled
        if use_time_of_day and self.config_service:
            selected_categories = self.config_service.get("selected_categories", [])
            time_category = self.get_time_of_day_category()
            
            # If time-based category is in selected categories, prioritize it
            if time_category in selected_categories:
                time_candidates = [
                    wp for wp in candidates 
                    if time_category in wp.categories
                ]
                if time_candidates:
                    candidates = time_candidates

        # Apply favorite preference
        if prefer_favorites:
            favorites = [wp for wp in candidates if wp.is_favorite]
            if favorites:
                # 70% chance to pick a favorite
                if random.random() < 0.7:
                    return random.choice(favorites)

        # Random selection from remaining candidates
        return random.choice(candidates)

    def select_wallpaper_by_category(
        self,
        available_wallpapers: List[WallpaperInfo],
        category: str,
        recent_history: List[str] = None
    ) -> Optional[WallpaperInfo]:
        """
        Select a wallpaper from a specific category.
        
        Args:
            available_wallpapers: List of usable wallpapers
            category: Category name to filter by
            recent_history: List of recently used wallpaper paths
            
        Returns:
            Selected WallpaperInfo or None if no matching wallpapers
        """
        if recent_history is None:
            recent_history = []

        candidates = [
            wp for wp in available_wallpapers
            if category in wp.categories and wp.path not in recent_history
        ]

        if not candidates:
            # Fallback to any wallpaper in the category
            candidates = [
                wp for wp in available_wallpapers
                if category in wp.categories
            ]

        if not candidates:
            return None

        return random.choice(candidates)

    def select_random_wallpaper(
        self,
        available_wallpapers: List[WallpaperInfo],
        exclude_recent: bool = True,
        recent_history: List[str] = None
    ) -> Optional[WallpaperInfo]:
        """
        Select a completely random wallpaper.
        
        Args:
            available_wallpapers: List of usable wallpapers
            exclude_recent: If True, avoid recently used wallpapers
            recent_history: List of recently used wallpaper paths
            
        Returns:
            Selected WallpaperInfo or None if no wallpapers available
        """
        if not available_wallpapers:
            return None

        if exclude_recent and recent_history:
            candidates = [
                wp for wp in available_wallpapers
                if wp.path not in recent_history
            ]
            if not candidates:
                candidates = available_wallpapers
        else:
            candidates = available_wallpapers

        return random.choice(candidates)

    def get_smart_recommendation(
        self,
        available_wallpapers: List[WallpaperInfo],
        recent_history: List[str] = None
    ) -> Optional[WallpaperInfo]:
        """
        Get a smart wallpaper recommendation based on multiple factors.
        
        Factors considered:
        - Time of day
        - Favorite status
        - Recent usage
        - Variety (avoid repeats)
        
        Args:
            available_wallpapers: List of usable wallpapers
            recent_history: List of recently used wallpaper paths
            
        Returns:
            Recommended WallpaperInfo or None
        """
        return self.select_next_wallpaper(
            available_wallpapers=available_wallpapers,
            recent_history=recent_history,
            prefer_favorites=True,
            use_time_of_day=True
        )

    def should_change_wallpaper(self, last_change_time: datetime) -> bool:
        """
        Determine if wallpaper should be changed based on interval.
        
        Args:
            last_change_time: When the wallpaper was last changed
            
        Returns:
            True if wallpaper should be changed
        """
        if not self.config_service:
            return False

        if not self.config_service.get("auto_change_enabled", False):
            return False

        interval_minutes = self.config_service.get("auto_change_interval_minutes", 30)
        elapsed = (datetime.now() - last_change_time).total_seconds() / 60

        return elapsed >= interval_minutes
