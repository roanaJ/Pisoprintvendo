"""
Database Manager for PisoPrint Vendo.
Handles database operations for statistics, settings, and admin access.
"""
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Manages database operations for the PisoPrint system"""
    
    def __init__(self, db_path=None):
        """
        Initialize the database manager.
        
        Args:
            db_path (str, optional): Path to the database file. Defaults to 'data/pisoprint.db'.
        """
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'pisoprint.db'
            
        self.db_path = str(db_path)
        self.initialize_db()
        
    def initialize_db(self):
        """Initialize the database with required tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
            ''')
            
            # Create print_jobs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                filename TEXT,
                pages INTEGER,
                copies INTEGER,
                is_colored BOOLEAN,
                amount_paid REAL,
                success BOOLEAN
            )
            ''')
            
            # Create payment_transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                amount REAL,
                print_job_id INTEGER,
                FOREIGN KEY (print_job_id) REFERENCES print_jobs (id)
            )
            ''')
            
            # Create admin_access_log table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                action TEXT,
                details TEXT
            )
            ''')
            
            # Insert default settings if they don't exist
            default_settings = {
                'price_bw_page': 3,
                'price_color_page': 5,
                'max_payment_amount': 100,
                'admin_pattern': '1,2,3,4',  # Default admin access pattern
                'printer_name': '',
                'system_name': 'PisoPrint Vendo',
                'last_maintenance': datetime.now().isoformat()
            }
            
            for key, value in default_settings.items():
                cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ''', (key, str(value), datetime.now().isoformat()))
                
            conn.commit()
    
    def get_setting(self, key, default=None):
        """
        Get a setting value from the database.
        
        Args:
            key (str): Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Value of the setting or default if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                
                if result:
                    # Try to parse as JSON if it looks like a dictionary or list
                    value = result[0]
                    try:
                        if (value.startswith('{') and value.endswith('}')) or \
                           (value.startswith('[') and value.endswith(']')):
                            return json.loads(value)
                        return value
                    except (json.JSONDecodeError, AttributeError):
                        return value
                return default
        except Exception as e:
            print(f"Database error in get_setting: {e}")
            return default
    
    def set_setting(self, key, value):
        """
        Set a setting value in the database.
        
        Args:
            key (str): Setting key
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert non-string values to JSON
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ''', (key, value, datetime.now().isoformat()))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error in set_setting: {e}")
            return False
    
    def log_print_job(self, filename, pages, copies, is_colored, amount_paid, success):
        """
        Log a print job to the database.
        
        Args:
            filename (str): Name of the printed file
            pages (int): Number of pages
            copies (int): Number of copies
            is_colored (bool): Whether it was a color print
            amount_paid (float): Amount paid
            success (bool): Whether the print job was successful
            
        Returns:
            int: ID of the new print job record or None if failed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO print_jobs (
                    timestamp, filename, pages, copies, is_colored, amount_paid, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    filename,
                    pages,
                    copies,
                    is_colored,
                    amount_paid,
                    success
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Database error in log_print_job: {e}")
            return None
    
    def log_payment(self, amount, print_job_id=None):
        """
        Log a payment transaction.
        
        Args:
            amount (float): Amount paid
            print_job_id (int, optional): ID of the associated print job
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO payment_transactions (
                    timestamp, amount, print_job_id
                ) VALUES (?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    amount,
                    print_job_id
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error in log_payment: {e}")
            return False
    
    def log_admin_access(self, action, details=None):
        """
        Log admin access activity.
        
        Args:
            action (str): Description of the action performed
            details (str, optional): Additional details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO admin_access_log (
                    timestamp, action, details
                ) VALUES (?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    action,
                    details
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error in log_admin_access: {e}")
            return False
    
    def get_total_revenue(self, start_date=None, end_date=None):
        """
        Get total revenue from payment transactions.
        
        Args:
            start_date (str, optional): Start date filter (ISO format)
            end_date (str, optional): End date filter (ISO format)
            
        Returns:
            float: Total revenue
        """
        query = 'SELECT SUM(amount) FROM payment_transactions'
        params = []
        
        if start_date or end_date:
            query += ' WHERE '
            if start_date:
                query += 'timestamp >= ?'
                params.append(start_date)
            if end_date:
                if start_date:
                    query += ' AND '
                query += 'timestamp <= ?'
                params.append(end_date)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return float(result[0]) if result[0] else 0.0
        except Exception as e:
            print(f"Database error in get_total_revenue: {e}")
            return 0.0
    
    def get_total_pages_printed(self, start_date=None, end_date=None):
        """
        Get total pages printed.
        
        Args:
            start_date (str, optional): Start date filter (ISO format)
            end_date (str, optional): End date filter (ISO format)
            
        Returns:
            int: Total pages printed
        """
        query = 'SELECT SUM(pages * copies) FROM print_jobs WHERE success = 1'
        params = []
        
        if start_date or end_date:
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return int(result[0]) if result[0] else 0
        except Exception as e:
            print(f"Database error in get_total_pages_printed: {e}")
            return 0
    
    def get_print_job_stats(self, limit=10):
        """
        Get statistics about recent print jobs.
        
        Args:
            limit (int, optional): Maximum number of records to return
            
        Returns:
            list: List of print job records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM print_jobs 
                ORDER BY timestamp DESC 
                LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Database error in get_print_job_stats: {e}")
            return []
    
    def verify_admin_pattern(self, input_pattern):
        """
        Verify an admin access pattern against the stored pattern.
        
        Args:
            input_pattern (str): Input pattern to verify
            
        Returns:
            bool: True if pattern matches, False otherwise
        """
        stored_pattern = self.get_setting('admin_pattern', '1,2,3,4')
        return input_pattern == stored_pattern