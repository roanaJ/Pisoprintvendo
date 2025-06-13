"""
PisoPrint Vendo Monitoring Web App.
This Flask application provides remote monitoring of the PisoPrint Vendo system.
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, make_response
import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
from functools import wraps
import uuid
import hashlib

# Fix import path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

# Import the SQLite manager from the main project
try:
    from src.utils.sqlite_manager import SQLiteManager
except ImportError as e:
    print(f"Error importing SQLiteManager: {e}")
    sys.exit(1)

# Import the custom sensor class
try:
    from src.monitor.sensor import PisoPrintSensors
except ImportError as e:
    print(f"Error importing PisoPrintSensors: {e}")
    sys.exit(1)

# Get absolute paths
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

# Initialize Flask with correct paths
app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir)

# Enable template auto-reload
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Debug path resolution
print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Template directory: {template_dir}")
print(f"Template directory exists: {os.path.exists(template_dir)}")
if os.path.exists(template_dir):
    print(f"Files in template directory: {os.listdir(template_dir)}")
print(f"Static directory: {static_dir}")

app.config['SECRET_KEY'] = 'pisoprint_monitor_key'

# Initialize database manager with error handling
try:
    db_manager = SQLiteManager()
    print("Database manager initialized successfully")
except Exception as e:
    print(f"Error initializing database manager: {e}")
    db_manager = None

# Initialize sensor manager with error handling
try:
    sensor_manager = PisoPrintSensors(db_manager)
    print("Sensor manager initialized successfully")
except Exception as e:
    print(f"Error initializing sensor manager: {e}")
    sensor_manager = None

# Only start monitoring if sensor manager was initialized successfully
if sensor_manager:
    try:
        # Start monitoring with 10-second interval
        sensor_manager.start_monitoring(10)
        print("Sensor monitoring started")
    except Exception as e:
        print(f"Error starting sensor monitoring: {e}")

# Add a context processor to provide current_year to all templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('user_role') != 'administrator':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with enhanced device recognition"""
    # Check for auto-login cookie
    device_token = request.cookies.get('pisoprint_device')
    
    if device_token:
        # Try to auto-login with device token
        user = db_manager.authenticate_with_token(device_token)
        if user:
            # Set up session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            
            # Renew the cookie for another 30 days
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                response = redirect(next_page)
            else:
                response = redirect(url_for('dashboard'))
                
            response.set_cookie('pisoprint_device', device_token, 
                               max_age=60*60*24*30, httponly=True, 
                               samesite='Lax')
            return response
    
    # Show reset success message if applicable
    if request.args.get('reset') == 'success':
        flash('Password has been reset successfully. Please login with your new password.', 'success')
    
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = db_manager.authenticate_user(username, password)
        
        if user:
            # Set up session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            
            if remember:
                # Session expires after 30 days
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
                
                # Create a device token for persistent login
                device_token = str(uuid.uuid4())
                db_manager.store_device_token(user['id'], device_token)
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    response = redirect(next_page)
                else:
                    response = redirect(url_for('dashboard'))
                
                # Set a long-lived cookie
                response.set_cookie('pisoprint_device', device_token, 
                                   max_age=60*60*24*30, httponly=True, 
                                   samesite='Lax')
                return response
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Index page redirects to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard view with system status overview"""
    return render_template('dashboard.html')

@app.route('/transactions')
@login_required
def transactions():
    """Show transaction history"""
    return render_template('transactions.html')

@app.route('/maintenance')
@login_required
def maintenance():
    """Maintenance view with system health and logs"""
    return render_template('maintenance.html')

@app.route('/settings')
@admin_required
def settings():
    """Settings view for system configuration"""
    return render_template('settings.html')

# Add a new route for user management (admin only)
@app.route('/users')
@admin_required
def users():
    """User management page"""
    users_list = db_manager.get_all_users()
    return render_template('users.html', users=users_list)

# Add a new API route for user operations
@app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def api_users():
    """API endpoint for user management"""
    if request.method == 'GET':
        users_list = db_manager.get_all_users()
        return jsonify({
            'status': 'ok',
            'users': users_list
        })
    
    elif request.method == 'POST':
        # Add new user
        data = request.json
        if not all(k in data for k in ['username', 'password', 'role']):
            return jsonify({'status': 'error', 'message': 'Missing required fields'})
        
        success = db_manager.add_user(
            data['username'], 
            data['password'], 
            data['role'],
            data.get('email')
        )
        
        if success:
            return jsonify({'status': 'ok', 'message': 'User created successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Username or email already exists'})
    
    elif request.method == 'PUT':
        # Update user
        data = request.json
        if 'id' not in data:
            return jsonify({'status': 'error', 'message': 'User ID required'})
        
        success = db_manager.update_user(data['id'], data)
        
        if success:
            return jsonify({'status': 'ok', 'message': 'User updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update user'})
    
    elif request.method == 'DELETE':
        # Delete user
        data = request.json
        if 'id' not in data:
            return jsonify({'status': 'error', 'message': 'User ID required'})
        
        # Prevent self-deletion
        if int(data['id']) == session.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Cannot delete your own account'})
        
        success = db_manager.delete_user(data['id'])
        
        if success:
            return jsonify({'status': 'ok', 'message': 'User deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete user'})

# API Endpoints
@app.route('/api/system-status')
def api_system_status():
    """Return system status data as JSON"""
    try:
        # Get system data
        system_data = {}
        
        # Check if printer is detected using system functions
        printer_detected = False
        printer_name = None
        printer_error = None
        
        try:
            # Try to get printer information
            import subprocess
            result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                printer_detected = True
                # Extract printer name from output if available
                lines = result.stdout.strip().split('\n')
                if lines and len(lines) > 0:
                    printer_name = lines[0].split(' ')[1] if len(lines[0].split(' ')) > 1 else "Default Printer"
            else:
                # Check Windows systems
                result = subprocess.run(['wmic', 'printer', 'get', 'name'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        printer_detected = True
                        printer_name = lines[1].strip()
        except Exception as e:
            printer_error = str(e)
            app.logger.error(f"Error checking printer: {e}")
        
        # Example data structure with enhanced printer detection
        system_data = {
            'status': 'ok',
            'system_info': {
                'total_revenue': db_manager.get_total_revenue() if hasattr(db_manager, 'get_total_revenue') else 702,
                'total_pages': db_manager.get_total_pages_printed() if hasattr(db_manager, 'get_total_pages_printed') else 56,
                'recent_jobs_count': db_manager.get_recent_jobs_count(24) if hasattr(db_manager, 'get_recent_jobs_count') else 0,
                'days_since_maintenance': 17,
                'last_maintenance': '2025-02-22',
                'printer_detected': printer_detected,
                'printer_name': printer_name or "Epson L121",
                'printer_online': printer_detected,  # Assume it's online if detected
                'printer_error': printer_error,
                'system_uptime': '3 days, 7 hours',
                'last_reboot': '2025-03-09T01:57:00'
            },
            'sensor_data': {
                # Sensor data will come from sensor_manager
            }
        }
        
        return jsonify(system_data)
    except Exception as e:
        app.logger.error(f"Error in system status API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/transactions')
def api_transactions():
    """Return transaction data as JSON"""
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        
        # Get transaction data
        transactions = db_manager.get_print_job_stats(100)
        
        # Convert to better format for frontend
        formatted_transactions = []
        for tx in transactions:
            formatted_transactions.append({
                'id': tx['id'],
                'date': tx['timestamp'].split('T')[0],
                'time': tx['timestamp'].split('T')[1].split('.')[0],
                'filename': tx['filename'],
                'pages': tx['pages'],
                'copies': tx['copies'],
                'total_pages': tx['pages'] * tx['copies'],
                'type': 'Color' if tx['is_colored'] else 'B&W',
                'amount': f"₱{tx['amount_paid']}",
                'amount_raw': tx['amount_paid'],
                'status': 'Success' if tx['success'] else 'Failed'
            })
        
        # Get revenue data by day for the chart
        stats = db_manager.get_daily_stats(days)
        chart_data = []
        for day, data in stats.items():
            chart_data.append({
                'date': day,
                'revenue': data['revenue'],
                'pages': data['pages'],
                'jobs': data['jobs']
            })
        
        # Summary data
        total_revenue = db_manager.get_total_revenue()
        total_pages = db_manager.get_total_pages_printed()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'transactions': formatted_transactions,
            'chart_data': chart_data,
            'summary': {
                'total_revenue': total_revenue,
                'total_pages': total_pages,
                'average_per_job': round(total_revenue / len(transactions), 2) if len(transactions) > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/sensor-data')
def api_sensor_data():
    """Return the current sensor data as JSON"""
    try:
        sensor_data = sensor_manager.get_sensor_data()
        # Add Arduino connection status
        sensor_data['arduino_connected'] = sensor_manager.arduino is not None
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'sensor_data': sensor_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    """Return the current settings as JSON"""
    try:
        settings = {
            'price_bw_page': float(db_manager.get_setting('price_bw_page', 3)),
            'price_color_page': float(db_manager.get_setting('price_color_page', 5)),
            'max_payment_amount': float(db_manager.get_setting('max_payment_amount', 100)),
            'printer_name': db_manager.get_setting('printer_name', ''),
            'system_name': db_manager.get_setting('system_name', 'PisoPrint Vendo'),
            'paper_capacity': int(db_manager.get_setting('paper_capacity', 500)),
            'admin_pattern': db_manager.get_setting('admin_pattern', '1,2,3,4'),
            'session_timeout': int(db_manager.get_setting('session_timeout', 30)),
        }
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'settings': settings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """Update settings from POST data"""
    try:
        data = request.json
        settings = data.get('settings', {})
        
        # Update each setting
        for key, value in settings.items():
            db_manager.set_setting(key, value)
            
        # Log the update
        db_manager.log_admin_access("Settings updated via web interface", 
                                  f"Settings updated: {', '.join(settings.keys())}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Settings updated successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/admin-logs')
def api_admin_logs():
    """Return admin access logs as JSON"""
    try:
        logs = db_manager.get_admin_logs(50)
        
        # Format logs for frontend
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'id': log['id'],
                'date': log['timestamp'].split('T')[0],
                'time': log['timestamp'].split('T')[1].split('.')[0],
                'action': log['action'],
                'details': log['details'] or 'No details'
            })
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'logs': formatted_logs
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/reset-maintenance')
def api_reset_maintenance():
    """Reset the maintenance date to today"""
    try:
        db_manager.set_setting('last_maintenance', datetime.now().isoformat())
        db_manager.log_admin_access("Maintenance reset", "Maintenance date reset via web interface")
        
        return jsonify({
            'status': 'ok',
            'message': 'Maintenance date reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/restock-paper')
def api_restock_paper():
    """Restock paper to full capacity"""
    try:
        paper_capacity = int(db_manager.get_setting('paper_capacity', 500))
        db_manager.set_setting('paper_level', paper_capacity)
        db_manager.log_admin_access("Paper restocked", f"Paper level set to {paper_capacity} via web interface")
        
        return jsonify({
            'status': 'ok',
            'message': f'Paper restocked to {paper_capacity} sheets',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/refill-ink/<color>')
def api_refill_ink(color):
    """Refill a specific ink cartridge"""
    try:
        if color not in ['black', 'cyan', 'magenta', 'yellow']:
            return jsonify({
                'status': 'error',
                'error': f'Invalid ink color: {color}',
                'timestamp': datetime.now().isoformat()
            })
        
        db_manager.set_setting(f'ink_level_{color}', 100)
        sensor_manager.ink_levels[color] = 100
        db_manager.log_admin_access("Ink refilled", f"{color} ink refilled via web interface")
        
        return jsonify({
            'status': 'ok',
            'message': f'{color.capitalize()} ink refilled to 100%',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/arduino', methods=['POST'])
def api_arduino_command():
    """Send a command to the Arduino"""
    try:
        data = request.json
        command = data.get('command')
        params = data.get('params', {})
        
        if command == 'tare':
            # Send tare command to scale
            response = sensor_manager.send_command('TARE')
            success = response == 'TARE_COMPLETE'
        elif command == 'calibrate_empty':
            # Calibrate with empty tray - Epson L121 specific
            result = sensor_manager.calibrate_paper_sensor(known_sheets=0, printer_model="EPSON_L121")
            success = result.get('success', False)
            response = result
        elif command == 'calibrate_full':
            # Calibrate with exactly 50 A4 sheets - Epson L121 specific
            result = sensor_manager.calibrate_paper_sensor(known_sheets=50, printer_model="EPSON_L121")
            success = result.get('success', False)
            response = result
        elif command == 'test_sensors':
            # Read raw sensor values
            ink_readings = {}
            for color in ['black', 'cyan', 'magenta', 'yellow']:
                resp = sensor_manager.send_command(f"READ_INK_{color.upper()}")
                if resp:
                    ink_readings[color] = resp
            weight_resp = sensor_manager.send_command("READ_WEIGHT")
            success = True
            response = {
                'ink_readings': ink_readings,
                'weight_reading': weight_resp
            }
        elif command == 'connect':
            # Try to connect to Arduino on specified port
            port = params.get('port', 'COM4')
            sensor_manager.arduino_port = port
            success = sensor_manager.initialize_arduino()
            response = {'connected': success}
        else:
            success = False
            response = {'error': f'Unknown command: {command}'}
        
        return jsonify({
            'status': 'ok' if success else 'error',
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/profile')
@login_required
def profile():
    """User profile page for viewing and updating account information"""
    # Get user data
    user_data = db_manager.get_user_by_id(session.get('user_id'))
    return render_template('profile.html', user_data=user_data)

# Add route for forgot password
@app.route('/forgot-password')
def forgot_password():
    """Forgot password page"""
    return render_template('forgot_password.html')

# API route for changing user's own password
@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """API endpoint for changing password"""
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Verify current password
    user_id = session.get('user_id')
    username = session.get('username')
    
    # Check if current password is correct
    verify_result = db_manager.authenticate_user(username, current_password)
    if not verify_result:
        return jsonify({'status': 'error', 'message': 'Current password is incorrect'})
    
    # Update password
    success = db_manager.update_user_password(user_id, new_password)
    
    if success:
        # Log the action
        db_manager.log_admin_access("Password changed", f"User {username} changed their password")
        return jsonify({'status': 'ok', 'message': 'Password updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to update password'})

# API route for checking username in forgot password flow
@app.route('/api/check-username', methods=['POST'])
def api_check_username():
    """API endpoint to check if a username exists"""
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'Username is required'})
    
    user_exists = db_manager.check_username_exists(username)
    
    if user_exists:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Username not found'})

# API route for verifying admin PIN
@app.route('/api/verify-admin-pin', methods=['POST'])
def api_verify_admin_pin():
    """API endpoint to verify admin PIN for password reset"""
    data = request.json
    username = data.get('username')
    admin_pin = data.get('admin_pin')
    
    if not username or not admin_pin:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Get stored admin pattern
    stored_pattern = db_manager.get_setting('admin_pattern', '1,2,3,4')
    
    if admin_pin == stored_pattern:
        # Create a temporary reset token and store it
        reset_token = str(uuid.uuid4())
        db_manager.store_reset_token(username, reset_token)
        
        return jsonify({'status': 'ok', 'token': reset_token})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid admin PIN'})

# API route for resetting password
@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """API endpoint for resetting password after PIN verification"""
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')
    
    if not username or not new_password:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Reset the password
    success = db_manager.reset_user_password(username, new_password)
    
    if success:
        # Log the action
        db_manager.log_admin_access("Password reset", f"Password reset for user {username} via admin PIN")
        return jsonify({'status': 'ok', 'message': 'Password reset successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to reset password'})

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, 
                          error_message="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error_code=500, 
                          error_message="Internal Server Error"), 500

def shutdown_server():
    """Clean up resources when shutting down"""
    sensor_manager.shutdown()

# Remove the auto-start code and make it conditional
if __name__ == '__main__':
    # Only start the server if running directly
    try:
        # Register shutdown handler
        import atexit
        atexit.register(shutdown_server)
        
        # Get port from command line or default to 5000
        import sys
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
        
        # Verify critical components before starting
        if not db_manager:
            print("ERROR: Database manager failed to initialize. Cannot start server.")
            sys.exit(1)
            
        # Start the server
        print(f"Starting PisoPrint Monitor on port {port}")
        print(f"Visit http://localhost:{port} in your browser")
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        print("Shutting down PisoPrint Monitor...")
        shutdown_server()
    except Exception as e:
        print(f"Error starting server: {e}")
        shutdown_server()
        sys.exit(1)