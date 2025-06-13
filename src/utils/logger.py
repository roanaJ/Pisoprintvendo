"""
Logging utility for the PisoPrint Vendo system.
Handles logging of events, errors, payments, and print jobs.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Configure logger
logger = logging.getLogger('pisoprint')
logger.setLevel(logging.DEBUG)

# Create file handler for logging to file
log_file = logs_dir / f"pisoprint_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create console handler for logging to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_event(event_type, message):
    """
    Log an application event.
    
    Args:
        event_type (str): Type of event
        message (str): Event message
    """
    logger.info(f"{event_type}: {message}")

def log_error(component, message):
    """
    Log an error.
    
    Args:
        component (str): Component where the error occurred
        message (str): Error message
    """
    logger.error(f"{component}: {message}")

def log_payment(amount):
    """
    Log a payment transaction.
    
    Args:
        amount (float): Payment amount
    """
    logger.info(f"PAYMENT: Received ₱{amount}")

def log_print_job(filename, copies, pages):
    """
    Log a print job.
    
    Args:
        filename (str): Name of the printed file
        copies (int): Number of copies
        pages (int): Number of pages
    """
    logger.info(f"PRINT_JOB: {filename}, {copies} copies, {pages} pages")