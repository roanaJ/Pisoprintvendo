"""
Screen modules for the PisoPrint Vendo system.
Provides user interface components for different application screens.
"""

# Import all screen classes for easy access
from src.screens.main_screen import MainScreen
from src.screens.admin_screen import AdminScreen, AdminPatternScreen
from src.screens.guide_screen import GuideScreen
from src.screens.receive_screen import ReceiveScreen
from src.screens.preview_screen import PreviewScreen
from src.screens.selection_screen import SelectionScreen
from src.screens.payment_screen import PaymentScreen
from src.screens.printing_screen import PrintingScreen
from src.screens.base_screen import BaseScreen

# Define available screens for the application
__all__ = [
    'BaseScreen',
    'MainScreen',
    'AdminScreen',
    'AdminPatternScreen',
    'GuideScreen',
    'ReceiveScreen',
    'PreviewScreen',
    'SelectionScreen',
    'PaymentScreen',
    'PrintingScreen'
]