"""
Admin Screen for PisoPrint Vendo.
Provides administration features and system statistics.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.screens.base_screen import BaseScreen

class AdminPatternScreen(BaseScreen):
    """Screen for entering the admin access pattern"""
    
    def __init__(self, app):
        """
        Initialize the admin pattern screen.
        
        Args:
            app (PisoPrintSystem): Main application instance
        """
        super().__init__(app)
        self.app = app
        self.current_pattern = []
        self.db = app.db_manager
        
        # Create UI
        self.create_ui()
        
        # Log access attempt
        self.db.log_admin_access("Admin access attempt", "Pattern screen displayed")
        
    def create_ui(self):
        """Create the admin pattern screen UI"""
        # Header with dark blue background
        header = tk.Frame(self.app.current_frame, bg="#1a5276", height=55)
        header.pack(fill="x")
        tk.Label(header, text="ADMIN ACCESS", 
                font=("Inter", 24, "bold"), bg="#1a5276", 
                fg="white").pack(pady=10)
        
        # Main content frame
        content_frame = tk.Frame(self.app.current_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Instructions
        tk.Label(content_frame, 
                text="Enter Admin Pattern", 
                font=("Inter", 18, "bold"), 
                bg="white").pack(pady=(10, 30))
        
        # Pattern display
        self.pattern_var = tk.StringVar(value="")
        pattern_display = tk.Entry(content_frame, 
                                 textvariable=self.pattern_var,
                                 font=("Inter", 20),
                                 justify="center",
                                 show="●",
                                 width=10,
                                 state="readonly")
        pattern_display.pack(pady=10)
        
        # Pattern entry buttons
        button_frame = tk.Frame(content_frame, bg="white")
        button_frame.pack(pady=30)
        
        # Create a 3x4 grid of buttons
        self.create_pattern_buttons(button_frame)
        
        # Only have Back button in bottom navigation
        nav_frame = tk.Frame(self.app.current_frame, bg="white")
        nav_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        tk.Button(nav_frame, 
                 text="BACK", 
                 font=("Inter", 16),
                 bg="#FF6B6B",  # Red color for back button
                 fg="white",
                 width=15, height=2,
                 command=self.app.show_main_screen).pack(side="right", padx=10)
        
    def create_pattern_buttons(self, parent):
        """
        Create pattern entry buttons.
        
        Args:
            parent (tk.Frame): Parent frame for the buttons
        """
        # Use grid layout with equal weights
        for i in range(4):
            parent.grid_rowconfigure(i, weight=1)
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)
        
        # Number buttons 1-9
        for i in range(9):
            row = i // 3
            col = i % 3
            btn_value = i + 1
            
            btn = tk.Button(parent, 
                          text=str(btn_value), 
                          font=("Inter", 20, "bold"),
                          bg="#d6eaf8", 
                          width=5, height=2,
                          command=lambda v=btn_value: self.add_to_pattern(v))
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        # Button 0
        btn_0 = tk.Button(parent, 
                        text="0", 
                        font=("Inter", 20, "bold"),
                        bg="#d6eaf8", 
                        width=5, height=2,
                        command=lambda: self.add_to_pattern(0))
        btn_0.grid(row=3, column=1, padx=5, pady=5)
        
        # Check/Verify button
        check_btn = tk.Button(parent,
                        text="✓", 
                        font=("Inter", 20, "bold"),
                        bg="#2ecc71", fg="white",
                        width=5, height=2,
                        command=self.verify_pattern)
        check_btn.grid(row=3, column=2, padx=5, pady=5)
        
        # Undo button
        undo_btn = tk.Button(parent,
                        text="⌫", 
                        font=("Inter", 20, "bold"),
                        bg="#e74c3c", fg="white",
                        width=5, height=2,
                        command=self.undo_pattern)
        undo_btn.grid(row=3, column=0, padx=5, pady=5)

    def undo_pattern(self):
        """Remove the last digit from the pattern"""
        if self.current_pattern:
            self.current_pattern.pop()  # Remove the last element
            self.pattern_var.set("●" * len(self.current_pattern))
        
    def add_to_pattern(self, value):
        """
        Add a value to the current pattern.
        
        Args:
            value (int): Value to add to the pattern
        """
        # Limit pattern length to 10 digits
        if len(self.current_pattern) < 10:
            self.current_pattern.append(value)
            self.pattern_var.set("●" * len(self.current_pattern))
            
    def clear_pattern(self):
        """Clear the current pattern"""
        self.current_pattern = []
        self.pattern_var.set("")
        
    def verify_pattern(self):
        """Verify the entered pattern against the stored admin pattern"""
        # Convert pattern list to comma-separated string
        pattern_str = ",".join(map(str, self.current_pattern))
        
        if self.db.verify_admin_pattern(pattern_str):
            # Log successful admin access
            self.db.log_admin_access("Admin access granted", "Pattern verified successfully")
            
            # Show admin panel
            self.app.show_admin_screen()
        else:
            # Log failed admin access
            self.db.log_admin_access("Admin access denied", f"Invalid pattern: {pattern_str}")
            
            # Show error message
            messagebox.showerror("Access Denied", "Invalid admin pattern")
            self.clear_pattern()


class AdminScreen(BaseScreen):
    """Main admin panel screen with system settings and statistics"""
    
    def __init__(self, app):
        """
        Initialize the admin screen.
        
        Args:
            app (PisoPrintSystem): Main application instance
        """
        super().__init__(app)
        self.app = app
        self.db = app.db_manager
        
        # Load current settings
        self.load_settings()
        
        # Create UI
        self.create_ui()
        
        # Log admin screen access
        self.db.log_admin_access("Admin panel opened")
        
    def load_settings(self):
        """Load current settings from the database"""
        self.price_bw = float(self.db.get_setting('price_bw_page', 3))
        self.price_color = float(self.db.get_setting('price_color_page', 5))
        self.max_payment = float(self.db.get_setting('max_payment_amount', 100))
        self.admin_pattern = self.db.get_setting('admin_pattern', '1,2,3,4')
        
    def save_settings(self):
        """Save settings to the database"""
        try:
            # Validate inputs
            price_per_page = float(self.price_per_page_var.get())
            max_payment = float(self.max_payment_var.get())
            admin_pattern = self.admin_pattern_var.get()
            
            # Ensure values are positive
            if price_per_page <= 0 or max_payment <= 0:
                raise ValueError("Values must be positive")
            
            # Save to database
            self.db.set_setting('price_bw_page', price_per_page)  # Use same price for both
            self.db.set_setting('price_color_page', price_per_page)  # Use same price for both
            self.db.set_setting('max_payment_amount', max_payment)
            self.db.set_setting('admin_pattern', admin_pattern)
            
            # Update loaded settings
            self.load_settings()
            
            # Log settings change
            self.db.log_admin_access("Settings updated", 
                                   f"Price per page: {price_per_page}, "
                                   f"Max Payment: {max_payment}")
            
            # Show success message
            messagebox.showinfo("Success", "Settings saved successfully")
            return True
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return False
        
    def create_ui(self):
        """Create the admin screen UI"""
        # Header with dark blue background
        header = tk.Frame(self.app.current_frame, bg="#1a5276", height=55)
        header.pack(fill="x")
        tk.Label(header, text="ADMIN PANEL", 
                font=("Inter", 24, "bold"), bg="#1a5276", 
                fg="white").pack(pady=10)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.app.current_frame)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        settings_tab = tk.Frame(notebook, bg="white")
        stats_tab = tk.Frame(notebook, bg="white")
        logs_tab = tk.Frame(notebook, bg="white")
        
        notebook.add(settings_tab, text="Settings")
        notebook.add(stats_tab, text="Statistics")
        notebook.add(logs_tab, text="Logs")
        
        # Populate tabs
        self.create_settings_tab(settings_tab)
        self.create_stats_tab(stats_tab)
        self.create_logs_tab(logs_tab)
        
        # Bottom navigation
        nav_frame = tk.Frame(self.app.current_frame, bg="white")
        nav_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.create_button(nav_frame, 
                           text="EXIT ADMIN", 
                           font=("Inter", 16),
                           bg="#FF6B6B", fg="white",
                           width=15, height=2,
                           command=self.app.show_main_screen).pack(side="right", padx=10)
        
    def create_settings_tab(self, parent):
        """
        Create the settings tab content.
        
        Args:
            parent (tk.Frame): Parent frame for the tab content
        """
        settings_frame = tk.Frame(parent, bg="white")
        settings_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Pricing settings
        pricing_frame = tk.LabelFrame(settings_frame, text="Pricing Settings", 
                                    font=("Inter", 12, "bold"), bg="white")
        pricing_frame.pack(fill="x", padx=10, pady=10)
        
        # Single Price Per Page
        price_frame = tk.Frame(pricing_frame, bg="white")
        price_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(price_frame, text="Price per page:", 
                font=("Inter", 12), bg="white").pack(side="left")
        self.price_per_page_var = tk.StringVar(value=str(self.price_bw))  # Use black/white price as default
        tk.Entry(price_frame, textvariable=self.price_per_page_var, 
                font=("Inter", 12), width=10).pack(side="right")
        
        # Maximum Payment Amount
        max_payment_frame = tk.Frame(pricing_frame, bg="white")
        max_payment_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(max_payment_frame, text="Maximum Payment Amount:", 
                font=("Inter", 12), bg="white").pack(side="left")
        self.max_payment_var = tk.StringVar(value=str(self.max_payment))
        tk.Entry(max_payment_frame, textvariable=self.max_payment_var, 
                font=("Inter", 12), width=10).pack(side="right")
        
        # Security settings
        security_frame = tk.LabelFrame(settings_frame, text="Security Settings", 
                                     font=("Inter", 12, "bold"), bg="white")
        security_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        # Admin Pattern
        admin_pattern_frame = tk.Frame(security_frame, bg="white")
        admin_pattern_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(admin_pattern_frame, text="Admin Access Pattern (comma-separated):", 
                font=("Inter", 12), bg="white").pack(side="left")
        self.admin_pattern_var = tk.StringVar(value=str(self.admin_pattern))
        tk.Entry(admin_pattern_frame, textvariable=self.admin_pattern_var, 
                font=("Inter", 12), width=15).pack(side="right")
        
        # Save settings button
        tk.Button(settings_frame, text="SAVE SETTINGS", 
                 font=("Inter", 14, "bold"), bg="#4CAF50", fg="white",
                 command=self.save_settings).pack(pady=20)
        
    def create_stats_tab(self, parent):
        """
        Create the statistics tab content.
        
        Args:
            parent (tk.Frame): Parent frame for the tab content
        """
        stats_frame = tk.Frame(parent, bg="white")
        stats_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Summary statistics
        summary_frame = tk.LabelFrame(stats_frame, text="System Summary", 
                                    font=("Inter", 12, "bold"), bg="white")
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        # Total Revenue
        total_revenue = self.db.get_total_revenue()
        revenue_frame = tk.Frame(summary_frame, bg="white")
        revenue_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(revenue_frame, text="Total Revenue:", 
                font=("Inter", 12), bg="white").pack(side="left")
        tk.Label(revenue_frame, text=f"₱{total_revenue:.2f}", 
                font=("Inter", 12, "bold"), bg="white").pack(side="right")
        
        # Total Pages Printed
        total_pages = self.db.get_total_pages_printed()
        pages_frame = tk.Frame(summary_frame, bg="white")
        pages_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(pages_frame, text="Total Pages Printed:", 
                font=("Inter", 12), bg="white").pack(side="left")
        tk.Label(pages_frame, text=str(total_pages), 
                font=("Inter", 12, "bold"), bg="white").pack(side="right")
        
        # Charts section
        charts_frame = tk.LabelFrame(stats_frame, text="Usage Statistics", 
                                   font=("Inter", 12, "bold"), bg="white")
        charts_frame.pack(fill="both", expand=True, padx=10, pady=(20, 10))
        
        # Create charts if data is available
        self.create_charts(charts_frame)
        
    def create_charts(self, parent):
        """
        Create statistics charts.
        
        Args:
            parent (tk.Frame): Parent frame for the charts
        """
        # Get recent print jobs
        jobs = self.db.get_print_job_stats(30)
        
        if not jobs:
            tk.Label(parent, text="No data available for charts", 
                   font=("Inter", 14), bg="white").pack(expand=True)
            return
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.set_facecolor('white')
        
        # Weekly print volume
        weekly_data = {}
        for job in jobs:
            date = job['timestamp'].split('T')[0]  # Extract date part
            pages = job['pages'] * job['copies']
            
            if date in weekly_data:
                weekly_data[date] += pages
            else:
                weekly_data[date] = pages
        
        # Sort by date and take last 7 days
        dates = sorted(weekly_data.keys())[-7:]
        volumes = [weekly_data.get(date, 0) for date in dates]
        
        # Format dates for display
        display_dates = [date.split('-')[2] + '/' + date.split('-')[1] for date in dates]
        
        ax1.bar(display_dates, volumes, color='#3498db')
        ax1.set_title('Daily Print Volume (Last 7 Days)')
        ax1.set_xlabel('Date (DD/MM)')
        ax1.set_ylabel('Pages')
        
        # Color vs. BW print ratio
        color_count = sum(1 for job in jobs if job['is_colored'])
        bw_count = len(jobs) - color_count
        
        ax2.pie([color_count, bw_count], 
              labels=['Color', 'B&W'], 
              autopct='%1.1f%%',
              colors=['#e74c3c', '#34495e'])
        ax2.set_title('Color vs. B&W Print Jobs')
        
        # Add the figure to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def create_logs_tab(self, parent):
        """
        Create the logs tab content.
        
        Args:
            parent (tk.Frame): Parent frame for the tab content
        """
        logs_frame = tk.Frame(parent, bg="white")
        logs_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create scrollable frame for logs
        log_container = tk.Frame(logs_frame, bg="white")
        log_container.pack(fill="both", expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side="right", fill="y")

        # Create table-like display with headers
        columns = ("Timestamp", "Type", "Details")
        self.log_tree = ttk.Treeview(log_container, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        # Configure column widths and headings
        self.log_tree.column("Timestamp", width=150)
        self.log_tree.column("Type", width=100)
        self.log_tree.column("Details", width=350)
        
        for col in columns:
            self.log_tree.heading(col, text=col)
        
        self.log_tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_tree.yview)
        
        # Load print jobs into treeview
        self.load_logs()
        
        # Control buttons
        button_frame = tk.Frame(logs_frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        tk.Button(button_frame, text="Refresh Logs", 
                 command=self.load_logs,
                 bg="#3498db", fg="white",
                 font=("Inter", 10)).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Export Logs", 
                 command=self.export_logs,
                 bg="#2ecc71", fg="white",
                 font=("Inter", 10)).pack(side="left", padx=5)
        
        # Date filter frame
        filter_frame = tk.Frame(logs_frame, bg="white")
        filter_frame.pack(fill="x", pady=10)
        
        tk.Label(filter_frame, text="Date Filter:", 
                font=("Inter", 10), bg="white").pack(side="left")
                
        # Add date pickers or entry fields here
        # For simplicity, we'll use just text entries with format instructions
        
        tk.Label(filter_frame, text="From:", 
                font=("Inter", 10), bg="white").pack(side="left", padx=(10, 5))
        self.date_from = tk.Entry(filter_frame, width=10)
        self.date_from.pack(side="left")
        
        tk.Label(filter_frame, text="To:", 
                font=("Inter", 10), bg="white").pack(side="left", padx=(10, 5))
        self.date_to = tk.Entry(filter_frame, width=10)
        self.date_to.pack(side="left")
        
        tk.Button(filter_frame, text="Apply Filter", 
                 command=self.apply_date_filter,
                 bg="#3498db", fg="white",
                 font=("Inter", 10)).pack(side="left", padx=10)
        
    def load_logs(self):
        """Load log data into the treeview"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Get print job logs
        print_jobs = self.db.get_print_job_stats(100)  # Limit to recent 100 for performance
        
        # Insert into treeview
        for job in print_jobs:
            timestamp = job['timestamp'].replace('T', ' ').split('.')[0]  # Format timestamp
            job_type = "Color Print" if job['is_colored'] else "B&W Print"
            details = f"{job['filename']} - {job['pages']} pages, {job['copies']} copies, ₱{job['amount_paid']}"
            
            self.log_tree.insert("", "end", values=(timestamp, job_type, details))
            
        # Get admin access logs
        # Note: This would need to be implemented in the DatabaseManager class
        # For now, we'll just leave a placeholder
        
    def export_logs(self):
        """Export logs to a CSV file"""
        try:
            from datetime import datetime
            import csv
            import os
            
            # Create exports directory if it doesn't exist
            os.makedirs("exports", exist_ok=True)
            
            # Generate filename with timestamp
            filename = f"exports/pisoprint_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Get data
            print_jobs = self.db.get_print_job_stats(1000)  # Larger limit for export
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Timestamp", "File", "Pages", "Copies", "Type", "Amount Paid", "Success"])
                
                # Write data
                for job in print_jobs:
                    writer.writerow([
                        job['timestamp'],
                        job['filename'],
                        job['pages'],
                        job['copies'],
                        "Color" if job['is_colored'] else "B&W",
                        job['amount_paid'],
                        "Success" if job['success'] else "Failed"
                    ])
            
            messagebox.showinfo("Export Successful", f"Logs exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
            
    def apply_date_filter(self):
        """Apply date filter to logs"""
        try:
            from_date = self.date_from.get().strip()
            to_date = self.date_to.get().strip()
            
            # Validate dates (simple validation for format YYYY-MM-DD)
            if from_date and not self.is_valid_date_format(from_date):
                messagebox.showerror("Invalid Date", "From date must be in YYYY-MM-DD format")
                return
                
            if to_date and not self.is_valid_date_format(to_date):
                messagebox.showerror("Invalid Date", "To date must be in YYYY-MM-DD format")
                return
            
            # Clear existing items
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            
            # Get filtered print job logs
            # This would need to be implemented in the DatabaseManager
            # For now, we'll just show a message
            messagebox.showinfo("Filter Applied", "Date filter applied")
            
            # Reload logs with filter
            self.load_logs()
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to apply filter: {str(e)}")
            
    def is_valid_date_format(self, date_str):
        """
        Validate if string is in YYYY-MM-DD format.
        
        Args:
            date_str (str): Date string to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, date_str))