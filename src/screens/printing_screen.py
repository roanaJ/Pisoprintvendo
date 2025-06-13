import tkinter as tk
from tkinter import messagebox
from src.screens.base_screen import BaseScreen

class PrintingScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        # Store original copy count and prevent changes
        self._copies = app.copies
        print(f"Starting print job with {self._copies} copies")  # Debug print
        
        # Header with blue background
        header = tk.Frame(app.current_frame, bg="#248CCF", height=55)
        header.pack(fill="x")
        tk.Label(header, text="YOUR DOCUMENT IS NOW PRINTING", 
                font=("Inter", 24, "bold"), bg="#248CCF", 
                fg="white").pack(pady=10)
        
        # Main content frame
        content_frame = tk.Frame(app.current_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Progress message
        self.message_label = tk.Label(content_frame, 
                                    text="Printing in progress...", 
                                    font=("Inter", 24, "bold"), 
                                    bg="white")
        self.message_label.pack(expand=True)
        
        # Start single print job after a short delay
        app.root.after(100, self.single_print_job)

    def single_print_job(self):
        """Execute exactly one print job"""
        try:
            # Force the correct number of copies
            self.app.copies = self._copies
            print(f"Executing single print job with {self._copies} copies")  # Debug print
            
            # Attempt to print once
            success = self.app.print_document()
            
            if success:
                self.show_success_message()
            else:
                self.show_error_message()
        
        except Exception as e:
            self.show_error_message(str(e))

    def show_success_message(self):
        """Show success message and return button"""
        self.message_label.config(text="Printing is now started!\nPlease collect your document.")
        self.show_return_button()

    def show_error_message(self, error_msg="Printing failed"):
        """Show error message and return button"""
        self.message_label.config(text=f"Printing Error:\n{error_msg}")
        self.show_return_button()

    def show_return_button(self):
        """Show return to main menu button"""
        nav_frame = tk.Frame(self.app.current_frame, bg="white")
        nav_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        self.create_button(nav_frame, 
                 text="BACK TO HOME", 
                 font=("Inter", 16),
                 bg="#90EE90",
                 width=20, height=2,
                 command=self.app.show_main_screen).pack(expand=True)