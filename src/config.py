"""
Configuration settings for the PisoPrint Vendo application.
This module centralizes all configurable parameters.
"""
import os
from pathlib import Path

# Application information
APP_NAME = "PisoPrint Vendo"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Research Group 1"

# File paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "image_ctu.ico")
LOGO_PATH = os.path.join(ASSETS_DIR, "image_ctu.png")

# UI settings
FULLSCREEN = True
KIOSK_MODE = True
DEFAULT_BG_COLOR = "white"
HEADER_BG_COLOR = "#248CCF"
BUTTON_COLORS = {
    "main": "#90EE90",  # Light green
    "action": "#7FFFD4",  # Turquoise
    "warning": "#FFEB3B",  # Yellow
    "danger": "#FF0000",  # Red
    "numpad": "#FFEB3B",  # Yellow
}
FONT_FAMILY = "Inter"

# Printer settings
DEFAULT_PRINTER = None  # None means use system default

# Hardware settings
COIN_ACCEPTOR_PORT = "COM4"
COIN_ACCEPTOR_BAUDRATE = 9600
COIN_VALUES = {
    1: 1,    # 1 pulse = 1 peso
    2: 5,    # 2 pulses = 5 pesos
    3: 10,   # 3 pulses = 10 pesos
    4: 20    # 4 pulses = 20 pesos
}

# Pricing settings
PRICE_BW_PAGE = 3  # 3 pesos per black & white page
PRICE_COLOR_PAGE = 5  # 5 pesos per colored page

# External applications
SUMATRA_PATHS = [
    r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
    r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
    r"C:\Users\Waren\AppData\Local\SumatraPDF\SumatraPDF.exe",
]

# Bluetooth settings
BLUETOOTH_DEVICE_NAME = "ORANGEPIZERO3"

# Debug mode
DEBUG = False