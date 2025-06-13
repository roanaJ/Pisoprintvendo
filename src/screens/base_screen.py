"""
Base Screen class with sound feedback functionality.
Parent class for all screens in the PisoPrint Vendo system.
"""
import tkinter as tk
from src.utils.logger import logger

class BaseScreen:
    def __init__(self, app):
        self.app = app
        
    def create_button(self, parent, **kwargs):
        """
        Create a button with sound feedback.
        
        Args:
            parent: Parent widget
            **kwargs: Button parameters
            
        Returns:
            tk.Button: Button with sound feedback
        """
        original_command = kwargs.get('command', None)
        
        def command_with_sound():
            try:
                # Play button click sound if buzzer is available
                if hasattr(self.app, 'buzzer') and self.app.buzzer:
                    self.app.buzzer.button_click()
                # Execute original command if it exists
                if original_command:
                    original_command()
            except Exception as e:
                logger.error(f"Button error: {e}")
                
        kwargs['command'] = command_with_sound
        return tk.Button(parent, **kwargs)

    def play_error_sound(self):
        """Play error sound if buzzer is available"""
        if hasattr(self.app, 'buzzer') and self.app.buzzer:
            self.app.buzzer.error()

    def play_success_sound(self):
        """Play success sound if buzzer is available"""
        if hasattr(self.app, 'buzzer') and self.app.buzzer:
            self.app.buzzer.success()