"""
Main Screen for the PisoPrint Vendo system.
Provides the entry point for the application with main navigation options.
"""
import tkinter as tk
from PIL import Image, ImageTk
from src.screens.base_screen import BaseScreen

class MainScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        """
        Initialize the main screen.
        
        Args:
            app (PisoPrintSystem): Main application instance
        """
        self.app = app
        
        # Header Frame with blue background
        header = tk.Frame(app.current_frame, bg="#248CCF", height=120)
        header.pack(fill="x")
        
        # Logo and Title container
        title_container = tk.Frame(header, bg="#248CCF")
        title_container.pack(pady=10)
        
        # Load and resize CTU logo
        try:
            logo = Image.open("assets/image_ctu.png")
            logo = logo.resize((60, 60), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(title_container, image=logo_photo, bg="#248CCF")
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # IM 311 text
        tk.Label(title_container, text="IM 311", font=("Inter", 24, "bold"), 
                bg="#248CCF", fg="white").pack(side="left", padx=10)
        
        # PISOPRINT VENDO text
        tk.Label(title_container, text="PISOPRINT VENDO", font=("Inter", 32, "bold"), 
                bg="#248CCF", fg="white").pack(side="left", padx=20)

        # Reset variables
        app.current_pdf = None
        app.pdf_document = None
        app.total_pages = 0
        app.copies = 0
        app.total_amount = 0
        app.inserted_amount = 0

        # Button container
        btn_frame = tk.Frame(app.current_frame, bg="white")
        btn_frame.pack(expand=True, pady=50)
        
        # Guide and Info Button
        self.create_button(
            btn_frame,
            text="GUIDE AND\nINFO",
            font=("Inter", 16),
            bg="#90EE90",  # Light green
            width=15, height=6,
            command=self.show_guide
        ).pack(side="left", padx=20)
        
        # Send PDF Button
        self.create_button(
            btn_frame,
            text="SEND PDF\nVIA BT",
            font=("Inter", 16),
            bg="#7FFFD4",  # Turquoise
            width=15, height=6,
            command=app.show_receive_screen
        ).pack(side="left", padx=20)
        
        # Footer with version info and admin hint
        footer = tk.Frame(app.current_frame, bg="white")
        footer.pack(side="bottom", fill="x")
        
        # Version info left
        version_info = tk.Label(
            footer, 
            text="PisoPrint Vendo v1.0", 
            font=("Inter", 8), 
            bg="white", 
            fg="gray"
        )
        version_info.pack(side="left", padx=10, pady=5)
        
        # Count of pages printed
        total_pages = app.db_manager.get_total_pages_printed()
        usage_info = tk.Label(
            footer, 
            text=f"Total Pages: {total_pages}", 
            font=("Inter", 8), 
            bg="white", 
            fg="gray"
        )
        usage_info.pack(side="right", padx=10, pady=5)

    def show_guide(self):
        """Navigate to guide screen"""
        self.app.show_guide_screen()
    
    def create_button(self, parent, **kwargs):
        """Helper method to create a button with common properties"""
        return tk.Button(parent, **kwargs)