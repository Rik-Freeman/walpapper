"""Toast message widget for displaying temporary notifications."""

import customtkinter as ctk


class ToastMessage(ctk.CTkToplevel):
    """A toast notification widget for temporary messages."""
    
    def __init__(self, master, message: str, duration: int = 3000, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title("Notification")
        self.geometry("+%d+%d" % (master.winfo_rootx() + 50, master.winfo_rooty() + 50))
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Message label
        self.message_label = ctk.CTkLabel(
            self, 
            text=message, 
            font=("Arial", 12),
            wraplength=300
        )
        self.message_label.pack(padx=20, pady=20)
        
        # Auto-close after duration
        if duration > 0:
            self.after(duration, self.destroy)
    
    def destroy(self):
        """Override destroy to handle cleanup."""
        try:
            super().destroy()
        except:
            pass
