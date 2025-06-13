"""
Buzzer Interface for the PisoPrint Vendo system.
Handles sound feedback through Arduino buzzer.
"""
class BuzzerInterface:
    def __init__(self, arduino_interface):
        """
        Initialize the buzzer interface.
        
        Args:
            arduino_interface: Arduino interface instance for communication
        """
        self.arduino = arduino_interface
        
    def button_click(self):
        """Sound feedback for button clicks"""
        if self.arduino and self.arduino.serial:
            self.arduino.serial.write(b'BEEP:SHORT\n')
            
    def success(self):
        """Sound feedback for successful operations"""
        if self.arduino and self.arduino.serial:
            self.arduino.serial.write(b'BEEP:SUCCESS\n')
            
    def error(self):
        """Sound feedback for errors"""
        if self.arduino and self.arduino.serial:
            self.arduino.serial.write(b'BEEP:ERROR\n')