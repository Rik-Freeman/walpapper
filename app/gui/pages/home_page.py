"""Home page for Semantic Wallpaper application."""

import customtkinter as ctk
from typing import Callable, Optional


class HomePage(ctk.CTkFrame):
    """Home page displaying current wallpaper and quick actions."""
    
    def __init__(self, master, on_change_now: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_change_now = on_change_now
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Current Wallpaper", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # Current wallpaper info frame
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder for wallpaper preview
        self.preview_label = ctk.CTkLabel(
            info_frame,
            text="No wallpaper selected",
            font=("Arial", 14),
            width=400,
            height=300
        )
        self.preview_label.grid(row=0, column=0, pady=20)
        
        # Wallpaper path label
        self.path_label = ctk.CTkLabel(
            info_frame,
            text="Path: --",
            font=("Arial", 12),
            anchor="w"
        )
        self.path_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Last change time
        self.time_label = ctk.CTkLabel(
            info_frame,
            text="Last changed: --",
            font=("Arial", 11),
            anchor="w"
        )
        self.time_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Action buttons frame
        button_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        
        # Change Now button
        self.change_button = ctk.CTkButton(
            button_frame,
            text="Change Now",
            command=self._on_change_now,
            width=150,
            height=40
        )
        self.change_button.grid(row=0, column=0, padx=10)
        
        # Open File button
        self.open_file_button = ctk.CTkButton(
            button_frame,
            text="Open File",
            command=self._on_open_file,
            width=150,
            height=40,
            variant="secondary"
        )
        self.open_file_button.grid(row=0, column=1, padx=10)
        
        # Open Folder button
        self.open_folder_button = ctk.CTkButton(
            button_frame,
            text="Open Folder",
            command=self._on_open_folder,
            width=150,
            height=40,
            variant="secondary"
        )
        self.open_folder_button.grid(row=1, column=0, padx=10, pady=(10, 0))
        
        # Add to Favorites button
        self.fav_button = ctk.CTkButton(
            button_frame,
            text="Add to Favorites",
            command=self._on_add_favorite,
            width=150,
            height=40,
            variant="secondary"
        )
        self.fav_button.grid(row=1, column=1, padx=10, pady=(10, 0))
        
        # Never Show Again button
        self.blacklist_button = ctk.CTkButton(
            button_frame,
            text="Never Show Again",
            command=self._on_blacklist,
            width=150,
            height=40,
            fg_color="#e74c3c"
        )
        self.blacklist_button.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0))
    
    def _on_change_now(self):
        """Handle change now action."""
        if self.on_change_now:
            self.on_change_now()
    
    def _on_open_file(self):
        """Handle open file action."""
        pass
    
    def _on_open_folder(self):
        """Handle open folder action."""
        pass
    
    def _on_add_favorite(self):
        """Handle add to favorites action."""
        pass
    
    def _on_blacklist(self):
        """Handle blacklist action."""
        pass
    
    def update_wallpaper_info(self, path: str, last_changed: str = "--"):
        """Update wallpaper information display."""
        self.path_label.configure(text=f"Path: {path}")
        self.time_label.configure(text=f"Last changed: {last_changed}")
        
        # Update preview (placeholder for now)
        self.preview_label.configure(text=f"Preview: {path.split('/')[-1]}")
