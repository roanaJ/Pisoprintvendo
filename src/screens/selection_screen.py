"""
Selection Screen for PisoPrint Vendo.
Handles copy count selection and enforces maximum payment limit.
"""
import tkinter as tk
from tkinter import messagebox
from src.screens.base_screen import BaseScreen

class SelectionScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        app.copies = 0  # Reset copies
        
        # Reload pricing settings
        self.price_per_page = app.price_color if app.is_colored else app.price_bw
        self.max_payment = app.max_payment
        self.max_copies = self.calculate_max_copies()

        # Header with blue background (minimized)
        header = tk.Frame(app.current_frame, bg="#248CCF", height=40)
        header.pack(fill="x")
        tk.Label(header, text="SELECT COPIES", font=("Inter", 18, "bold"),
                bg="#248CCF", fg="white").pack(pady=5)

        # Main content frame
        content_frame = tk.Frame(app.current_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=10, pady=(5, 0))

        # Left side - Displays (larger text)
        left_frame = tk.Frame(content_frame, bg="white")
        left_frame.pack(side="left", expand=True, fill="x", padx=10)

        # Total Copies (increased font size)
        tk.Label(left_frame, text="TOTAL COPIES:", font=("Inter", 20, "bold"),
                bg="white").pack(anchor="w", pady=(0, 2))
        self.copies_var = tk.StringVar(value="0")
        copies_entry = tk.Entry(left_frame, textvariable=self.copies_var,
                              font=("Inter", 24, "bold"), width=15, state='readonly',
                              bg="#D9D9D9", justify='center')
        copies_entry.pack(pady=(0, 10))

        # Total Payment (increased font size)
        tk.Label(left_frame, text="TOTAL PAYMENT:", font=("Inter", 20, "bold"),
                bg="white").pack(anchor="w", pady=(0, 2))
        self.price_var = tk.StringVar(value="₱0")
        price_entry = tk.Entry(left_frame, textvariable=self.price_var,
                             font=("Inter", 24, "bold"), width=15, state='readonly',
                             bg="#D9D9D9", justify='center')
        price_entry.pack(pady=(0, 10))
        
        # Maximum payment limit information
        payment_limit_frame = tk.Frame(left_frame, bg="#FFF3CD")
        payment_limit_frame.pack(fill="x", pady=10)
        
        tk.Label(payment_limit_frame, 
                text=f"Maximum Payment: ₱{self.max_payment}", 
                font=("Inter", 12, "bold"),
                bg="#FFF3CD", fg="#856404").pack(pady=5)
        
        tk.Label(payment_limit_frame, 
                text=f"Maximum Copies: {self.max_copies}", 
                font=("Inter", 12),
                bg="#FFF3CD", fg="#856404").pack(pady=5)
        
        # Current price information
        price_info_frame = tk.Frame(left_frame, bg="white")
        price_info_frame.pack(fill="x", pady=10)
        
        price_type = "COLOR" if self.app.is_colored else "B&W"
        tk.Label(price_info_frame, 
                text=f"Price per page ({price_type}): ₱{self.price_per_page}", 
                font=("Inter", 12),
                bg="white").pack(anchor="w")
        
        tk.Label(price_info_frame, 
                text=f"Total pages: {self.app.total_pages}", 
                font=("Inter", 12),
                bg="white").pack(anchor="w")

        # Right side - Numpad (centered and expanded)
        numpad_frame = tk.Frame(content_frame, bg="white")
        numpad_frame.pack(side="right", expand=True, fill="both", padx=10)
        self.create_numpad(numpad_frame)

        # Bottom navigation frame
        nav_frame = tk.Frame(app.current_frame, bg="white")
        nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        # Navigation buttons (full width)
        back_btn = self.create_button(nav_frame, text="BACK", font=("Inter", 12),
                 bg="#90EE90", height=2,
                 command=app.show_preview_screen)
        back_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        proceed_btn = self.create_button(nav_frame, text="PROCEED PAYMENT", font=("Inter", 12),
                 bg="#7FFFD4", height=2,
                 command=self.proceed_to_payment)
        proceed_btn.pack(side="right", expand=True, fill="x", padx=5)

    def calculate_max_copies(self):
        """Calculate maximum allowed copies based on payment limit"""
        pages = self.app.total_pages
        price = self.price_per_page
        
        if pages <= 0 or price <= 0:
            return 99  # Default limit
            
        # Formula: max_payment / (pages * price_per_page)
        max_copies = int(self.max_payment / (pages * price))
        
        # Ensure at least 1 copy is always allowed
        return max(1, max_copies)

    def create_numpad(self, parent):
        """
        Create numpad for copy selection.
        
        Args:
            parent (tk.Frame): Parent frame for the numpad
        """
        # Use grid with equal weight to make buttons fill the space
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        # Numbers 1-9
        for i in range(9):
            row = i // 3
            col = i % 3
            btn = self.create_button(parent, text=str(i + 1), font=("Inter", 16),
                          command=lambda x=i+1: self.update_copies(x),
                          bg="#FFEB3B")
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        # 0 and clear buttons
        zero_btn = self.create_button(parent, text="0", font=("Inter", 16),
                 command=lambda: self.update_copies(0),
                 bg="#FFEB3B")
        zero_btn.grid(row=3, column=1, sticky="nsew", padx=2, pady=2)
        
        clear_btn = self.create_button(parent, text="C", font=("Inter", 16),
                 command=lambda: self.update_copies(-1),
                 bg="#FF69B4")
        clear_btn.grid(row=3, column=2, sticky="nsew", padx=2, pady=2)

    def update_copies(self, num):
        """
        Update the copies count.
        
        Args:
            num (int): Number to add or -1 to clear
        """
        current = int(self.copies_var.get())
        
        if num == -1:  # Clear
            current = 0
        else:
            current = current * 10 + num
            
        # Check if exceeding max copies
        if current > self.max_copies:
            messagebox.showwarning(
                "Maximum Exceeded",
                f"Maximum allowed copies is {self.max_copies} due to payment limit of ₱{self.max_payment}."
            )
            return
            
        self.copies_var.set(str(current))
        self.app.copies = current
        self.price_var.set(f"₱{self.app.calculate_total()}")

    def proceed_to_payment(self):
        """Proceed to payment screen with validation"""
        if self.app.copies <= 0:
            messagebox.showwarning("Warning", "Please select number of copies")
            return
            
        # Check if total exceeds maximum payment limit
        total_amount = self.app.calculate_total()
        if total_amount > self.max_payment:
            messagebox.showerror(
                "Payment Limit Exceeded",
                f"Total amount (₱{total_amount}) exceeds the maximum allowed (₱{self.max_payment}).\n"
                "Please reduce the number of copies."
            )
            return
            
        self.app.show_payment_screen()