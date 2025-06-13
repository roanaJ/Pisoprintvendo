"""
Hardware sensor interface for PisoPrint Vendo monitoring system.
Interfaces with Arduino Uno R3 via serial connection for ink levels and paper weight sensing.
"""
import time
import threading
import logging
import json
import os
import serial
import re
from src.utils.sqlite_manager import SQLiteManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("sensors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pisoprint_sensors")

class PisoPrintSensors:
    """Interface for PisoPrint Vendo hardware sensors using Arduino Uno"""
    
    def __init__(self, db_manager, config_file=None):
        """
        Initialize the sensor interface.
        
        Args:
            db_manager: Database manager instance for storing readings
            config_file (str, optional): Path to config file
        """
        self.db_manager = db_manager
        self.running = False
        self.config = self.load_config(config_file)
        
        # Arduino serial connection parameters
        self.arduino_port = self.config.get('arduino_port', 'COM4')
        self.arduino_baudrate = self.config.get('arduino_baudrate', 9600)
        self.arduino = None
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # Paper sensor calibration values for Epson L120 (50 sheets capacity)
        self.paper_calibration = {
            'reference_unit': -467,  # Default calibration value
            'offset': 0,             # Default offset
            'empty_weight': 50,      # Weight of empty paper tray in grams
            'full_weight': 350,      # Weight of full paper tray (50 sheets) in grams
            'sheet_weight': 5,       # Weight of single sheet in grams (A4 80gsm)
        }
        
        # Update calibration from config if available
        if 'paper_calibration' in self.config:
            self.paper_calibration.update(self.config['paper_calibration'])
        
        # Current readings
        self.current_weight = 0
        self.paper_count = 0
        self.paper_capacity = 50  # Epson L120 paper capacity
        self.ink_levels = {
            'black': 0,
            'cyan': 0,
            'magenta': 0,
            'yellow': 0
        }
        
        # Thread for continuous monitoring
        self.monitor_thread = None
        
        # Try to initialize Arduino connection
        try:
            self.initialize_arduino()
        except Exception as e:
            logger.error(f"Failed to initialize Arduino: {e}")
            # Fall back to simulation mode
            self.load_sample_data()
    
    def load_config(self, config_file):
        """
        Load configuration from file.
        
        Args:
            config_file (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            'arduino_port': 'COM4',
            'arduino_baudrate': 9600,
            'paper_calibration': {
                'reference_unit': -467,
                'offset': 0,
                'empty_weight': 50,
                'full_weight': 350,
                'sheet_weight': 5,
            },
            'monitoring': {
                'interval': 10,  # Seconds between readings
                'ink_change_rate': 0.1,  # Ink consumption rate per page
            }
        }
        
        if not config_file or not os.path.exists(config_file):
            logger.info("Config file not found, using defaults")
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing values
                merged_config = default_config.copy()
                for key, value in config.items():
                    if isinstance(value, dict) and key in merged_config:
                        merged_config[key].update(value)
                    else:
                        merged_config[key] = value
                return merged_config
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return default_config
    
    def load_sample_data(self):
        """Load sample sensor data for simulation mode"""
        # Get paper capacity from database or use default
        paper_capacity = int(self.db_manager.get_setting('paper_capacity', self.paper_capacity))
        self.paper_capacity = paper_capacity
        
        # Load paper level from database
        paper_level = int(self.db_manager.get_setting('paper_level', 40))
        
        # Calculate simulated paper weight
        paper_weight_range = self.paper_calibration['full_weight'] - self.paper_calibration['empty_weight']
        self.current_weight = self.paper_calibration['empty_weight'] + (paper_weight_range * (paper_level / paper_capacity))
        self.paper_count = paper_level
        
        # Load ink levels from database or use defaults
        for color in self.ink_levels:
            level = float(self.db_manager.get_setting(f'ink_level_{color}', 0))
            if level == 0:  # If not set, use random starting values
                import random
                level = random.uniform(60, 100)
            self.ink_levels[color] = level
        
        logger.info("Loaded sample data in simulation mode")
    
    def initialize_arduino(self):
        """Initialize connection to Arduino over serial port"""
        try:
            # Try to connect to Arduino
            self.arduino = serial.Serial(self.arduino_port, self.arduino_baudrate, timeout=2)
            time.sleep(2)  # Wait for Arduino to reset after connection
            
            # Send a test command and wait for response
            self.arduino.write(b'TEST\n')
            response = self.arduino.readline().decode('utf-8').strip()
            
            if 'READY' in response:
                logger.info(f"Arduino connected successfully on {self.arduino_port}")
                self.initialized = True
                return True
            else:
                logger.error(f"Arduino not responding correctly. Got: {response}")
                self.arduino.close()
                self.arduino = None
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Arduino: {e}")
            if self.arduino:
                self.arduino.close()
            self.arduino = None
            return False
    
    def reconnect_arduino(self):
        """Attempt to reconnect to Arduino if connection is lost"""
        self.connection_attempts += 1
        
        if self.connection_attempts > self.max_connection_attempts:
            logger.error(f"Max reconnection attempts ({self.max_connection_attempts}) reached. Switching to simulation mode.")
            self.load_sample_data()
            return False
            
        logger.info(f"Attempting to reconnect to Arduino (attempt {self.connection_attempts}/{self.max_connection_attempts})")
        
        if self.arduino:
            try:
                self.arduino.close()
            except:
                pass
                
        time.sleep(2)  # Wait before attempting reconnection
        return self.initialize_arduino()
    
    def send_command(self, command):
        """
        Send command to Arduino and get response.
        
        Args:
            command (str): Command to send
            
        Returns:
            str: Response from Arduino, or None if error
        """
        if not self.arduino:
            # Try to reconnect
            if not self.reconnect_arduino():
                return None
        
        try:
            # Clear any pending data
            self.arduino.reset_input_buffer()
            
            # Send command
            self.arduino.write(f"{command}\n".encode('utf-8'))
            
            # Wait for response
            response = self.arduino.readline().decode('utf-8').strip()
            return response
            
        except Exception as e:
            logger.error(f"Error sending command to Arduino: {e}")
            # Try to reconnect on error
            self.reconnect_arduino()
            return None
    
    def read_paper_weight(self):
        """
        Read weight from HX711 load cell via Arduino.
        
        Returns:
            float: Weight in grams
        """
        if not self.arduino:
            # In simulation mode, return current simulated weight
            return self.current_weight
        
        try:
            # Send command to Arduino to read weight
            response = self.send_command("READ_WEIGHT")
            
            if response and response.startswith("WEIGHT:"):
                # Parse weight value from response
                weight_str = response.split(':')[1].strip()
                try:
                    weight = float(weight_str)
                    # Apply offset and return weight in grams
                    weight = weight + self.paper_calibration['offset']
                    return max(0, weight)  # Ensure non-negative
                except ValueError:
                    logger.error(f"Invalid weight value from Arduino: {weight_str}")
            
            logger.warning(f"Unexpected weight response from Arduino: {response}")
            return self.current_weight  # Return last known value on error
            
        except Exception as e:
            logger.error(f"Error reading paper weight: {e}")
            return self.current_weight  # Return last known value on error
    
    def read_ink_level(self, color):
        """
        Read ink level from non-contact water sensor via Arduino.
        These sensors will return binary values (LOW/HIGH) indicating if ink is below threshold.
        
        Args:
            color (str): Ink color ('black', 'cyan', 'magenta', 'yellow')
            
        Returns:
            float: Ink level as percentage (0-100)
        """
        if not self.arduino:
            # In simulation mode, return current simulated level
            return self.ink_levels.get(color, 0)
        
        try:
            # Send command to Arduino to read specific ink sensor
            response = self.send_command(f"READ_INK_{color.upper()}")
            
            if response:
                # Extract the sensor reading (binary LOW/HIGH)
                if response.startswith(f"INK_{color.upper()}:"):
                    status = response.split(':')[1].strip()
                    
                    # Get current level from database
                    current_level = float(self.db_manager.get_setting(f'ink_level_{color}', 60))
                    
                    # Update based on sensor reading
                    # LOW means resistance is low, which means ink is present (not below threshold)
                    # HIGH means resistance is high, which means ink is below threshold (low level)
                    if status == "HIGH":
                        # Ink below threshold - reduce level if it's not already low
                        if current_level > 20:
                            current_level = 15  # Set to a low level
                        else:
                            # Already low, decrease slightly
                            current_level -= 0.5
                    else:  # LOW reading
                        # Ink above threshold - keep or slightly increase if it was low
                        if current_level < 20:
                            current_level = 60  # Reset to reasonable level after refill
                        else:
                            # Normal level, may fluctuate slightly
                            import random
                            current_level += random.uniform(-0.3, 0.1)
                    
                    # Ensure level stays within 0-100%
                    current_level = max(0, min(current_level, 100))
                    
                    return current_level
            
            logger.warning(f"Unexpected ink level response from Arduino: {response}")
            return self.ink_levels.get(color, 0)  # Return last known value on error
            
        except Exception as e:
            logger.error(f"Error reading {color} ink level: {e}")
            return self.ink_levels.get(color, 0)  # Return last known value on error
    
    def update_all_sensors(self):
        """Read all sensors and update current values"""
        # Read paper weight
        self.current_weight = self.read_paper_weight()
        
        # Calculate paper count
        self.paper_count = self.calculate_paper_count(self.current_weight)
        
        # Read ink levels
        for color in self.ink_levels.keys():
            self.ink_levels[color] = self.read_ink_level(color)
        
        # Update database with new readings
        self.update_database()
        
        return {
            'paper_weight': round(self.current_weight, 1),
            'paper_count': self.paper_count,
            'ink_levels': {k: round(v, 1) for k, v in self.ink_levels.items()}
        }
    
    def calculate_paper_count(self, weight):
        """
        Calculate paper count from weight.
        
        Args:
            weight (float): Paper weight in grams
            
        Returns:
            int: Estimated paper count
        """
        # Get weight range and capacity
        empty_weight = self.paper_calibration['empty_weight']
        full_weight = self.paper_calibration['full_weight']
        
        # If weight is at or below empty weight, there's no paper
        if weight <= empty_weight:
            return 0
        
        # If weight is at or above full weight, it's full capacity
        if weight >= full_weight:
            return self.paper_capacity
            
        # Calculate paper count based on weight range
        weight_range = full_weight - empty_weight
        weight_percentage = (weight - empty_weight) / weight_range
        paper_count = int(weight_percentage * self.paper_capacity)
        
        return paper_count
    
    def update_database(self):
        """Update database with current sensor readings"""
        # Update paper level
        self.db_manager.set_setting('paper_level', self.paper_count)
        self.db_manager.set_setting('paper_capacity', self.paper_capacity)
        
        # Update ink levels
        for color, level in self.ink_levels.items():
            self.db_manager.set_setting(f'ink_level_{color}', level)
        
        # Log low levels as warnings
        paper_percentage = (self.paper_count / self.paper_capacity) * 100
        
        if paper_percentage < 20:
            self.db_manager.log_system_stat('paper_low', self.paper_count, 
                                          f"Low paper level: {self.paper_count} sheets ({paper_percentage:.1f}%)")
        
        for color, level in self.ink_levels.items():
            if level < 20:
                self.db_manager.log_system_stat('ink_low', level, 
                                              f"Low {color} ink level: {level:.1f}%")
    
    def start_monitoring(self, interval=10):
        """
        Start continuous monitoring in a separate thread.
        
        Args:
            interval (int): Seconds between readings
        """
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started sensor monitoring (interval: {interval}s)")
    
    def _monitor_loop(self, interval):
        """
        Continuous monitoring loop.
        
        Args:
            interval (int): Seconds between readings
        """
        while self.running:
            try:
                self.update_all_sensors()
                logger.debug(f"Sensor readings - Paper: {self.paper_count} sheets ({self.current_weight:.1f}g), " + 
                           f"Ink: {', '.join([f'{k}: {v:.1f}%' for k, v in self.ink_levels.items()])}")
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Sleep for the specified interval
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        logger.info("Stopped sensor monitoring")
    
    def calibrate_paper_sensor(self, known_weight=None, known_sheets=None):
        """
        Calibrate the paper weight sensor.
        
        Args:
            known_weight (float, optional): Known weight in grams
            known_sheets (int, optional): Known number of sheets
            
        Returns:
            dict: Calibration results
        """
        if not self.arduino:
            logger.warning("Cannot calibrate in simulation mode")
            return {"success": False, "error": "Cannot calibrate in simulation mode"}
        
        try:
            if known_weight is not None:
                # Calibrate with known weight
                # Send calibration command to Arduino
                response = self.send_command(f"CALIBRATE_WEIGHT:{known_weight}")
                
                if response and response.startswith("CALIBRATION_FACTOR:"):
                    # Parse reference unit (calibration factor)
                    reference_unit = float(response.split(':')[1].strip())
                    
                    # Update calibration values
                    self.paper_calibration['reference_unit'] = reference_unit
                    
                    logger.info(f"Calibrated with known weight: {known_weight}g, reference_unit: {reference_unit}")
                    
                    return {
                        "success": True,
                        "reference_unit": reference_unit
                    }
                else:
                    logger.error(f"Unexpected calibration response: {response}")
                    return {"success": False, "error": f"Unexpected response: {response}"}
                
            elif known_sheets is not None:
                # Read current weight
                self.current_weight = self.read_paper_weight()
                
                # Update calibration based on known sheets
                if known_sheets == 0:
                    # Empty tray calibration
                    self.paper_calibration['empty_weight'] = self.current_weight
                    logger.info(f"Calibrated empty tray weight: {self.current_weight}g")
                    
                    # Send calibration to Arduino
                    self.send_command(f"SET_EMPTY_WEIGHT:{self.current_weight}")
                    
                    return {
                        "success": True,
                        "empty_weight": self.current_weight
                    }
                    
                elif known_sheets == self.paper_capacity:
                    # Full tray calibration
                    self.paper_calibration['full_weight'] = self.current_weight
                    logger.info(f"Calibrated full tray weight ({self.paper_capacity} sheets): {self.current_weight}g")
                    
                    # Send calibration to Arduino
                    self.send_command(f"SET_FULL_WEIGHT:{self.current_weight}")
                    
                    # Calculate sheet weight
                    weight_range = self.paper_calibration['full_weight'] - self.paper_calibration['empty_weight']
                    sheet_weight = weight_range / self.paper_capacity
                    self.paper_calibration['sheet_weight'] = sheet_weight
                    
                    return {
                        "success": True,
                        "full_weight": self.current_weight,
                        "sheet_weight": sheet_weight
                    }
                
                else:
                    # Calibration with partial stack
                    weight_without_paper = self.paper_calibration['empty_weight']
                    paper_weight = self.current_weight - weight_without_paper
                    sheet_weight = paper_weight / known_sheets
                    
                    # Update calibration
                    self.paper_calibration['sheet_weight'] = sheet_weight
                    self.paper_calibration['full_weight'] = weight_without_paper + (sheet_weight * self.paper_capacity)
                    
                    logger.info(f"Calibrated with {known_sheets} sheets: sheet_weight: {sheet_weight}g")
                    
                    return {
                        "success": True,
                        "sheet_weight": sheet_weight,
                        "full_weight": self.paper_calibration['full_weight']
                    }
            else:
                return {"success": False, "error": "No calibration parameters provided"}
                
        except Exception as e:
            logger.error(f"Calibration error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sensor_data(self):
        """
        Get current sensor readings as a dictionary.
        
        Returns:
            dict: Current sensor data
        """
        return {
            'paper_level': self.paper_count,
            'paper_capacity': self.paper_capacity,
            'paper_percentage': round((self.paper_count / self.paper_capacity) * 100, 1) if self.paper_capacity > 0 else 0,
            'paper_weight': round(self.current_weight, 1),
            'ink_levels': {k: round(v, 1) for k, v in self.ink_levels.items()}
        }
    
    def shutdown(self):
        """Shutdown and cleanup resources"""
        self.stop_monitoring()
        
        if self.arduino:
            try:
                self.arduino.close()
                logger.info("Arduino connection closed")
            except Exception as e:
                logger.error(f"Error closing Arduino connection: {e}")
                
        logger.info("Sensor interface shutdown complete")