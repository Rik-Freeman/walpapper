"""Confirm dialog widget for user confirmations."""

import customtkinter as ctk


class ConfirmDialog(ctk.CTkToplevel):
    """A confirmation dialog for user actions."""
    
    def __init__(self, master, title: str, message: str, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Center the dialog
        self.transient(master)
        self.grab_set()
        
        # Message label
        self.message_label = ctk.CTkLabel(
            self, 
            text=message, 
            font=("Arial", 12),
            wraplength=350
        )
        self.message_label.pack(padx=20, pady=20)
        
        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(0, 20))
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=100
        )
        self.cancel_button.grid(row=0, column=0, padx=10)
        
        # Confirm button
        self.confirm_button = ctk.CTkButton(
            button_frame,
            text="Confirm",
            command=self._on_confirm,
            width=100,
            fg_color="#e74c3c"
        )
        self.confirm_button.grid(row=0, column=1, padx=10)
        
        self.result = None
    
    def _on_confirm(self):
        """Handle confirm action."""
        self.result = True
        self.destroy()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.result = False
        self.destroy()
    
    def get_result(self) -> bool:
        """Get the dialog result."""
        return self.result
