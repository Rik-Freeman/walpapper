"""Status banner widget for displaying application status."""

import customtkinter as ctk


class StatusBanner(ctk.CTkFrame):
    """A banner widget to display application status messages."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Status icon
        self.icon_label = ctk.CTkLabel(self, text="●", font=("Arial", 16))
        self.icon_label.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Status message
        self.message_label = ctk.CTkLabel(
            self, 
            text="Ready", 
            font=("Arial", 12),
            anchor="w"
        )
        self.message_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        self.set_status("Ready", "green")
    
    def set_status(self, message: str, color: str = "green"):
        """Set the status message and color.
        
        Args:
            message: The status message to display
            color: Color indicator (green, yellow, red, blue)
        """
        self.message_label.configure(text=message)
        
        color_map = {
            "green": "#2ecc71",
            "yellow": "#f1c40f",
            "red": "#e74c3c",
            "blue": "#3498db",
            "gray": "#95a5a6"
        }
        
        self.icon_label.configure(text_color=color_map.get(color, "#95a5a6"))
