"""Library page for browsing and managing wallpapers."""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any


class LibraryPage(ctk.CTkFrame):
    """Library page for browsing and managing wallpaper collection."""
    
    def __init__(self, master, 
                 on_select: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_select = on_select
        self.on_delete = on_delete
        
        # Configure grid
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Wallpaper Library", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20)
        
        # Left panel - wallpaper list
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Show all checkbox
        self.show_all_var = ctk.BooleanVar(value=True)
        self.show_all_check = ctk.CTkCheckBox(
            filter_frame,
            text="Show All",
            variable=self.show_all_var,
            command=self._on_filter_change
        )
        self.show_all_check.grid(row=0, column=0, padx=5)
        
        # Favorites only checkbox
        self.favorites_only_var = ctk.BooleanVar(value=False)
        self.favorites_only_check = ctk.CTkCheckBox(
            filter_frame,
            text="Favorites Only",
            variable=self.favorites_only_var,
            command=self._on_filter_change
        )
        self.favorites_only_check.grid(row=0, column=1, padx=5)
        
        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(list_frame)
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Wallpaper items storage
        self.wallpaper_items: List[Dict[str, Any]] = []
        self.item_widgets = []
        
        # Right panel - preview and actions
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview placeholder
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Select a wallpaper\n to preview",
            font=("Arial", 14)
        )
        self.preview_label.grid(row=0, column=0, pady=20)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            preview_frame,
            text="--",
            font=("Arial", 11),
            anchor="w"
        )
        self.info_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)
        
        # Set as wallpaper button
        self.set_button = ctk.CTkButton(
            button_frame,
            text="Set as Wallpaper",
            command=self._on_set_wallpaper,
            width=180
        )
        self.set_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Favorite toggle
        self.fav_button = ctk.CTkButton(
            button_frame,
            text="Toggle Favorite",
            command=self._on_toggle_favorite,
            width=180,
            variant="secondary"
        )
        self.fav_button.grid(row=1, column=0, padx=5, pady=5)
        
        # Blacklist toggle
        self.blacklist_button = ctk.CTkButton(
            button_frame,
            text="Toggle Blacklist",
            command=self._on_toggle_blacklist,
            width=180,
            variant="secondary"
        )
        self.blacklist_button.grid(row=2, column=0, padx=5, pady=5)
        
        # Delete button
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            command=self._on_delete,
            width=180,
            fg_color="#e74c3c"
        )
        self.delete_button.grid(row=3, column=0, padx=5, pady=5)
        
        # Selected item
        self.selected_item: Optional[Dict[str, Any]] = None
    
    def _on_filter_change(self):
        """Handle filter change."""
        self.refresh_list()
    
    def _on_set_wallpaper(self):
        """Handle set wallpaper action."""
        if self.selected_item and self.on_select:
            self.on_select(self.selected_item)
    
    def _on_toggle_favorite(self):
        """Handle toggle favorite action."""
        pass
    
    def _on_toggle_blacklist(self):
        """Handle toggle blacklist action."""
        pass
    
    def _on_delete(self):
        """Handle delete action."""
        if self.selected_item and self.on_delete:
            self.on_delete(self.selected_item)
    
    def load_library(self, items: List[Dict[str, Any]]):
        """Load wallpaper library items."""
        self.wallpaper_items = items
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the wallpaper list based on filters."""
        # Clear existing widgets
        for widget in self.item_widgets:
            widget.destroy()
        self.item_widgets = []
        
        # Filter items
        filtered = self.wallpaper_items
        
        if not self.show_all_var.get():
            if self.favorites_only_var.get():
                filtered = [item for item in filtered if item.get('favorite', False)]
            else:
                filtered = [item for item in filtered if not item.get('blacklisted', False)]
        
        # Create list items
        for i, item in enumerate(filtered):
            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            item_frame.grid_columnconfigure(0, weight=1)
            
            name_label = ctk.CTkLabel(
                item_frame,
                text=item.get('name', 'Unknown'),
                font=("Arial", 11),
                anchor="w"
            )
            name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            # Bind click
            item_frame.bind("<Button-1>", lambda e, it=item: self.select_item(it))
            name_label.bind("<Button-1>", lambda e, it=item: self.select_item(it))
            
            self.item_widgets.append(item_frame)
    
    def select_item(self, item: Dict[str, Any]):
        """Select a wallpaper item."""
        self.selected_item = item
        
        # Update preview
        self.preview_label.configure(text=f"Preview:\n{item.get('name', 'Unknown')}")
        self.info_label.configure(
            text=f"Path: {item.get('path', '--')}\n"
                 f"Favorite: {'Yes' if item.get('favorite') else 'No'}\n"
                 f"Blacklisted: {'Yes' if item.get('blacklisted') else 'No'}"
        )
