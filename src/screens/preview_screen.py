import tkinter as tk
from PIL import Image, ImageTk
import fitz
from src.screens.base_screen import BaseScreen

class PreviewScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        
        # Header with blue background (smaller)
        header = tk.Frame(app.current_frame, bg="#248CCF", height=40)
        header.pack(fill="x")
        tk.Label(header, text="PDF PREVIEW", font=("Inter", 18, "bold"),
                bg="#248CCF", fg="white").pack(pady=5)

        # Main buttons at bottom
        btn_frame = tk.Frame(app.current_frame, bg="white")
        btn_frame.pack(side="bottom", fill="x")
        
        self.create_button(btn_frame, text="BACK", font=("Inter", 16),
                 bg="#90EE90", height=2,
                 command=app.show_receive_screen).pack(side="left", expand=True, fill="x")
        
        self.create_button(btn_frame, text="SELECT COPIES", font=("Inter", 16),
                 bg="#7FFFD4", height=2,
                 command=app.show_selection_screen).pack(side="left", expand=True, fill="x")

        # Container for preview and page navigation
        container = tk.Frame(app.current_frame, bg="white")
        container.pack(expand=True, fill="both")

        # PDF Preview area with scrollbar if needed
        preview_frame = tk.Frame(container, bg="#D9D9D9")
        preview_frame.pack(expand=True, fill="both")

        if app.pdf_document:
            self.show_preview(preview_frame)

        # Page navigation if multiple pages
        if self.app.total_pages > 1:
            nav_frame = tk.Frame(container, bg="#D9D9D9")
            nav_frame.pack(fill="x")
            
            # Previous button
            self.create_button(nav_frame, text="PREVIOUS", font=("Inter", 14, "bold"),
                     bg="#FFEB3B", height=2,
                     command=lambda: self.change_page(-1)).pack(side="left", expand=True, fill="x")
            
            # Page counter (increased size and padding)
            tk.Label(nav_frame, text=f"Page {self.app.current_page + 1}/{self.app.total_pages}",
                    bg="#D9D9D9", font=("Inter", 16, "bold")).pack(side="left", padx=30)
            
            # Next button
            self.create_button(nav_frame, text="NEXT", font=("Inter", 14, "bold"),
                     bg="#FFEB3B", height=2,
                     command=lambda: self.change_page(1)).pack(side="right", expand=True, fill="x")

    def show_preview(self, preview_frame):
        # Get the current page
        page = self.app.pdf_document[self.app.current_page]
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Calculate aspect ratio
        aspect_ratio = img.width / img.height
        
        # Set maximum dimensions while maintaining aspect ratio
        max_width = 700
        max_height = 320
        
        # Calculate new dimensions
        if aspect_ratio > 1:  # Wider than tall
            new_width = min(max_width, img.width)
            new_height = int(new_width / aspect_ratio)
        else:  # Taller than wide
            new_height = min(max_height, img.height)
            new_width = int(new_height * aspect_ratio)
        
        # Resize image while maintaining aspect ratio
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Display image
        label = tk.Label(preview_frame, image=photo, bg="#D9D9D9")
        label.image = photo
        label.pack(expand=True, pady=5)

    def change_page(self, delta):
        self.app.current_page = (self.app.current_page + delta) % self.app.total_pages
        self.app.show_preview_screen()