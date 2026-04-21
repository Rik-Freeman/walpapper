"""Loading overlay widget for displaying progress during long operations."""

import customtkinter as ctk


class LoadingOverlay(ctk.CTkFrame):
    """A loading overlay to display during long-running operations."""
    
    def __init__(self, master, message: str = "Loading...", **kwargs):
        super().__init__(master, **kwargs)
        
        # Semi-transparent background
        self.configure(fg_color=("gray85", "gray15"))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Center frame
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, sticky="nsew")
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Loading label
        self.label = ctk.CTkLabel(
            center_frame, 
            text=message, 
            font=("Arial", 14, "bold")
        )
        self.label.grid(row=0, column=0, pady=20)
        
        # Progress bar (indeterminate)
        self.progress = ctk.CTkProgressBar(center_frame, mode="indeterminate")
        self.progress.grid(row=1, column=0, padx=40, pady=(0, 20))
        self.progress.start()
    
    def set_message(self, message: str):
        """Update the loading message."""
        self.label.configure(text=message)
    
    def stop(self):
        """Stop the progress animation."""
        self.progress.stop()
    
    def destroy(self):
        """Override destroy to stop progress."""
        self.stop()
        try:
            super().destroy()
        except:
            pass
