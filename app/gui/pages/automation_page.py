"""Automation page for configuring scheduled tasks."""

import customtkinter as ctk
from typing import Callable, Optional


class AutomationPage(ctk.CTkFrame):
    """Automation page for configuring Windows Task Scheduler integration."""
    
    def __init__(self, master,
                 on_install: Optional[Callable] = None,
                 on_remove: Optional[Callable] = None,
                 on_test: Optional[Callable] = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_install = on_install
        self.on_remove = on_remove
        self.on_test = on_test
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Automation", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        # Status frame
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Scheduled Tasks Status:",
            font=("Arial", 13, "bold")
        )
        status_label.grid(row=0, column=0, padx=10, pady=15)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="Not Installed",
            font=("Arial", 12),
            text_color="#e74c3c"
        )
        self.status_indicator.grid(row=0, column=1, padx=10, pady=15, sticky="w")
        
        # Configuration frame
        config_frame = ctk.CTkFrame(self)
        config_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Enable automation checkbox
        self.enabled_var = ctk.BooleanVar(value=False)
        self.enabled_check = ctk.CTkCheckBox(
            config_frame,
            text="Enable Automatic Wallpaper Changes",
            variable=self.enabled_var,
            font=("Arial", 13, "bold")
        )
        self.enabled_check.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Interval mode
        interval_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        interval_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        interval_label = ctk.CTkLabel(
            interval_frame,
            text="Change interval:",
            font=("Arial", 11)
        )
        interval_label.grid(row=0, column=0, padx=5)
        
        self.interval_var = ctk.StringVar(value="logon")
        self.interval_menu = ctk.CTkOptionMenu(
            interval_frame,
            variable=self.interval_var,
            values=["logon", "startup", "hourly", "daily", "weekly"],
            width=150
        )
        self.interval_menu.grid(row=0, column=1, padx=5)
        
        interval_help = ctk.CTkLabel(
            interval_frame,
            text="(logon=on user login, startup=on boot)",
            font=("Arial", 9),
            text_color="gray"
        )
        interval_help.grid(row=0, column=2, padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=30)
        
        # Install task button
        self.install_button = ctk.CTkButton(
            button_frame,
            text="Install Scheduled Task",
            command=self._on_install,
            width=200,
            height=40
        )
        self.install_button.grid(row=0, column=0, padx=10)
        
        # Remove task button
        self.remove_button = ctk.CTkButton(
            button_frame,
            text="Remove Scheduled Task",
            command=self._on_remove,
            width=200,
            height=40,
            fg_color="#e74c3c"
        )
        self.remove_button.grid(row=0, column=1, padx=10)
        
        # Test button
        self.test_button = ctk.CTkButton(
            button_frame,
            text="Test Automation",
            command=self._on_test,
            width=200,
            height=40,
            variant="secondary"
        )
        self.test_button.grid(row=1, column=0, columnspan=2, padx=10, pady=(15, 0))
        
        # Info label
        info_label = ctk.CTkLabel(
            config_frame,
            text="Note: Administrative privileges may be required\n"
                 "to install or remove scheduled tasks.",
            font=("Arial", 9),
            text_color="gray",
            justify="center"
        )
        info_label.grid(row=3, column=0, pady=20)
        
        # Result message
        self.result_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=("Arial", 10)
        )
        self.result_label.grid(row=4, column=0, pady=(0, 10))
    
    def _on_install(self):
        """Handle install action."""
        if self.on_install:
            self.on_install(interval=self.interval_var.get())
    
    def _on_remove(self):
        """Handle remove action."""
        if self.on_remove:
            self.on_remove()
    
    def _on_test(self):
        """Handle test action."""
        if self.on_test:
            self.on_test()
    
    def set_status(self, installed: bool, message: str = ""):
        """Update the status display."""
        if installed:
            self.status_indicator.configure(
                text=f"Installed ({message})" if message else "Installed",
                text_color="#2ecc71"
            )
        else:
            self.status_indicator.configure(
                text=message or "Not Installed",
                text_color="#e74c3c"
            )
    
    def set_result(self, message: str):
        """Set result message."""
        self.result_label.configure(text=message)
    
    def is_enabled(self) -> bool:
        """Check if automation is enabled."""
        return self.enabled_var.get()
    
    def get_interval(self) -> str:
        """Get selected interval."""
        return self.interval_var.get()
