"""
Coin Acceptor Interface for the PisoPrint Vendo system.
Handles communication with the coin acceptor hardware.
"""
import serial
import threading
import time
from tkinter import messagebox
from src.config import COIN_ACCEPTOR_PORT, COIN_ACCEPTOR_BAUDRATE, COIN_VALUES
from src.utils.logger import logger, log_error, log_payment

class CoinAcceptor:
    """
    Interface for the coin acceptor hardware.
    
    This class handles communication with a coin acceptor connected via serial port.
    It reads pulse counts from the acceptor and converts them to coin values.
    """
    
    def __init__(self, port=None, baudrate=None):
        """
        Initialize the coin acceptor interface.
        
        Args:
            port (str, optional): Serial port name. Defaults to config value.
            baudrate (int, optional): Serial baudrate. Defaults to config value.
        """
        self.port = port or COIN_ACCEPTOR_PORT
        self.baudrate = baudrate or COIN_ACCEPTOR_BAUDRATE
        self.serial = None
        self.running = False
        self.callback = None
        self._coin_thread = None
        self.connection_attempts = 0
        self.max_attempts = 3
        self.connected = False
        logger.info(f"CoinAcceptor initialized with port {self.port}, baudrate {self.baudrate}")
        
    def connect(self):
        """
        Connect to the coin acceptor device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check if already connected
            if self.connected and self.serial and self.serial.is_open:
                logger.info("CoinAcceptor already connected")
                return True
                
            # Limit connection attempts
            self.connection_attempts += 1
            if self.connection_attempts > self.max_attempts:
                error_msg = f"Maximum connection attempts ({self.max_attempts}) reached"
                log_error("CoinAcceptor", error_msg)
                messagebox.showerror("Hardware Error", 
                                  f"Failed to connect to coin acceptor after {self.max_attempts} attempts.\n"
                                  "Please check the connection and restart the application.")
                return False
                
            logger.info(f"Connecting to coin acceptor on port {self.port}")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Test if connection is working by reading a few bytes
            test_read = self.serial.read(10)
            logger.debug(f"Test read from coin acceptor: {test_read}")
            
            self.running = True
            self.connected = True
            self._coin_thread = threading.Thread(target=self._read_coins, daemon=True)
            self._coin_thread.start()
            
            logger.info("Successfully connected to coin acceptor")
            return True
            
        except serial.SerialException as e:
            error_msg = f"Serial error: {str(e)}"
            log_error("CoinAcceptor", error_msg)
            messagebox.showerror("Hardware Error", 
                               f"Could not connect to coin acceptor on port {self.port}.\n"
                               "Please check the connection.")
            return False
            
        except Exception as e:
            error_msg = f"Error connecting to coin acceptor: {str(e)}"
            log_error("CoinAcceptor", error_msg)
            messagebox.showerror("Hardware Error", 
                               f"Could not connect to coin acceptor: {str(e)}")
            return False
            
    def disconnect(self):
        """Disconnect from the coin acceptor device"""
        logger.info("Disconnecting from coin acceptor")
        self.running = False
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                logger.info("Serial connection closed")
            except Exception as e:
                log_error("CoinAcceptor", f"Error closing serial connection: {e}")
        self.connected = False
            
    def _read_coins(self):
        """
        Read coin pulses from the serial port.
        This method runs in a separate thread.
        """
        logger.info("Coin reading thread started")
        while self.running:
            if not self.serial or not self.serial.is_open:
                logger.warning("Serial connection lost, attempting to reconnect")
                try:
                    self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
                    logger.info("Reconnected to coin acceptor")
                except Exception as e:
                    log_error("CoinAcceptor", f"Failed to reconnect: {e}")
                    time.sleep(5)  # Wait before retrying
                    continue
            
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='replace').strip()
                    logger.debug(f"Received from coin acceptor: {line}")
                    
                    if line.startswith('COIN:'):
                        try:
                            pulse_count = int(line.split(':')[1])
                            coin_value = self._get_coin_value(pulse_count)
                            logger.info(f"Detected coin: {pulse_count} pulses = ₱{coin_value}")
                            
                            if coin_value > 0 and self.callback:
                                log_payment(coin_value)
                                self.callback(coin_value)
                        except ValueError as e:
                            log_error("CoinAcceptor", f"Invalid pulse count: {e}")
            except Exception as e:
                log_error("CoinAcceptor", f"Error reading from serial port: {e}")
                time.sleep(1)  # Prevent CPU spinning on error
                
            time.sleep(0.1)  # Short sleep to prevent CPU hogging
            
        logger.info("Coin reading thread stopped")
    
    def _get_coin_value(self, pulses):
        """
        Convert pulse count to coin value.
        
        Args:
            pulses (int): Number of pulses from coin acceptor
            
        Returns:
            int: Coin value in pesos
        """
        # Get value from config mapping, defaulting to 0 if not found
        value = COIN_VALUES.get(pulses, 0)
        if value == 0:
            logger.warning(f"Unknown pulse count: {pulses}")
        return value
            
    def set_callback(self, callback_function):
        """
        Set the callback function to be called when a coin is detected.
        
        Args:
            callback_function (callable): Function to call with coin value
        """
        if not callable(callback_function):
            log_error("CoinAcceptor", "Invalid callback function (not callable)")
            return
            
        logger.info("Coin callback function set")
        self.callback = callback_function
        
    def test_coin_insertion(self, value):
        """
        Simulate a coin insertion for testing purposes.
        
        Args:
            value (int): Coin value to simulate
            
        Returns:
            bool: True if callback was triggered, False otherwise
        """
        logger.info(f"Simulating coin insertion: ₱{value}")
        # Find the pulse count for this value
        pulse = None
        for p, v in COIN_VALUES.items():
            if v == value:
                pulse = p
                break
                
        if pulse is None:
            logger.warning(f"No matching pulse found for value ₱{value}")
            return False
            
        if self.callback:
            self.callback(value)
            return True
        return False