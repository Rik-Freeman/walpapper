#!/usr/bin/env python3
"""
Semantic Wallpaper - Main GUI Entry Point

Launches the CustomTkinter desktop application for managing wallpapers.
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Initialize and run the GUI application."""
    try:
        import customtkinter as ctk
    except ImportError:
        print("Error: customtkinter is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)

    # Configure customtkinter settings
    ctk.set_appearance_mode("dark")  # Options: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

    # Import GUI app after dependency check
    from app.gui.app import SemanticWallpaperApp

    # Create and run application
    app = SemanticWallpaperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
