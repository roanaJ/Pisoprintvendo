"""
SQLite Database Manager for PisoPrint Vendo.
Provides concrete implementation for the database operations.
"""
import os
import sqlite3
import json
from datetime import datetime
import threading
from pathlib import Path

class SQLiteManager:
    """SQLite implementation of the database operations"""
    
    def __init__(self, db_path=None):
        """
        Initialize the SQLite manager.
        
        Args:
            db_path (str, optional): Path to the database file. Defaults to 'data/pisoprint.db'.
        """
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'pisoprint.db'
            
        self.db_path = str(db_path)
        self.lock = threading.RLock()  # Thread-safe operations
        self.initialize_db()
        
    def initialize_db(self):
        """Initialize the database with required tables if they don't exist."""
        with self.lock:
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
                    print_job_id INTEGER NULL,
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
                
                # Create system_stats table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    stat_type TEXT,
                    value REAL,
                    notes TEXT
                )
                ''')
                
                # Create users table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
                ''')
                
                # Create device_tokens table for persistent login
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                ''')
                
                # Create password_reset_tokens table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    username TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
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
                    'last_maintenance': datetime.now().isoformat(),
                    'paper_capacity': 500,
                    'paper_level': 500,
                    'session_timeout': 30  # 30 minutes default timeout
                }
                
                for key, value in default_settings.items():
                    cursor.execute('''
                    INSERT OR IGNORE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                    ''', (key, str(value), datetime.now().isoformat()))
                    
                # Add a default admin user if none exists
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    import hashlib
                    default_password = hashlib.sha256("admin123".encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        ("admin", default_password, "administrator")
                    )
                
                conn.commit()
    
    def execute_query(self, query, params=None, fetch_all=False, fetch_one=False):
        """
        Execute an SQL query with error handling.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            fetch_all (bool, optional): Whether to fetch all results
            fetch_one (bool, optional): Whether to fetch one result
            
        Returns:
            The query result based on the fetch parameters
        """
        params = params or ()
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    
                    if fetch_all:
                        return cursor.fetchall()
                    elif fetch_one:
                        return cursor.fetchone()
                    elif query.strip().upper().startswith('INSERT'):
                        return cursor.lastrowid
                    else:
                        conn.commit()
                        return True
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return None
    
    def get_setting(self, key, default=None):
        """
        Get a setting value from the database.
        
        Args:
            key (str): Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Value of the setting or default if not found
        """
        query = 'SELECT value FROM settings WHERE key = ?'
        result = self.execute_query(query, (key,), fetch_one=True)
        
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
    
    def set_setting(self, key, value):
        """
        Set a setting value in the database.
        
        Args:
            key (str): Setting key
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert non-string values to JSON
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)
            
        query = '''
        INSERT OR REPLACE INTO settings (key, value, updated_at)
        VALUES (?, ?, ?)
        '''
        return self.execute_query(query, (key, value, datetime.now().isoformat()))
    
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
        query = '''
        INSERT INTO print_jobs (
            timestamp, filename, pages, copies, is_colored, amount_paid, success
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            datetime.now().isoformat(),
            filename,
            pages,
            copies,
            is_colored,
            amount_paid,
            success
        )
        
        job_id = self.execute_query(query, params)
        
        # Update paper level
        if success and job_id:
            self.update_paper_level(pages * copies)
            
        return job_id
    
    def update_paper_level(self, pages_used):
        """
        Update paper level after printing.
        
        Args:
            pages_used (int): Number of pages used in the print job
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get current paper level
        current_level = int(self.get_setting('paper_level', 0))
        
        # Update to new level (ensure it doesn't go below 0)
        new_level = max(0, current_level - pages_used)
        
        # Update the setting
        result = self.set_setting('paper_level', new_level)
        
        # Log if paper is running low (below 20% of capacity)
        capacity = int(self.get_setting('paper_capacity', 500))
        if new_level / capacity < 0.2:
            self.log_system_stat('paper_low', new_level, f"Paper level is low: {new_level}/{capacity}")
            
        return result
    
    def log_payment(self, amount, print_job_id=None):
        """
        Log a payment transaction.
        
        Args:
            amount (float): Amount paid
            print_job_id (int, optional): ID of the associated print job
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        INSERT INTO payment_transactions (
            timestamp, amount, print_job_id
        ) VALUES (?, ?, ?)
        '''
        params = (
            datetime.now().isoformat(),
            amount,
            print_job_id
        )
        
        result = self.execute_query(query, params)
        
        # Also log to system stats
        self.log_system_stat('revenue', amount, f"Payment received: ₱{amount}")
        
        return result is not None
    
    def log_admin_access(self, action, details=None):
        """
        Log admin access activity.
        
        Args:
            action (str): Description of the action performed
            details (str, optional): Additional details
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        INSERT INTO admin_access_log (
            timestamp, action, details
        ) VALUES (?, ?, ?)
        '''
        params = (
            datetime.now().isoformat(),
            action,
            details
        )
        
        return self.execute_query(query, params) is not None
    
    def log_system_stat(self, stat_type, value, notes=None):
        """
        Log a system statistic.
        
        Args:
            stat_type (str): Type of statistic (e.g., 'paper_used', 'revenue')
            value (float): Value of the statistic
            notes (str, optional): Additional notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        INSERT INTO system_stats (
            timestamp, stat_type, value, notes
        ) VALUES (?, ?, ?, ?)
        '''
        params = (
            datetime.now().isoformat(),
            stat_type,
            value,
            notes
        )
        
        return self.execute_query(query, params) is not None
    
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
        
        result = self.execute_query(query, tuple(params), fetch_one=True)
        return float(result[0]) if result and result[0] else 0.0
    
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
        
        result = self.execute_query(query, tuple(params), fetch_one=True)
        return int(result[0]) if result and result[0] else 0
    
    def get_print_job_stats(self, limit=10):
        """
        Get statistics about recent print jobs.
        
        Args:
            limit (int, optional): Maximum number of records to return
            
        Returns:
            list: List of print job records
        """
        with self.lock:
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
            except sqlite3.Error as e:
                print(f"SQLite error in get_print_job_stats: {e}")
                return []
    
    def get_admin_logs(self, limit=50):
        """
        Get admin access logs.
        
        Args:
            limit (int, optional): Maximum number of records to return
            
        Returns:
            list: List of admin access log records
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('''
                    SELECT * FROM admin_access_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                    ''', (limit,))
                    
                    return [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                print(f"SQLite error in get_admin_logs: {e}")
                return []
    
    def get_daily_stats(self, days=30):
        """
        Get daily statistics for the last N days.
        
        Args:
            days (int, optional): Number of days to retrieve
            
        Returns:
            dict: Dictionary with daily statistics
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    # Get daily revenue
                    cursor.execute('''
                    SELECT 
                        date(timestamp) as day,
                        SUM(amount) as revenue
                    FROM payment_transactions
                    WHERE timestamp >= date('now', ?)
                    GROUP BY day
                    ORDER BY day
                    ''', (f'-{days} days',))
                    
                    revenue_data = {row['day']: row['revenue'] for row in cursor.fetchall()}
                    
                    # Get daily pages printed
                    cursor.execute('''
                    SELECT 
                        date(timestamp) as day,
                        SUM(pages * copies) as pages
                    FROM print_jobs
                    WHERE success = 1 AND timestamp >= date('now', ?)
                    GROUP BY day
                    ORDER BY day
                    ''', (f'-{days} days',))
                    
                    pages_data = {row['day']: row['pages'] for row in cursor.fetchall()}
                    
                    # Get daily print jobs count
                    cursor.execute('''
                    SELECT 
                        date(timestamp) as day,
                        COUNT(*) as jobs
                    FROM print_jobs
                    WHERE success = 1 AND timestamp >= date('now', ?)
                    GROUP BY day
                    ORDER BY day
                    ''', (f'-{days} days',))
                    
                    jobs_data = {row['day']: row['jobs'] for row in cursor.fetchall()}
                    
                    # Combine all data
                    result = {}
                    all_days = set(revenue_data.keys()) | set(pages_data.keys()) | set(jobs_data.keys())
                    
                    for day in sorted(all_days):
                        result[day] = {
                            'revenue': revenue_data.get(day, 0),
                            'pages': pages_data.get(day, 0),
                            'jobs': jobs_data.get(day, 0)
                        }
                    
                    return result
            except sqlite3.Error as e:
                print(f"SQLite error in get_daily_stats: {e}")
                return {}
    
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
    
    def backup_database(self, backup_path=None):
        """
        Create a backup of the database.
        
        Args:
            backup_path (str, optional): Path for the backup file
            
        Returns:
            str: Path to the backup file or None if failed
        """
        if backup_path is None:
            # Create backups directory if it doesn't exist
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f'pisoprint_backup_{timestamp}.db'
        
        with self.lock:
            try:
                # Create backup using SQLite's backup API
                with sqlite3.connect(self.db_path) as source_conn:
                    with sqlite3.connect(str(backup_path)) as target_conn:
                        source_conn.backup(target_conn)
                
                # Log the backup
                self.log_admin_access("Database backup", f"Backup created at {backup_path}")
                
                return str(backup_path)
            except sqlite3.Error as e:
                print(f"SQLite error in backup_database: {e}")
                return None

    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        params = (username, hashed_password)
        
        result = self.execute_query(query, params, fetch_one=True)
        
        if result:
            # Update last login time
            self.execute_query("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (result[0],))
            return {"id": result[0], "username": result[1], "role": result[2]}
        return None

    def add_user(self, username, password, role, email=None):
        """Add a new user to the system"""
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            self.execute_query("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)", (username, hashed_password, role, email))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_users(self):
        """Get all users from the database"""
        query = "SELECT id, username, role, email, created_at, last_login FROM users"
        result = self.execute_query(query, fetch_all=True)
        return [dict(zip([col[0] for col in self.cursor.description], row)) for row in result]

    def update_user(self, user_id, data):
        """Update user information"""
        valid_fields = ["username", "email", "role"]
        set_clause = ", ".join([f"{field} = ?" for field in data if field in valid_fields])
        values = [data[field] for field in data if field in valid_fields]
        
        if "password" in data and data["password"]:
            import hashlib
            hashed_password = hashlib.sha256(data["password"].encode()).hexdigest()
            set_clause += ", password = ?"
            values.append(hashed_password)
        
        values.append(user_id)
        
        if set_clause:
            self.execute_query(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(values))
            return True
        return False

    def delete_user(self, user_id):
        """Delete a user from the system"""
        self.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
        return self.execute_query("SELECT changes()", fetch_one=True)[0] > 0

    def get_user_by_id(self, user_id):
        """Get user data by ID"""
        query = "SELECT id, username, role, email, created_at, last_login FROM users WHERE id = ?"
        result = self.execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            columns = ["id", "username", "role", "email", "created_at", "last_login"]
            return dict(zip(columns, result))
        return None

    def check_username_exists(self, username):
        """Check if a username exists in the database"""
        query = "SELECT COUNT(*) FROM users WHERE username = ?"
        result = self.execute_query(query, (username,), fetch_one=True)
        return result[0] > 0 if result else False

    def update_user_password(self, user_id, new_password):
        """Update a user's password"""
        import hashlib
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        query = "UPDATE users SET password = ? WHERE id = ?"
        return self.execute_query(query, (hashed_password, user_id))

    def reset_user_password(self, username, new_password):
        """Reset a user's password by username"""
        import hashlib
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        query = "UPDATE users SET password = ? WHERE username = ?"
        return self.execute_query(query, (hashed_password, username))

    def store_reset_token(self, username, token):
        """Store a password reset token"""
        from datetime import datetime, timedelta
        
        # Token expires in 1 hour
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
        
        query = """
        INSERT OR REPLACE INTO password_reset_tokens (username, token, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (username, token, datetime.now().isoformat(), expires_at))

    def store_device_token(self, user_id, token):
        """Store a device token for automatic login"""
        query = """
        INSERT INTO device_tokens (token, user_id, created_at, last_used)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (token, user_id, datetime.now().isoformat(), datetime.now().isoformat()))

    def authenticate_with_token(self, token):
        """Authenticate a user with a device token"""
        from datetime import datetime
        
        query = """
        SELECT u.id, u.username, u.role 
        FROM device_tokens d
        JOIN users u ON d.user_id = u.id
        WHERE d.token = ?
        """
        result = self.execute_query(query, (token,), fetch_one=True)
        
        if result:
            # Update last_used timestamp
            update_query = "UPDATE device_tokens SET last_used = ? WHERE token = ?"
            self.execute_query(update_query, (datetime.now().isoformat(), token))
            
            return {"id": result[0], "username": result[1], "role": result[2]}
        return None