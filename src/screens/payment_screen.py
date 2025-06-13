"""
Payment Screen for the PisoPrint Vendo system.
Handles coin collection and payment processing with payment limit enforcement.
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time
from src.utils.coin_acceptor import CoinAcceptor
from src.utils.logger import logger, log_event, log_payment, log_error
from src.screens.base_screen import BaseScreen

class PaymentScreen(BaseScreen):
    """
    Payment screen that manages coin collection and payment processing.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store original copies and amount
        self.original_copies = app.copies
        self.original_amount = app.calculate_total()
        
        # Check for payment limit
        if self.original_amount > app.max_payment:
            messagebox.showerror(
                "Payment Limit Exceeded",
                f"Total amount (₱{self.original_amount}) exceeds the maximum allowed (₱{app.max_payment}).\n"
                "Please reduce the number of copies."
            )
            app.show_selection_screen()
            return
            
        # Set amount values
        app.total_amount = self.original_amount
        app.inserted_amount = 0
        
        # Payment state flags to prevent multiple triggers
        self.payment_completed = False
        self.processing_payment = False
        
        # Initialize coin acceptor
        self.setup_coin_acceptor()
        
        # Create UI
        self.create_ui()
        
        # Log screen creation
        log_event("PAYMENT", f"Payment screen initialized. Amount: ₱{self.original_amount}, Copies: {self.original_copies}")
        
        # Register payment to database for tracking
        self.payment_id = None

    def create_ui(self):
        """Create the payment screen user interface"""
        # Header with blue background
        header = tk.Frame(self.app.current_frame, bg="#248CCF", height=80)
        header.pack(fill="x")
        tk.Label(header, text="PLEASE INSERT COIN TO PAY", 
                font=("Inter", 24, "bold"),
                bg="#248CCF", fg="white").pack(pady=20)

        # Main content frame
        content_frame = tk.Frame(self.app.current_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Payment information displays
        self.setup_displays(content_frame)

        # Payment limit warning
        limit_frame = tk.Frame(content_frame, bg="#FFEB3B")
        limit_frame.pack(fill="x", pady=10)
        tk.Label(limit_frame, 
                text=f"Maximum Payment Limit: ₱{self.app.max_payment}", 
                font=("Inter", 14, "bold"),
                bg="#FFEB3B", fg="#333").pack(pady=5)

        # Cancel button
        cancel_frame = tk.Frame(content_frame, bg="white")
        cancel_frame.pack(side="bottom", pady=20)
        
        self.create_button(cancel_frame, 
                 text="CANCEL PAYMENT", 
                 font=("Inter", 16),
                 bg="#FF6B6B", 
                 fg="white", 
                 width=20, 
                 height=2,
                 command=self.cancel_payment).pack()

    def setup_displays(self, parent):
        """
        Create payment information displays.
        
        Args:
            parent (tk.Frame): Parent frame for the displays
        """
        display_frame = tk.Frame(parent, bg="white")
        display_frame.pack(pady=20)

        # Number of copies display
        copies_frame = tk.Frame(display_frame, bg="white")
        copies_frame.pack(fill="x", pady=10)
        tk.Label(copies_frame, 
                text="COPIES:", 
                font=("Inter", 20, "bold"),
                bg="white").pack(side="left", padx=10)
        tk.Label(copies_frame, 
                text=str(self.original_copies), 
                font=("Inter", 20),
                bg="white").pack(side="left")

        # Total Payment Display
        payment_frame = tk.Frame(display_frame, bg="white")
        payment_frame.pack(fill="x", pady=10)
        tk.Label(payment_frame, 
                text="TOTAL PAYMENT:", 
                font=("Inter", 20, "bold"),
                bg="white").pack(side="left", padx=10)
        tk.Label(payment_frame, 
                text=f"₱{self.original_amount}", 
                font=("Inter", 20),
                bg="white").pack(side="left")

        # Amount Inserted Display
        inserted_frame = tk.Frame(display_frame, bg="white")
        inserted_frame.pack(fill="x", pady=10)
        tk.Label(inserted_frame, 
                text="COIN INSERTED:", 
                font=("Inter", 20, "bold"),
                bg="white").pack(side="left", padx=10)
        self.inserted_var = tk.StringVar(value="₱0")
        tk.Label(inserted_frame, 
                textvariable=self.inserted_var, 
                font=("Inter", 20),
                bg="white").pack(side="left")
                
        # Remaining amount display
        remaining_frame = tk.Frame(display_frame, bg="white")
        remaining_frame.pack(fill="x", pady=10)
        tk.Label(remaining_frame, 
                text="REMAINING:", 
                font=("Inter", 20, "bold"),
                bg="white").pack(side="left", padx=10)
        self.remaining_var = tk.StringVar(value=f"₱{self.original_amount}")
        tk.Label(remaining_frame, 
                textvariable=self.remaining_var, 
                font=("Inter", 20),
                bg="white").pack(side="left")

    def coin_detected(self, value):
        """
        Handle detected coin with payment completion lock.
        
        Args:
            value (int): Value of the detected coin in pesos
        """
        # Prevent multiple rapid triggers
        if self.payment_completed or self.processing_payment:
            logger.info("Ignoring coin - payment already processing")
            return
            
        logger.info(f"Coin detected: ₱{value}")
        
        # Update the inserted amount
        self.app.inserted_amount += value
        self.inserted_var.set(f"₱{self.app.inserted_amount}")
        
        # Update remaining amount
        remaining = max(0, self.original_amount - self.app.inserted_amount)
        self.remaining_var.set(f"₱{remaining}")
        
        # Log the payment
        log_payment(value)
        
        # Add payment to database
        self.app.db_manager.log_payment(value, self.payment_id)
        
        # Check if payment is complete
        if self.app.inserted_amount >= self.original_amount:
            self.processing_payment = True  # Lock to prevent multiple triggers
            self.payment_completed = True   # Mark payment as completed
            
            # Show payment completed message
            self.show_payment_completed()
            
            # Ensure original copy count is preserved
            self.app.copies = self.original_copies
            log_event("PAYMENT", f"Payment complete. Amount: ₱{self.app.inserted_amount}, Copies: {self.app.copies}")
            
            # Use a short delay to prevent multiple triggers
            self.app.root.after(2000, self.proceed_to_printing)
            
    def show_payment_completed(self):
        """Show payment completed message"""
        # Create a payment successful overlay
        self.success_frame = tk.Frame(self.app.current_frame, bg="white")
        self.success_frame.place(relx=0.5, rely=0.5, anchor="center", 
                               width=400, height=200)
        
        # Add a border
        self.success_frame.config(highlightbackground="#4CAF50", 
                                highlightthickness=3)
        
        # Success message
        tk.Label(self.success_frame, text="PAYMENT SUCCESSFUL!", 
                font=("Inter", 20, "bold"), bg="white").pack(pady=(30, 15))
        
        tk.Label(self.success_frame, text="Proceeding to printing...", 
                font=("Inter", 16), bg="white").pack(pady=10)
        
        # Create a progress indicator
        self.progress_var = tk.IntVar(value=0)
        self.progress = tk.Scale(self.success_frame, from_=0, to=100, 
                               orient=tk.HORIZONTAL, length=300,
                               variable=self.progress_var, 
                               showvalue=False, bg="white",
                               highlightthickness=0)
        self.progress.pack(pady=10)
        
        # Start progress animation
        self.animate_progress()
        
    def animate_progress(self, current=0):
        """Animate the progress bar"""
        if current <= 100:
            self.progress_var.set(current)
            self.app.root.after(20, lambda: self.animate_progress(current + 2))

    def proceed_to_printing(self):
        """Proceed to printing screen after delay"""
        # Double-check that copies is still correct
        self.app.copies = self.original_copies
        log_event("NAVIGATION", f"Proceeding to printing with {self.app.copies} copies")
        
        # Clean up coin acceptor before changing screens
        self.cleanup()
        
        # Show printing screen
        self.app.show_printing_screen()

    def setup_coin_acceptor(self):
        """Initialize and connect to the coin acceptor"""
        try:
            # Check if Arduino interface exists and is connected
            if hasattr(self.app, 'arduino') and self.app.arduino:
                # Set callback for coin detection
                self.app.arduino.set_coin_callback(self.coin_detected)
                log_event("PAYMENT", "Coin acceptor ready via Arduino")
            else:
                # Legacy coin acceptor method or fallback
                if not hasattr(self.app, 'coin_acceptor') or not self.app.coin_acceptor:
                    from src.utils.coin_acceptor import CoinAcceptor
                    self.app.coin_acceptor = CoinAcceptor()
                    
                if not self.app.coin_acceptor.connect():
                    log_error("PAYMENT", "Failed to connect to coin acceptor")
                    self.enable_test_buttons()
                else:
                    self.app.coin_acceptor.set_callback(self.coin_detected)
                    log_event("PAYMENT", "Legacy coin acceptor connected")
                    
        except Exception as e:
            log_error("PAYMENT", f"Error setting up coin acceptor: {e}")
            self.enable_test_buttons()
            
    def enable_test_buttons(self):
        """Enable test buttons for simulating coin insertion"""
        test_frame = tk.Frame(self.app.current_frame, bg="white")
        test_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Label(test_frame, text="TEST MODE - SIMULATE COINS:", 
                font=("Inter", 14, "bold"), bg="white").pack(pady=5)
        
        button_frame = tk.Frame(test_frame, bg="white")
        button_frame.pack()
        
        # Create buttons for each coin value
        for value in [1, 5, 10, 20]:
            self.create_button(button_frame, text=f"₱{value}", 
                     command=lambda v=value: self.coin_detected(v),
                     font=("Inter", 12), bg="#FFEB3B",
                     width=8, height=2).pack(side="left", padx=10)

    def cancel_payment(self):
        """Handle payment cancellation"""
        self.payment_completed = True  # Prevent any further coin processing
        
        if self.app.inserted_amount > 0:
            log_event("PAYMENT", f"Payment cancelled. Amount inserted: ₱{self.app.inserted_amount}")
            messagebox.showinfo("Payment Cancelled", 
                              f"Payment cancelled. You inserted ₱{self.app.inserted_amount}.\n"
                              "Sorry but you can't retrieve your coins.")
        else:
            log_event("PAYMENT", "Payment cancelled. No coins inserted.")
            
        self.cleanup()
        self.app.show_main_screen()

    def cleanup(self):
        """Clean up resources when leaving the screen"""
        # Don't disconnect the coin acceptor here, just remove the callback
        # This allows the coin acceptor to be reused in future payment screens
        if hasattr(self.app, 'coin_acceptor') and self.app.coin_acceptor:
            self.app.coin_acceptor.set_callback(None)
            
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()