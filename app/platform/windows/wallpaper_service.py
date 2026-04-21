"""
Windows platform services for Semantic Wallpaper application.
Handles wallpaper and lockscreen changes using Windows API.
"""

import ctypes
import sys
from pathlib import Path
from typing import Optional, Tuple


class WallpaperService:
    """Service for changing desktop wallpaper on Windows."""

    # Windows SPI constants
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    def __init__(self):
        """Initialize wallpaper service."""
        self._is_windows = sys.platform == "win32"
        if self._is_windows:
            self._user32 = ctypes.windll.user32
        else:
            self._user32 = None

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._is_windows

    def set_wallpaper(self, image_path: str) -> Tuple[bool, str]:
        """
        Set the desktop wallpaper.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (success, message)
        """
        if not self._is_windows:
            return (False, "Wallpaper change is only supported on Windows")

        try:
            # Validate file exists
            path = Path(image_path)
            if not path.exists():
                return (False, f"Image file does not exist: {image_path}")

            # Convert to absolute path
            abs_path = str(path.absolute())

            # Call Windows API
            result = self._user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )

            if result:
                return (True, f"Wallpaper set successfully: {abs_path}")
            else:
                return (False, "Failed to set wallpaper (Windows API returned False)")

        except Exception as e:
            return (False, f"Error setting wallpaper: {str(e)}")

    def get_current_wallpaper(self) -> Optional[str]:
        """
        Get the current wallpaper path.
        
        Returns:
            Path to current wallpaper or None
        """
        if not self._is_windows:
            return None

        try:
            # Read from Windows registry
            import winreg
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop"
            )
            value, _ = winreg.QueryValueEx(key, "WallPaper")
            winreg.CloseKey(key)
            
            return value if value else None
            
        except Exception:
            return None


class LockscreenService:
    """Service for changing Windows lockscreen background."""

    def __init__(self):
        """Initialize lockscreen service."""
        self._is_windows = sys.platform == "win32"

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._is_windows

    def set_lockscreen(self, image_path: str) -> Tuple[bool, str]:
        """
        Set the lockscreen background.
        
        Note: This requires Windows 10/11 and may need elevated permissions.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (success, message)
        """
        if not self._is_windows:
            return (False, "Lockscreen change is only supported on Windows")

        try:
            # Validate file exists
            path = Path(image_path)
            if not path.exists():
                return (False, f"Image file does not exist: {image_path}")

            # For lockscreen, we need to copy the image to a specific location
            # and update registry. This is a simplified implementation.
            
            # Target location for lockscreen images
            local_appdata = Path.home() / "AppData" / "Local"
            lockscreen_dir = local_appdata / "Packages" / \
                "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy" / \
                "LocalState" / "Assets"
            
            # Alternative: Use registry method
            return self._set_lockscreen_via_registry(str(path.absolute()))

        except PermissionError:
            return (False, "Permission denied. Try running as administrator.")
        except Exception as e:
            return (False, f"Error setting lockscreen: {str(e)}")

    def _set_lockscreen_via_registry(self, image_path: str) -> Tuple[bool, str]:
        """
        Set lockscreen via Windows Registry.
        
        Args:
            image_path: Absolute path to the image file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import winreg
            
            # Copy image to a location accessible by lockscreen
            target_path = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "LockScreen.jpg"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(image_path, target_path)
            
            # Update registry
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Lock Screen",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                key,
                "LockScreenImagePath",
                0,
                winreg.REG_SZ,
                str(target_path)
            )
            
            winreg.CloseKey(key)
            
            return (True, f"Lockscreen set successfully: {target_path}")
            
        except PermissionError:
            return (False, "Permission denied. Registry access requires appropriate permissions.")
        except Exception as e:
            return (False, f"Error updating registry: {str(e)}")

    def is_lockscreen_supported(self) -> Tuple[bool, str]:
        """
        Check if lockscreen change is supported on this system.
        
        Returns:
            Tuple of (supported, reason)
        """
        if not self._is_windows:
            return (False, "Not running on Windows")

        # Check Windows version
        try:
            import platform
            version = platform.win32_ver()[0]
            
            if version in ["10", "11"]:
                return (True, "Lockscreen change is supported")
            else:
                return (False, f"Lockscreen change may not be supported on Windows {version}")
                
        except Exception as e:
            return (False, f"Could not determine Windows version: {str(e)}")


def set_wallpaper_and_lockscreen(
    image_path: str,
    change_lockscreen: bool = True
) -> Tuple[bool, str, str]:
    """
    Convenience function to set both wallpaper and lockscreen.
    
    Args:
        image_path: Path to the image file
        change_lockscreen: Whether to also change the lockscreen
        
    Returns:
        Tuple of (overall_success, wallpaper_message, lockscreen_message)
    """
    wallpaper_service = WallpaperService()
    lockscreen_service = LockscreenService()

    # Set wallpaper
    wp_success, wp_message = wallpaper_service.set_wallpaper(image_path)

    # Set lockscreen if requested
    ls_success = False
    ls_message = "Lockscreen change not requested"
    
    if change_lockscreen:
        ls_success, ls_message = lockscreen_service.set_lockscreen(image_path)

    overall_success = wp_success and (ls_success or not change_lockscreen)
    
    return (overall_success, wp_message, ls_message)
