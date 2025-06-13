import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
from src.screens.base_screen import BaseScreen

class ReceiveScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        
        # Header with blue background
        header = tk.Frame(app.current_frame, bg="#248CCF", height=80)
        header.pack(fill="x")
        
        tk.Label(header, 
                text="SEND YOUR PDF TO THIS BLUETOOTH NAME:", 
                font=("Inter", 20),
                bg="#248CCF", fg="white").pack(pady=5)
        
        tk.Label(header, 
                text="ORANGEPIZERO3", 
                font=("Inter", 24, "bold"),
                bg="#248CCF", fg="white").pack(pady=5)

        # Content area
        content_frame = tk.Frame(app.current_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Accept Device Button
        self.create_button(content_frame,
                 text="PLEASE SELECT\nYOUR PDF FILE",
                 font=("Inter", 16),
                 bg="#7FFFD4",  # Turquoise
                 width=20, height=4,
                 command=self.select_file).pack(pady=20)
        
        # Back Button
        self.create_button(content_frame,
                 text="BACK",
                 font=("Inter", 16),
                 bg="#90EE90",  # Light green
                 width=20, height=4,
                 command=app.show_main_screen).pack(pady=20)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.app.current_pdf = file_path
            try:
                self.app.pdf_document = fitz.open(file_path)
                self.app.total_pages = len(self.app.pdf_document)
                self.app.show_preview_screen()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF file: {str(e)}")