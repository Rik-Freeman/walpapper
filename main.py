#!/usr/bin/env python3
"""
Semantic Wallpaper - Main Entry Point

Launches the GUI application for managing desktop wallpapers.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui.app import run_app


def main():
    """Main entry point for the application."""
    try:
        run_app()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
