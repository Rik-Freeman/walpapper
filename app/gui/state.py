"""State container for GUI session state."""

from typing import Optional, List, Dict, Any


class AppState:
    """Container for GUI session state."""
    
    def __init__(self):
        # Current wallpaper info
        self.current_wallpaper: Optional[str] = None
        self.current_wallpaper_path: Optional[str] = None
        
        # Library state
        self.library_items: List[Dict[str, Any]] = []
        self.selected_image: Optional[Dict[str, Any]] = None
        
        # Status and errors
        self.status_text: str = "Ready"
        self.last_error: Optional[str] = None
        
        # Download state
        self.is_downloading: bool = False
        self.download_progress: float = 0.0
        
        # Automation state
        self.automation_enabled: bool = False
        self.scheduled_tasks_exist: bool = False
        
        # Settings cache
        self.settings: Dict[str, Any] = {}
    
    def set_current_wallpaper(self, path: str):
        """Set the current wallpaper path."""
        self.current_wallpaper_path = path
        self.current_wallpaper = path.split('/')[-1] if path else None
    
    def set_status(self, status: str):
        """Set the current status text."""
        self.status_text = status
    
    def set_error(self, error: Optional[str]):
        """Set or clear the last error."""
        self.last_error = error
    
    def update_library(self, items: List[Dict[str, Any]]):
        """Update the library items list."""
        self.library_items = items
    
    def select_image(self, image: Optional[Dict[str, Any]]):
        """Select an image from the library."""
        self.selected_image = image
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update cached settings."""
        self.settings.update(settings)
    
    def clear(self):
        """Clear all state."""
        self.current_wallpaper = None
        self.current_wallpaper_path = None
        self.library_items = []
        self.selected_image = None
        self.status_text = "Ready"
        self.last_error = None
        self.is_downloading = False
        self.download_progress = 0.0
