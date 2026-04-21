"""Settings page for application configuration."""

import customtkinter as ctk
from typing import Callable, Optional
import os


class SettingsPage(ctk.CTkFrame):
    """Settings page for configuring application preferences."""
    
    def __init__(self, master,
                 on_save: Optional[Callable] = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_save = on_save
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Settings", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # General settings frame
        general_frame = ctk.CTkFrame(self)
        general_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        general_frame.grid_columnconfigure(0, weight=1)
        
        general_label = ctk.CTkLabel(
            general_frame,
            text="General",
            font=("Arial", 14, "bold")
        )
        general_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Lockscreen change toggle
        self.lockscreen_var = ctk.BooleanVar(value=False)
        self.lockscreen_check = ctk.CTkCheckBox(
            general_frame,
            text="Change lockscreen wallpaper",
            variable=self.lockscreen_var
        )
        self.lockscreen_check.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Notifications toggle
        self.notifications_var = ctk.BooleanVar(value=True)
        self.notifications_check = ctk.CTkCheckBox(
            general_frame,
            text="Show notifications",
            variable=self.notifications_var
        )
        self.notifications_check.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Silent mode toggle
        self.silent_var = ctk.BooleanVar(value=False)
        self.silent_check = ctk.CTkCheckBox(
            general_frame,
            text="Silent mode (no popups)",
            variable=self.silent_var
        )
        self.silent_check.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Library settings frame
        library_frame = ctk.CTkFrame(self)
        library_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        library_frame.grid_columnconfigure(0, weight=1)
        
        library_label = ctk.CTkLabel(
            library_frame,
            text="Library",
            font=("Arial", 14, "bold")
        )
        library_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Library path
        path_frame = ctk.CTkFrame(library_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1)
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="Library folder:",
            font=("Arial", 11)
        )
        path_label.grid(row=0, column=0, padx=5)
        
        self.library_path_var = ctk.StringVar(value="")
        self.library_path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.library_path_var,
            width=400
        )
        self.library_path_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.browse_button = ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._on_browse_library,
            width=80
        )
        self.browse_button.grid(row=0, column=2, padx=5)
        
        # Cache settings
        cache_frame = ctk.CTkFrame(library_frame, fg_color="transparent")
        cache_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        cache_label = ctk.CTkLabel(
            cache_frame,
            text="Cache size limit (MB):",
            font=("Arial", 11)
        )
        cache_label.grid(row=0, column=0, padx=5)
        
        self.cache_size_var = ctk.StringVar(value="500")
        self.cache_size_entry = ctk.CTkEntry(
            cache_frame,
            textvariable=self.cache_size_var,
            width=80
        )
        self.cache_size_entry.grid(row=0, column=1, padx=5)
        
        self.cleanup_button = ctk.CTkButton(
            cache_frame,
            text="Cleanup Cache",
            command=self._on_cleanup_cache,
            width=120
        )
        self.cleanup_button.grid(row=0, column=2, padx=15)
        
        # Appearance frame
        appearance_frame = ctk.CTkFrame(self)
        appearance_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        appearance_frame.grid_columnconfigure(0, weight=1)
        
        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="Appearance",
            font=("Arial", 14, "bold")
        )
        appearance_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Theme selection
        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=("Arial", 11)
        )
        theme_label.grid(row=0, column=0, padx=5)
        
        self.theme_var = ctk.StringVar(value="System")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["System", "Light", "Dark"],
            width=120,
            command=self._on_theme_change
        )
        self.theme_menu.grid(row=0, column=1, padx=5)
        
        # Data paths info
        paths_frame = ctk.CTkFrame(self)
        paths_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        paths_frame.grid_columnconfigure(1, weight=1)
        
        paths_label = ctk.CTkLabel(
            paths_frame,
            text="Data Paths",
            font=("Arial", 14, "bold")
        )
        paths_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.config_path_label = ctk.CTkLabel(
            paths_frame,
            text="Config: --",
            font=("Arial", 9),
            anchor="w"
        )
        self.config_path_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        
        self.cache_path_label = ctk.CTkLabel(
            paths_frame,
            text="Cache: --",
            font=("Arial", 9),
            anchor="w"
        )
        self.cache_path_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")
        
        # Save button
        self.save_button = ctk.CTkButton(
            self,
            text="Save Settings",
            command=self._on_save,
            width=200,
            height=40
        )
        self.save_button.grid(row=5, column=0, pady=20)
        
        # Result message
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 10)
        )
        self.result_label.grid(row=6, column=0, pady=(0, 10))
    
    def _on_browse_library(self):
        """Handle browse library folder action."""
        pass
    
    def _on_cleanup_cache(self):
        """Handle cleanup cache action."""
        pass
    
    def _on_theme_change(self, theme: str):
        """Handle theme change."""
        ctk.set_appearance_mode(theme.lower())
    
    def _on_save(self):
        """Handle save action."""
        if self.on_save:
            self.on_save()
    
    def set_result(self, message: str):
        """Set result message."""
        self.result_label.configure(text=message)
    
    def load_settings(self, settings: dict):
        """Load settings from dictionary."""
        self.lockscreen_var.set(settings.get('lockscreen_enabled', False))
        self.notifications_var.set(settings.get('notifications_enabled', True))
        self.silent_var.set(settings.get('silent_mode', False))
        self.library_path_var.set(settings.get('library_path', ''))
        self.cache_size_var.set(str(settings.get('cache_size_mb', 500)))
        self.theme_var.set(settings.get('theme', 'System'))
        
        # Update paths display
        config_path = settings.get('config_path', '--')
        cache_path = settings.get('cache_path', '--')
        self.config_path_label.configure(text=f"Config: {config_path}")
        self.cache_path_label.configure(text=f"Cache: {cache_path}")
    
    def get_settings(self) -> dict:
        """Get current settings as dictionary."""
        return {
            'lockscreen_enabled': self.lockscreen_var.get(),
            'notifications_enabled': self.notifications_var.get(),
            'silent_mode': self.silent_var.get(),
            'library_path': self.library_path_var.get(),
            'cache_size_mb': int(self.cache_size_var.get()) if self.cache_size_var.get().isdigit() else 500,
            'theme': self.theme_var.get()
        }
