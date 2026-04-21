"""Sources page for managing wallpaper download sources."""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any


class SourcesPage(ctk.CTkFrame):
    """Sources page for configuring and downloading wallpapers from sources."""
    
    def __init__(self, master, 
                 on_download: Optional[Callable] = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_download = on_download
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Download Sources", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # Sources frame
        sources_frame = ctk.CTkFrame(self)
        sources_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        sources_frame.grid_columnconfigure(0, weight=1)
        
        # Picsum Photos source
        picsum_frame = ctk.CTkFrame(sources_frame, fg_color="transparent")
        picsum_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        picsum_frame.grid_columnconfigure(1, weight=1)
        
        self.picsum_var = ctk.BooleanVar(value=True)
        picsum_check = ctk.CTkCheckBox(
            picsum_frame,
            text="Picsum Photos",
            variable=self.picsum_var,
            width=150
        )
        picsum_check.grid(row=0, column=0, padx=10)
        
        picsum_desc = ctk.CTkLabel(
            picsum_frame,
            text="Random high-quality photos from Lorem Ipsum",
            font=("Arial", 10),
            anchor="w"
        )
        picsum_desc.grid(row=1, column=0, padx=10, sticky="w")
        
        # Akspic.ru source
        akspic_frame = ctk.CTkFrame(sources_frame, fg_color="transparent")
        akspic_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        akspic_frame.grid_columnconfigure(1, weight=1)
        
        self.akspic_var = ctk.BooleanVar(value=True)
        akspic_check = ctk.CTkCheckBox(
            akspic_frame,
            text="Akspic.ru",
            variable=self.akspic_var,
            width=150
        )
        akspic_check.grid(row=0, column=0, padx=10)
        
        akspic_desc = ctk.CTkLabel(
            akspic_frame,
            text="Russian wallpaper collection with categories",
            font=("Arial", 10),
            anchor="w"
        )
        akspic_desc.grid(row=1, column=0, padx=10, sticky="w")
        
        # Categories frame
        cat_frame = ctk.CTkFrame(self)
        cat_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        cat_frame.grid_columnconfigure(0, weight=1)
        cat_frame.grid_rowconfigure(1, weight=1)
        
        cat_label = ctk.CTkLabel(
            cat_frame,
            text="Categories (comma-separated)",
            font=("Arial", 14, "bold")
        )
        cat_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.categories_entry = ctk.CTkEntry(
            cat_frame,
            placeholder_text="nature, space, abstract, city",
            width=400
        )
        self.categories_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Download settings
        settings_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        settings_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # Amount to download
        amount_label = ctk.CTkLabel(
            settings_frame,
            text="Number to download:",
            font=("Arial", 11)
        )
        amount_label.grid(row=0, column=0, padx=5)
        
        self.amount_var = ctk.StringVar(value="5")
        self.amount_entry = ctk.CTkEntry(
            settings_frame,
            textvariable=self.amount_var,
            width=60
        )
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        # Minimum resolution
        res_label = ctk.CTkLabel(
            settings_frame,
            text="Min resolution:",
            font=("Arial", 11)
        )
        res_label.grid(row=0, column=2, padx=(15, 5))
        
        self.res_var = ctk.StringVar(value="1920x1080")
        self.res_entry = ctk.CTkEntry(
            settings_frame,
            textvariable=self.res_var,
            width=100
        )
        self.res_entry.grid(row=0, column=3, padx=5)
        
        # Download button
        self.download_button = ctk.CTkButton(
            cat_frame,
            text="Download Now",
            command=self._on_download,
            width=200,
            height=40
        )
        self.download_button.grid(row=3, column=0, pady=20)
        
        # Progress and results
        self.progress_label = ctk.CTkLabel(
            cat_frame,
            text="",
            font=("Arial", 11)
        )
        self.progress_label.grid(row=4, column=0, pady=(0, 10))
        
        self.result_label = ctk.CTkLabel(
            cat_frame,
            text="",
            font=("Arial", 10),
            anchor="w"
        )
        self.result_label.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")
    
    def _on_download(self):
        """Handle download action."""
        if self.on_download:
            categories = self.categories_entry.get().split(',')
            try:
                amount = int(self.amount_var.get())
            except ValueError:
                amount = 5
            
            self.on_download(
                categories=[c.strip() for c in categories if c.strip()],
                amount=amount,
                min_resolution=self.res_var.get()
            )
    
    def set_progress(self, message: str):
        """Set progress message."""
        self.progress_label.configure(text=message)
    
    def set_result(self, message: str):
        """Set result message."""
        self.result_label.configure(text=message)
    
    def get_enabled_sources(self) -> List[str]:
        """Get list of enabled sources."""
        sources = []
        if self.picsum_var.get():
            sources.append('picsum')
        if self.akspic_var.get():
            sources.append('akspic')
        return sources
