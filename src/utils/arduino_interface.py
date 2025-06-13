"""
Arduino Interface for the PisoPrint Vendo system.
Handles communication with Arduino for coin acceptor and admin button.
"""
import serial
import threading
import time
from src.utils.logger import logger, log_event, log_error

class ArduinoInterface:
    """Interface for Arduino communication"""
    
    def __init__(self, port, baudrate=9600):
        """
        Initialize the Arduino interface.
        
        Args:
            port (str): Serial port name
            baudrate (int, optional): Serial baudrate. Defaults to 9600.
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.coin_callback = None
        self.admin_callback = None
        self._thread = None
        
    def connect(self):
        """
        Connect to the Arduino device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to Arduino on port {self.port}")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Test connection
            self.serial.write(b'PING\n')
            response = self.serial.readline().decode('utf-8', errors='replace').strip()
            if not response.startswith('PONG'):
                logger.warning(f"Unexpected response from Arduino: {response}")
            
            self.running = True
            self._thread = threading.Thread(target=self._read_serial, daemon=True)
            self._thread.start()
            
            logger.info("Successfully connected to Arduino")
            return True
            
        except Exception as e:
            log_error("ArduinoInterface", f"Error connecting to Arduino: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from the Arduino device"""
        self.running = False
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except Exception as e:
                log_error("ArduinoInterface", f"Error closing serial connection: {e}")
                
    def _read_serial(self):
        """Read and process serial data from Arduino"""
        while self.running:
            try:
                if self.serial and self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='replace').strip()
                    logger.debug(f"Received from Arduino: {line}")
                    
                    # Handle different command types
                    if line.startswith('COIN:'):
                        try:
                            value = int(line.split(':')[1])
                            logger.info(f"Coin detected: {value}")
                            if self.coin_callback:
                                self.coin_callback(value)
                            else:
                                logger.warning("No coin callback registered")
                        except ValueError:
                            log_error("ArduinoInterface", f"Invalid coin value: {line}")
                    
                    elif line.startswith('ADMIN:'):
                        logger.info("Admin button pressed")
                        if self.admin_callback:
                            logger.info("Calling admin callback")
                            self.admin_callback()
                        else:
                            logger.warning("No admin callback registered")
                            
                    elif line.startswith('DEBUG:'):
                        logger.info(f"Arduino debug: {line[6:]}")
            
            except Exception as e:
                log_error("ArduinoInterface", f"Error reading from serial: {e}")
                time.sleep(1)
                
            time.sleep(0.1)
            
    def set_coin_callback(self, callback):
        """Set callback for coin detection"""
        self.coin_callback = callback
        
    def set_admin_callback(self, callback):
        """Set callback for admin button detection"""
        self.admin_callback = callback