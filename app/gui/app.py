"""
Semantic Wallpaper - Main GUI Application Window

Provides the main application window with navigation shell.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.gui.pages import (
    HomePage,
    LibraryPage,
    SourcesPage,
    AutomationPage,
    SettingsPage,
    AboutPage
)
from app.gui.widgets import StatusBanner
from app.gui.state import AppState


class SemanticWallpaperApp(ctk.CTk):
    """Main application window for Semantic Wallpaper."""
    
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("Semantic Wallpaper")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Initialize state
        self.state = AppState()
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create navigation sidebar
        self._create_sidebar()
        
        # Create main content area
        self._create_content_area()
        
        # Create status banner
        self._create_status_banner()
        
        # Load initial data
        self._load_initial_data()
    
    def _create_sidebar(self):
        """Create the left navigation sidebar."""
        sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_rowconfigure(7, weight=1)
        
        # App logo/title
        logo_label = ctk.CTkLabel(
            sidebar,
            text="Semantic\nWallpaper",
            font=("Arial", 18, "bold"),
            justify="center"
        )
        logo_label.grid(row=0, column=0, padx=10, pady=(20, 30))
        
        # Navigation buttons
        nav_buttons = [
            ("Home", self._show_home),
            ("Library", self._show_library),
            ("Sources", self._show_sources),
            ("Automation", self._show_automation),
            ("Settings", self._show_settings),
            ("About", self._show_about)
        ]
        
        self.nav_buttons = {}
        
        for i, (name, command) in enumerate(nav_buttons, start=1):
            btn = ctk.CTkButton(
                sidebar,
                text=name,
                command=command,
                width=160,
                height=45,
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=10, pady=5)
            self.nav_buttons[name.lower()] = btn
        
        # Initially show home button as active
        self._set_active_button("home")
    
    def _create_content_area(self):
        """Create the main content area."""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize pages
        self.pages: Dict[str, Any] = {}
        
        self.pages["home"] = HomePage(
            self.content_frame,
            on_change_now=self._on_change_wallpaper
        )
        self.pages["library"] = LibraryPage(
            self.content_frame,
            on_select=self._on_set_wallpaper,
            on_delete=self._on_delete_wallpaper
        )
        self.pages["sources"] = SourcesPage(
            self.content_frame,
            on_download=self._on_download_wallpapers
        )
        self.pages["automation"] = AutomationPage(
            self.content_frame,
            on_install=self._on_install_task,
            on_remove=self._on_remove_task,
            on_test=self._on_test_automation
        )
        self.pages["settings"] = SettingsPage(
            self.content_frame,
            on_save=self._on_save_settings
        )
        self.pages["about"] = AboutPage(self.content_frame)
        
        # Show home page initially
        self._show_home()
    
    def _create_status_banner(self):
        """Create the bottom status banner."""
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(row=1, column=0, columnspan=2, sticky="ew")
    
    def _load_initial_data(self):
        """Load initial application data."""
        self.state.set_status("Ready")
        self.status_banner.set_status("Ready", "green")
    
    def _set_active_button(self, page_name: str):
        """Set the active navigation button."""
        for name, btn in self.nav_buttons.items():
            if name == page_name.lower():
                btn.configure(fg_color="#3498db")
            else:
                btn.configure(fg_color="transparent", hover_color="#2c3e50")
    
    def _clear_content(self):
        """Clear the content area."""
        for page in self.pages.values():
            page.grid_forget()
    
    def _show_page(self, page_name: str):
        """Show a specific page."""
        self._clear_content()
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        self._set_active_button(page_name)
    
    def _show_home(self):
        """Show the home page."""
        self._show_page("home")
    
    def _show_library(self):
        """Show the library page."""
        self._show_page("library")
    
    def _show_sources(self):
        """Show the sources page."""
        self._show_page("sources")
    
    def _show_automation(self):
        """Show the automation page."""
        self._show_page("automation")
    
    def _show_settings(self):
        """Show the settings page."""
        self._show_page("settings")
    
    def _show_about(self):
        """Show the about page."""
        self._show_page("about")
    
    def _on_change_wallpaper(self):
        """Handle change wallpaper action."""
        self.status_banner.set_status("Changing wallpaper...", "blue")
    
    def _on_set_wallpaper(self, item: dict):
        """Handle set wallpaper from library."""
        self.status_banner.set_status(f"Setting: {item.get('name', 'Unknown')}", "blue")
    
    def _on_delete_wallpaper(self, item: dict):
        """Handle delete wallpaper action."""
        pass
    
    def _on_download_wallpapers(self, categories: list, amount: int, min_resolution: str):
        """Handle download wallpapers action."""
        self.status_banner.set_status("Downloading wallpapers...", "blue")
    
    def _on_install_task(self, interval: str):
        """Handle install scheduled task."""
        self.status_banner.set_status(f"Installing task ({interval})...", "blue")
    
    def _on_remove_task(self):
        """Handle remove scheduled task."""
        self.status_banner.set_status("Removing task...", "blue")
    
    def _on_test_automation(self):
        """Handle test automation action."""
        self.status_banner.set_status("Testing automation...", "blue")
    
    def _on_save_settings(self):
        """Handle save settings action."""
        self.status_banner.set_status("Settings saved", "green")


def run_app():
    """Run the application."""
    app = SemanticWallpaperApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
