"""
Semantic Wallpaper - Main GUI Application Window

Provides the main application window with navigation shell.
"""

import customtkinter as ctk
from typing import Optional


class SemanticWallpaperApp(ctk.CTk):
    """Main application window for Semantic Wallpaper."""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Semantic Wallpaper")
        self.geometry("1024x768")
        self.minsize(800, 600)

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create navigation frame (left sidebar)
        self._create_navigation()

        # Create main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Placeholder label for main content
        self.placeholder_label = ctk.CTkLabel(
            self.main_frame,
            text="Welcome to Semantic Wallpaper\n\nApplication is under development.\nSelect a page from the navigation menu.",
            font=ctk.CTkFont(size=18),
        )
        self.placeholder_label.pack(expand=True)

        # Current page reference
        self.current_page: Optional[ctk.CTkFrame] = None

    def _create_navigation(self):
        """Create left navigation sidebar with page buttons."""
        self.nav_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)

        # Configure navigation grid
        self.nav_frame.grid_rowconfigure(0, weight=1)
        self.nav_frame.grid_rowconfigure(7, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.nav_frame,
            text="Semantic\nWallpaper",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=10)

        # Navigation buttons
        self.nav_buttons = {}
        pages = [
            ("Home", 1),
            ("Library", 2),
            ("Sources", 3),
            ("Automation", 4),
            ("Settings", 5),
            ("About", 6),
        ]

        for page_name, row in pages:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=page_name,
                command=lambda name=page_name: self._navigate_to(name),
                anchor="w",
                padx=15,
            )
            btn.grid(row=row, column=0, pady=5, padx=10, sticky="ew")
            self.nav_buttons[page_name] = btn

        # Select Home by default
        self._navigate_to("Home")

    def _navigate_to(self, page_name: str):
        """Navigate to a specific page."""
        # Clear current page content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Update button states
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=("transparent", "transparent"))

        # Show placeholder for now (will be replaced with actual pages)
        label = ctk.CTkLabel(
            self.main_frame,
            text=f"{page_name} Page\n\nContent coming soon...",
            font=ctk.CTkFont(size=20),
        )
        label.pack(expand=True)

        self.current_page = label
