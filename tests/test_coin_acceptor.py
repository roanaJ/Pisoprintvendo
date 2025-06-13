"""
Tests for the CoinAcceptor class.
"""
import pytest
import serial
from unittest.mock import MagicMock, patch
from src.utils.coin_acceptor import CoinAcceptor
from src.config import COIN_VALUES

class MockSerial:
    """Mock serial port for testing"""
    def __init__(self, *args, **kwargs):
        self.is_open = True
        self.in_waiting = 0
        self._buffer = []
        
    def close(self):
        self.is_open = False
        
    def readline(self):
        if self._buffer:
            return self._buffer.pop(0)
        return b""
        
    def write(self, data):
        pass
        
    def simulate_coin(self, pulse_count):
        """Add a coin detection to the buffer"""
        self._buffer.append(f"COIN:{pulse_count}\n".encode())
        self.in_waiting = len(self._buffer[0])

@pytest.fixture
def mock_serial():
    """Create a mock serial port"""
    return MockSerial()

@pytest.fixture
def coin_acceptor(mock_serial):
    """Create a CoinAcceptor with mock serial port"""
    with patch('serial.Serial', return_value=mock_serial):
        acceptor = CoinAcceptor(port="MOCK", baudrate=9600)
        acceptor.connect()
        return acceptor, mock_serial

def test_initialization():
    """Test CoinAcceptor initialization"""
    acceptor = CoinAcceptor(port="COM9", baudrate=4800)
    assert acceptor.port == "COM9"
    assert acceptor.baudrate == 4800
    assert acceptor.serial is None
    assert acceptor.running is False
    assert acceptor.callback is None
    assert acceptor.connected is False

def test_connection(coin_acceptor):
    """Test successful connection"""
    acceptor, _ = coin_acceptor
    assert acceptor.connected is True
    assert acceptor.running is True
    assert acceptor._coin_thread is not None

def test_disconnect(coin_acceptor):
    """Test disconnection"""
    acceptor, mock_serial = coin_acceptor
    acceptor.disconnect()
    
    assert acceptor.running is False
    assert acceptor.connected is False
    assert mock_serial.is_open is False

def test_coin_detection(coin_acceptor):
    """Test coin detection and callback"""
    acceptor, mock_serial = coin_acceptor
    
    # Create a mock callback
    mock_callback = MagicMock()
    acceptor.set_callback(mock_callback)
    
    # Simulate coin detection events
    for pulse, expected_value in COIN_VALUES.items():
        mock_callback.reset_mock()
        mock_serial.simulate_coin(pulse)
        
        # Manually trigger the coin reading process
        acceptor._read_coins()
        
        # Verify callback was called with correct value
        mock_callback.assert_called_once_with(expected_value)

def test_invalid_pulse(coin_acceptor):
    """Test handling of invalid pulse count"""
    acceptor, mock_serial = coin_acceptor
    
    # Create a mock callback
    mock_callback = MagicMock()
    acceptor.set_callback(mock_callback)
    
    # Simulate invalid coin detection
    mock_serial.simulate_coin(99)  # Invalid pulse count
    
    # Manually trigger the coin reading process
    acceptor._read_coins()
    
    # Verify callback was not called
    mock_callback.assert_not_called()

def test_test_coin_insertion(coin_acceptor):
    """Test the coin insertion simulation feature"""
    acceptor, _ = coin_acceptor
    
    # Create a mock callback
    mock_callback = MagicMock()
    acceptor.set_callback(mock_callback)
    
    # Test valid coin simulation
    result = acceptor.test_coin_insertion(5)  # 5 peso coin
    assert result is True
    mock_callback.assert_called_once_with(5)
    
    # Test invalid coin value
    mock_callback.reset_mock()
    result = acceptor.test_coin_insertion(3)  # No 3 peso coin
    assert result is False
    mock_callback.assert_not_called()