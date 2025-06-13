"""
PisoPrint Vendo System Integration Module.
This module orchestrates the integration of all system components.
"""

import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from threading import Thread

# Ensure correct path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class PisoPrintSystem:
    """
    PisoPrint Vendo System Integration.
    
    This class serves as the main integration point for all system components.
    """
    
    def __init__(self, root=None, debug_mode=False):
        """
        Initialize the PisoPrint Vendo system.
        
        Args:
            root (tk.Tk, optional): Root Tkinter window
            debug_mode (bool, optional): Enable debug features
        """
        # Set debug mode
        self.debug_mode = debug_mode
        
        # Initialize database first
        from src.utils.sqlite_manager import SQLiteManager
        self.db_manager = SQLiteManager()
        
        # Load system settings
        self.load_settings()
        
        # Setup GUI
        self.setup_gui(root)
        
        # Initialize hardware interfaces
        self.initialize_hardware()
        
        # Initialize web monitor
        self.initialize_web_monitor()
        
        # Log system startup
        self.log_system_event("STARTUP", "System initialized")
        
        # Initialize maintenance monitor
        self.initialize_maintenance_monitor()
    
    def load_settings(self):
        """Load all settings from the database"""
        # Pricing and payment settings
        self.price_bw = float(self.db_manager.get_setting('price_bw_page', 3))
        self.price_color = float(self.db_manager.get_setting('price_color_page', 5))
        self.max_payment = float(self.db_manager.get_setting('max_payment_amount', 100))
        
        # System settings
        self.system_name = self.db_manager.get_setting('system_name', 'PisoPrint Vendo')
        self.printer_name = self.db_manager.get_setting('printer_name', '')
        
        # Paper inventory settings
        self.paper_capacity = int(self.db_manager.get_setting('paper_capacity', 500))
        self.paper_level = int(self.db_manager.get_setting('paper_level', 500))
        
        # Other state variables
        self.current_pdf = None
        self.pdf_document = None
        self.total_pages = 0
        self.current_page = 0
        self.copies = 1
        self.is_colored = False
        self.total_amount = 0
        self.inserted_amount = 0
        self.admin_pattern_buffer = []
    
    def setup_gui(self, provided_root=None):
        """
        Set up the GUI components.
    
        Args:
            provided_root (tk.Tk, optional): Root Tkinter window
        """
        if provided_root:
            self.root = provided_root
        else:
         self.root = tk.Tk()
        
        # Configure window properties
        self.root.title(self.system_name)
    
        # Set fullscreen mode unless in debug mode
        if not self.debug_mode:
            # Use either fullscreen OR overrideredirect, not both
            if getattr(self, 'kiosk_mode', True):
                # Kiosk mode: use overrideredirect
                self.root.overrideredirect(True)
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            else:
                # Regular fullscreen mode
                self.root.attributes('-fullscreen', True)
        else:
            # Windowed mode for development
            self.root.geometry("1024x768")
        
        # Configure base window
        self.root.configure(bg="white")
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
    
        # Initialize UI frame
        self.current_frame = None
    
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
        # Initialize screens dictionary for lazy loading
        self.screens = {}
    
        # Show the main screen
        self.show_main_screen()
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for navigation and debugging"""
        # Emergency exit in debug mode
        if self.debug_mode:
            self.root.bind('<Control-q>', lambda e: self.shutdown())
            self.root.bind('<Escape>', lambda e: self.shutdown())
            self.root.bind('<F12>', lambda e: self.toggle_fullscreen())
            
        # Admin pattern key sequence
        # Allow Ctrl+A to show admin pattern screen (only in debug mode)
        if self.debug_mode:
            self.root.bind('<Control-a>', lambda e: self.show_admin_pattern_screen())
    
    def initialize_hardware(self):
        """Initialize hardware components"""
        # Import hardware modules
        from src.utils.pdf_printer import PDFPrinter
        from src.utils.arduino_interface import ArduinoInterface
        from src.utils.buzzer_interface import BuzzerInterface
        
        # Initialize printer
        self.printer = PDFPrinter(self.printer_name)
        
        # Initialize Arduino interface
        arduino_port = self.db_manager.get_setting('arduino_port', 'COM4')
        self.arduino = ArduinoInterface(arduino_port)
        if self.arduino.connect():
            # Initialize buzzer
            self.buzzer = BuzzerInterface(self.arduino)
            # Set up admin button callback
            self.arduino.set_admin_callback(self.show_admin_pattern_screen)
            # Coin callback will be set in the payment screen
        else:
            self.log_system_event("ERROR", "Failed to connect to Arduino")
            self.arduino = None
            self.buzzer = None
    
    def initialize_web_monitor(self):
        """Initialize the web monitoring server"""
        try:
            from src.monitor.app import app as monitor_app
            
            # Start Flask in a separate thread
            def run_flask():
                monitor_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            
            # Create and start the thread
            self.monitor_thread = Thread(target=run_flask, daemon=True)
            self.monitor_thread.start()
            
            # Add monitor status to GUI
            self.add_monitor_status()
            
            self.log_system_event("STARTUP", "Web monitoring server started on port 5000")
        except Exception as e:
            self.log_system_event("ERROR", f"Failed to start web monitor: {str(e)}")

    def add_monitor_status(self):
        """Add monitor status indicator to the GUI"""
        if hasattr(self, 'current_frame') and self.current_frame:
            status_frame = tk.Frame(self.current_frame, bg="white")
            status_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
            
            status_label = tk.Label(status_frame, 
                                  text="Monitoring: Online ✓", 
                                  fg="green",
                                  bg="white",
                                  font=("Arial", 10))
            status_label.pack()
    
    def initialize_maintenance_monitor(self):
        """Initialize the maintenance monitoring system"""
        # Check paper level
        if self.paper_level < 0.2 * self.paper_capacity:
            self.log_system_event("WARNING", f"Paper level is low: {self.paper_level}/{self.paper_capacity}")
        
        # Schedule a periodic check
        self.root.after(3600000, self.maintenance_check)  # Check every hour
    
    def maintenance_check(self):
        """Perform periodic maintenance checks"""
        # Check paper level
        if self.paper_level < 0.2 * self.paper_capacity:
            self.log_system_event("WARNING", f"Paper level is low: {self.paper_level}/{self.paper_capacity}")
        
        # Check last maintenance date
        last_maintenance = self.db_manager.get_setting('last_maintenance', '')
        try:
            last_date = datetime.fromisoformat(last_maintenance)
            days_since = (datetime.now() - last_date).days
            
            if days_since > 30:
                self.log_system_event("WARNING", f"System maintenance overdue by {days_since} days")
        except ValueError:
            pass
        
        # Reschedule next check
        self.root.after(3600000, self.maintenance_check)
    
    def log_system_event(self, event_type, details):
        """
        Log a system event.
        
        Args:
            event_type (str): Type of event
            details (str): Event details
        """
        print(f"[{event_type}] {details}")
        
        # Log to database
        if event_type == "WARNING" or event_type == "ERROR":


            
            self.db_manager.log_admin_access(f"System {event_type}", details)
    
    def clear_screen(self):
        """Clear the current screen and prepare for a new one"""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg="white")
        self.current_frame.place(x=0, y=0, 
                              width=self.screen_width, 
                              height=self.screen_height)
        
        self.log_system_event("NAVIGATION", "Screen cleared")
    
    def show_main_screen(self):
        """Show the main screen"""
        self.reset_state()
        self.clear_screen()
        
        # Import and initialize main screen
        from src.screens.main_screen import MainScreen
        MainScreen(self)
        
        self.log_system_event("NAVIGATION", "Main screen displayed")
    
    def show_guide_screen(self):
        """Show the guide screen"""
        self.clear_screen()
        
        # Import and initialize guide screen
        from src.screens.guide_screen import GuideScreen
        GuideScreen(self)
        
        self.log_system_event("NAVIGATION", "Guide screen displayed")
    
    def show_receive_screen(self):
        """Show the receive screen"""
        self.clear_screen()
        
        # Import and initialize receive screen
        from src.screens.receive_screen import ReceiveScreen
        ReceiveScreen(self)
        
        self.log_system_event("NAVIGATION", "Receive screen displayed")
    
    def show_preview_screen(self):
        """Show the preview screen"""
        self.clear_screen()
        
        # Import and initialize preview screen
        from src.screens.preview_screen import PreviewScreen
        PreviewScreen(self)
        
        self.log_system_event("NAVIGATION", "Preview screen displayed")
    
    def show_selection_screen(self):
        """Show the selection screen"""
        self.clear_screen()
        
        # Import and initialize selection screen
        from src.screens.selection_screen import SelectionScreen
        SelectionScreen(self)
        
        self.log_system_event("NAVIGATION", "Selection screen displayed")
    
    def show_payment_screen(self):
        """Show the payment screen"""
        # Calculate total amount
        self.total_amount = self.calculate_total()
        
        # Enforce payment limit
        if self.total_amount > self.max_payment:
            from tkinter import messagebox
            messagebox.showerror(
                "Payment Limit Exceeded",
                f"Total amount (₱{self.total_amount}) exceeds the maximum allowed (₱{self.max_payment}).\n"
                "Please reduce the number of copies."
            )
            self.log_system_event("PAYMENT", f"Payment rejected - exceeds maximum: ₱{self.total_amount}")
            return
        
        self.inserted_amount = 0
        self.clear_screen()
        
        # Import and initialize payment screen
        from src.screens.payment_screen import PaymentScreen
        PaymentScreen(self)
        
        self.log_system_event("NAVIGATION", "Payment screen displayed")
    
    def show_printing_screen(self):
        """Show the printing screen"""
        # Store original copies
        original_copies = self.copies
        self.clear_screen()
        
        # Restore original copies
        self.copies = original_copies
        
        # Import and initialize printing screen
        from src.screens.printing_screen import PrintingScreen
        PrintingScreen(self)
        
        self.log_system_event("NAVIGATION", "Printing screen displayed")
    
    def show_admin_pattern_screen(self):
        """Show the admin pattern entry screen"""
        self.clear_screen()
        
        # Import and initialize admin pattern screen
        from src.screens.admin_screen import AdminPatternScreen
        AdminPatternScreen(self)
        
        self.log_system_event("NAVIGATION", "Admin pattern screen displayed")
    
    def show_admin_screen(self):
        """Show the admin panel screen"""
        self.clear_screen()
        
        # Import and initialize admin screen
        from src.screens.admin_screen import AdminScreen
        AdminScreen(self)
        
        self.log_system_event("NAVIGATION", "Admin panel displayed")
    
    def reset_state(self):
        """Reset the application state to default values"""
        # Document state
        self.current_pdf = None
        self.pdf_document = None
        self.total_pages = 0
        self.current_page = 0
        
        # Print job state
        self.copies = 1
        self.is_colored = False
        
        # Payment state
        self.total_amount = 0
        self.inserted_amount = 0
        
        # Admin pattern buffer
        self.admin_pattern_buffer = []
        
        self.log_system_event("APP_STATE", "System state reset")
    
    def calculate_total(self):
        """
        Calculate total payment amount based on copies and pages.
        
        Returns:
            float: Total amount in pesos
        """
        # Reload pricing settings
        self.price_bw = float(self.db_manager.get_setting('price_bw_page', 3))
        self.price_color = float(self.db_manager.get_setting('price_color_page', 5))
        
        price_per_page = self.price_color if self.is_colored else self.price_bw
        total = self.copies * self.total_pages * price_per_page
        
        self.log_system_event("PAYMENT", f"Calculated total: ₱{total} for {self.copies} copies")
        return total
    
    def print_document(self):
        """
        Print the document with current settings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_pdf:
                raise ValueError("No PDF file selected")
                
            self.log_system_event("PRINT", f"Printing {self.copies} copies of {self.current_pdf}")
            
            # Check printer status
            printer_status = self.printer.check_printer_status()
            if printer_status.get("status") == "error" or not printer_status.get("ready", False):
                error_details = ", ".join([k for k, v in printer_status.get("details", {}).items() if v])
                error_msg = f"Printer not ready: {error_details}" if error_details else "Printer not ready"
                raise ValueError(error_msg)
            
            # Check paper level
            pages_needed = self.copies * self.total_pages
            if pages_needed > self.paper_level:
                raise ValueError(f"Not enough paper. Need {pages_needed} pages, but only {self.paper_level} available.")
            
            # Print the document
            success = self.printer.print_pdf(self.current_pdf, self.copies)
            
            if success:
                # Log successful print job
                job_id = self.db_manager.log_print_job(
                    os.path.basename(self.current_pdf),
                    self.total_pages,
                    self.copies,
                    self.is_colored,
                    self.total_amount,
                    True
                )
                
                # Update paper level
                self.paper_level -= pages_needed
                self.db_manager.set_setting('paper_level', self.paper_level)
                
                self.log_system_event("PRINT", f"Print job completed successfully. Job ID: {job_id}")
                return True
            else:
                raise ValueError("Print job failed")
                
        except Exception as e:
            error_msg = str(e)
            self.log_system_event("ERROR", f"Printing error: {error_msg}")
            
            # Log failed print job
            if self.current_pdf:
                self.db_manager.log_print_job(
                    os.path.basename(self.current_pdf),
                    self.total_pages,
                    self.copies,
                    self.is_colored,
                    self.total_amount,
                    False
                )
            
            return False
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        self.root.overrideredirect(not is_fullscreen)
    
    def shutdown(self):
        """Shutdown the system"""
        # Perform cleanup
        self.cleanup()
        
        # Log shutdown
        self.log_system_event("SHUTDOWN", "System shutting down")
        
        # Exit
        self.root.destroy()
    
    def cleanup(self):
        """Clean up resources before shutdown"""
        # Close PDF document if open
        if hasattr(self, 'pdf_document') and self.pdf_document:
            try:
                self.pdf_document.close()
            except:
                pass
        
        # Disconnect coin acceptor if connected
        if hasattr(self, 'coin_acceptor') and self.coin_acceptor:
            try:
                self.coin_acceptor.disconnect()
            except:
                pass
        
        # Shutdown web monitor if running
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            from src.monitor.app import shutdown_server
            shutdown_server()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# Entry point when running as main module
def main():
    """Main entry point for the application"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PisoPrint Vendo System")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--windowed', action='store_true', help='Run in windowed mode')
    args = parser.parse_args()
    
    # Create and run application
    app = PisoPrintSystem(debug_mode=args.debug)
    
    # Apply windowed mode if requested
    if args.windowed:
        app.root.attributes('-fullscreen', False)
        app.root.overrideredirect(False)
        app.root.geometry("1024x768")
    
    # Run the application
    app.run()


if __name__ == "__main__":
    main()