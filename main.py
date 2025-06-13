#!/usr/bin/env python3
"""
PisoPrint Vendo - Main entry point for the application.
"""
import os
import sys
import argparse
import tkinter as tk

# Add the current directory to Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main application
from src.pisoprint_app import PisoPrintSystem
from src.config import FULLSCREEN, KIOSK_MODE, ICON_PATH
from src.utils.logger import logger, log_event

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='PisoPrint Vendo - PDF printing kiosk')
    parser.add_argument('--windowed', action='store_true', 
                       help='Run in windowed mode instead of fullscreen')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging and features')
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize Tkinter
    root = tk.Tk()
    
    # Log application start
    log_event("STARTUP", "Application starting")
    
    # Set application title
    root.title("PisoPrint Vendo")
    
    # Set application icon (only if file exists)
    try:
        if os.path.exists(ICON_PATH):
            root.iconbitmap(ICON_PATH)
    except Exception as e:
        log_event("WARNING", f"Could not set icon: {e}")
    
    # Configure for fullscreen kiosk mode unless windowed mode is requested
    if not args.windowed:
        if FULLSCREEN:
            root.attributes('-fullscreen', True)
        
        if KIOSK_MODE:
            # Make it fullscreen with no decorations
            root.overrideredirect(True)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Keep window always on top
            root.attributes('-topmost', True)
            
            # Disable alt+f4
            root.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Ensure window has focus
            root.focus_force()
    else:
        # Windowed mode for development/testing
        root.geometry("1024x768")
    
    # Initialize the app with debug mode if requested
    app = PisoPrintSystem(root, debug_mode=args.debug)
    
    # Log application ready
    log_event("STARTUP", "Application initialized and ready")
    
    # Run the application
    app.run()
    
    # Log application exit
    log_event("SHUTDOWN", "Application exiting")

# Try this instead in main.py:
try:
    from src.utils.logger import logger, log_event
except ImportError:
    print("Direct import failed, trying relative import...")
    try:
        # Alternative import method
        import logging
        logger = logging.getLogger('pisoprint')
        def log_event(event_type, message):
            print(f"[{event_type}] {message}")
    except Exception as e:
        print(f"Error setting up logger: {e}")
        # Basic fallback
        logger = None
        def log_event(event_type, message):
            print(f"[{event_type}] {message}")
            
if __name__ == "__main__":
    main()