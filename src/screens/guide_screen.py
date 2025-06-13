import tkinter as tk
import sys
import os

# Ensure the src directory is in the Python path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now import configuration
from config import (
    FONT_FAMILY, 
    DEFAULT_BG_COLOR, 
    HEADER_BG_COLOR, 
    BUTTON_COLORS
)

# Import BaseScreen
from src.screens.base_screen import BaseScreen

class GuideScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        """
        Initialize the Guide Screen with layout and styling
        
        Args:
            app: The main application instance
        """
        try:
            print("GuideScreen: Starting initialization")
            
            # Validate application frame
            if not hasattr(app, 'current_frame') or not app.current_frame:
                raise ValueError("Invalid application frame")
            
            self.app = app
            self.root = app.current_frame
            
            # Explicit configuration
            self.BACKGROUND_COLOR = DEFAULT_BG_COLOR
            self.HEADER_COLOR = HEADER_BG_COLOR
            self.BUTTON_COLOR = BUTTON_COLORS.get('main', '#90EE90')
            self.FONT = FONT_FAMILY
            
            # Ensure frame is configured and visible
            self.root.configure(bg=self.BACKGROUND_COLOR)
            
            # Debug: Print frame information
            print(f"Frame geometry: {self.root.winfo_width()}x{self.root.winfo_height()}")
            print(f"Frame bg color: {self.root.cget('bg')}")
            
            # Create the guide screen layout
            print("Creating header")
            self._create_header()
            
            print("Creating scrollable content")
            self._create_scrollable_content()
            
            print("Creating navigation")
            self._create_navigation()
            
            print("GuideScreen: Initialization complete")
        
        except Exception as e:
            print(f"CRITICAL ERROR in GuideScreen initialization: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback error display
            error_label = tk.Label(
                self.root, 
                text=f"Error loading Guide Screen: {e}", 
                bg="red", 
                fg="white",
                font=("Arial", 16)
            )
            error_label.pack(expand=True, fill="both")

    def _create_header(self):
        """Create the blue header for the guide screen"""
        header = tk.Frame(self.root, bg=self.HEADER_COLOR, height=80)
        header.pack(fill="x")
        
        header_label = tk.Label(
            header, 
            text="GUIDE AND INFORMATION", 
            font=(self.FONT, 24, "bold"),
            bg=self.HEADER_COLOR, 
            fg="white"
        )
        header_label.pack(pady=20)

    def _create_scrollable_content(self):
        """Create a scrollable frame for guide content"""
        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.BACKGROUND_COLOR)
        content_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Create canvas with scrollbar
        canvas = tk.Canvas(content_frame, bg=self.BACKGROUND_COLOR)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.BACKGROUND_COLOR)

        # Configure scrollbar and canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate scrollable content
        self._add_guide_sections(scrollable_frame)

    def _add_guide_sections(self, parent):
        """
        Add detailed guide sections with consistent styling
        
        Args:
            parent (tk.Frame): Parent frame to add sections to
        """
        sections = [
            {
                "title": "HOW TO USE",
                "items": [
                    "1. Select 'SEND PDF VIA BT' on the main screen",
                    "2. Choose your PDF file to print",
                    "3. Preview your document and check the pages",
                    "4. Select the number of copies needed",
                    "5. Insert coins according to the total amount",
                    "6. Wait for your document to print",
                    "7. Collect your printouts"
                ]
            },
            {
                "title": "PRICING",
                "items": [
                    "₱3.00 per page",
                ]
            },
            {
                "title": "ACCEPTED COINS",
                "items": [
                    "₱1 coin",
                    "₱5 coin", 
                    "₱10 coin", 
                    "₱20 coin"
                ]
            },
            {
                "title": "IMPORTANT NOTES",
                "items": [
                    "• Maximum file size: 20MB",
                    "• Supported paper size: A4 only",
                    "• The machine provides change if needed",
                    "• In case of problems, press the cancel button",
                    "• Ensure your PDF is ready before starting"
                ]
            },
            {
                "title": "CONTACT SUPPORT",
                "items": [
                    "Need assistance? Contact us:",
                    "Email: jwarenf@gmail.com",
                    "Phone: 09456447156"
                ]
            }
        ]

        for section in sections:
            # Section title
            self._create_section_title(parent, section["title"])
            
            # Section items
            for item in section["items"]:
                self._create_section_item(parent, item)

    def _create_section_title(self, parent, title):
        """
        Create a section title with consistent styling
        
        Args:
            parent (tk.Frame): Parent frame
            title (str): Section title
        """
        title_label = tk.Label(
            parent, 
            text=title, 
            font=(self.FONT, 18, "bold"),
            bg=self.BACKGROUND_COLOR,
            anchor="w"
        )
        title_label.pack(pady=(20, 10), fill="x")

    def _create_section_item(self, parent, text):
        """
        Create a section item with consistent styling
        
        Args:
            parent (tk.Frame): Parent frame
            text (str): Item text
        """
        item_label = tk.Label(
            parent, 
            text=text, 
            font=(self.FONT, 14),
            bg=self.BACKGROUND_COLOR,
            anchor="w",
            wraplength=700  # Add text wrapping
        )
        item_label.pack(pady=5, fill="x")

    def _create_navigation(self):
        """Create navigation buttons at the bottom of the screen"""
        nav_frame = tk.Frame(self.root, bg=self.BACKGROUND_COLOR)
        nav_frame.pack(fill="x", padx=30, pady=20)
        
        back_button = self.create_button(
            nav_frame, 
            text="BACK TO MAIN MENU", 
            font=(self.FONT, 16),
            bg=self.BUTTON_COLOR,
            width=20, 
            height=2,
            command=self.app.show_main_screen
        )
        back_button.pack(expand=True)

# Debug print to confirm module import
print("GuideScreen module imported successfully")