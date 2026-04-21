"""About page for application information."""

import customtkinter as ctk
import webbrowser


class AboutPage(ctk.CTkFrame):
    """About page displaying application information."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="About", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # App name and version
        name_frame = ctk.CTkFrame(self)
        name_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        name_frame.grid_columnconfigure(0, weight=1)
        
        app_name = ctk.CTkLabel(
            name_frame,
            text="Semantic Wallpaper",
            font=("Arial", 28, "bold")
        )
        app_name.grid(row=0, column=0, padx=10, pady=(20, 5))
        
        version_label = ctk.CTkLabel(
            name_frame,
            text="Version 0.1.0",
            font=("Arial", 12),
            text_color="gray"
        )
        version_label.grid(row=1, column=0, padx=10, pady=(0, 20))
        
        # Description
        desc_frame = ctk.CTkFrame(self)
        desc_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        desc_frame.grid_columnconfigure(0, weight=1)
        
        desc_label = ctk.CTkLabel(
            desc_frame,
            text="An intelligent wallpaper manager that automatically\n"
                 "changes your desktop background based on time of day,\n"
                 "personal preferences, and semantic categories.\n\n"
                 "Features:\n"
                 "• Automatic wallpaper rotation\n"
                 "• Smart recommendations by time of day\n"
                 "• Download from Picsum Photos and Akspic.ru\n"
                 "• Library management with favorites and blacklist\n"
                 "• Windows Task Scheduler integration\n"
                 "• Lockscreen wallpaper synchronization",
            font=("Arial", 11),
            justify="center"
        )
        desc_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Links frame
        links_frame = ctk.CTkFrame(self)
        links_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        links_frame.grid_columnconfigure(0, weight=1)
        
        links_label = ctk.CTkLabel(
            links_frame,
            text="Links",
            font=("Arial", 14, "bold")
        )
        links_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # GitHub link
        github_button = ctk.CTkButton(
            links_frame,
            text="GitHub Repository",
            command=self._open_github,
            width=200,
            variant="secondary"
        )
        github_button.grid(row=1, column=0, padx=10, pady=5)
        
        # License info
        license_label = ctk.CTkLabel(
            links_frame,
            text="License: MIT",
            font=("Arial", 10),
            text_color="gray"
        )
        license_label.grid(row=2, column=0, padx=10, pady=(5, 15))
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            self,
            text="© 2024 Semantic Wallpaper Project",
            font=("Arial", 9),
            text_color="gray"
        )
        copyright_label.grid(row=4, column=0, pady=(0, 20))
    
    def _open_github(self):
        """Open GitHub repository in browser."""
        webbrowser.open("https://github.com/semantic-wallpaper/semantic-wallpaper")
