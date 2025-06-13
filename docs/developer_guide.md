# PisoPrint Vendo Developer Guide

This guide provides information for developers who want to understand, modify, or extend the PisoPrint Vendo system.

## Architecture Overview

PisoPrint Vendo is built using Python and Tkinter for the user interface. The application follows a modular architecture with the following key components:

### Core Components

1. **Main Application (`PisoPrintSystem`)**: Central coordinator that manages the application state and screen navigation.

2. **Screens**: Individual UI screens implemented as separate classes. Each screen is responsible for its own layout and functionality.

3. **Utilities**: Hardware interfaces and helper functions:
   - `PDFPrinter`: Handles PDF printing using SumatraPDF
   - `CoinAcceptor`: Communicates with the coin acceptor hardware

4. **Configuration**: Centralized settings in `config.py`

5. **Logging**: System-wide logging functionality in `logger.py`

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Windows OS (for printing functionality)
- Required hardware for testing:
  - Coin acceptor (or simulation)
  - Printer

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/pisoprint-vendo.git
   cd pisoprint-vendo
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install SumatraPDF** (for printing functionality):
   Download from [SumatraPDF website](https://www.sumatrapdfreader.org/download-free-pdf-viewer)

## Project Structure

```
pisoprint-vendo/
├── assets/                # Images and icons
├── src/                   # Source code
│   ├── screens/           # UI screens
│   ├── utils/             # Utility modules
│   ├── __init__.py        # Package initialization
│   ├── pisoprint_app.py   # Main application class
│   ├── config.py          # Configuration settings
│   └── logger.py          # Logging functionality
├── tests/                 # Test modules
├── docs/                  # Documentation
├── logs/                  # Application logs (generated)
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── setup.py               # Package configuration
└── README.md              # Project overview
```

## Key Concepts

### Screen Navigation Flow

The application follows a linear screen flow:

1. Main Screen → Select "SEND PDF VIA BT"
2. Receive Screen → Select PDF file
3. Preview Screen → View document
4. Selection Screen → Choose number of copies
5. Payment Screen → Insert coins
6. Printing Screen → Print document and return to Main Screen

Each screen transition is handled by the `PisoPrintSystem` class through methods like `show_main_screen()`, `show_preview_screen()`, etc.

### State Management

The application state is maintained in the `PisoPrintSystem` class with properties such as:
- `current_pdf`: Path to the selected PDF file
- `pdf_document`: PyMuPDF document object
- `total_pages`: Number of pages in the document
- `copies`: Number of copies to print
- `total_amount`: Total cost to be paid
- `inserted_amount`: Amount paid so far

### Hardware Interfaces

#### Coin Acceptor

The coin acceptor interface (`CoinAcceptor` class) communicates with the hardware via serial port. It listens for coin insertion events and converts pulse counts to coin values. The callback pattern is used to notify the payment screen when coins are inserted.

#### PDF Printer

The `PDFPrinter` class handles PDF printing using SumatraPDF. It provides methods to:
- Print PDF documents with specified copy count
- Check printer status
- List available printers

## Extending the Application

### Adding a New Screen

1. Create a new screen class in the `src/screens` directory:

```python
# src/screens/new_screen.py
import tkinter as tk

class NewScreen:
    def __init__(self, app):
        self.app = app
        
        # Header
        header = tk.Frame(app.current_frame, bg="#248CCF", height=80)
        header.pack(fill="x")
        tk.Label(header, text="NEW SCREEN", 
                font=("Inter", 24, "bold"),
                bg="#248CCF", fg="white").pack(pady=20)
        
        # Content
        content = tk.Frame(app.current_frame, bg="white")
        content.pack(expand=True, fill="both")
        
        # Add your UI elements here
        
        # Navigation buttons
        button_frame = tk.Frame(app.current_frame, bg="white")
        button_frame.pack(side="bottom", fill="x")
        
        tk.Button(button_frame, text="BACK", 
                 command=app.show_main_screen).pack(side="left")
```

2. Add a navigation method to `PisoPrintSystem`:

```python
# src/pisoprint_app.py
def show_new_screen(self):
    self.clear_screen()
    from src.screens.new_screen import NewScreen
    NewScreen(self)
```

3. Add an import in the screens package:

```python
# src/screens/__init__.py
from .new_screen import NewScreen
```

### Adding a New Feature

To add a new feature, follow these guidelines:

1. **Identify the appropriate component**: Determine whether the feature belongs in a screen, utility, or the main application.

2. **Maintain separation of concerns**: Keep UI logic in screen classes and business logic in the main application or utility classes.

3. **Update configuration**: Add any new configurable parameters to `config.py`.

4. **Add proper logging**: Use the logging system to track feature usage and errors.

5. **Update documentation**: Document the new feature in this guide and the user manual.

## Testing

### Running Tests

The project uses pytest for testing. Run tests with:

```bash
python -m pytest
```

### Writing Tests

Create test files in the `tests` directory with the prefix `test_`. For example:

```python
# tests/test_pdf_printer.py
import pytest
from src.utils.pdf_printer import PDFPrinter

def test_printer_initialization():
    printer = PDFPrinter()
    assert printer is not None
    assert printer.printer_name is not None
```

## Debugging

### Development Mode

Run the application in windowed mode for easier debugging:

```bash
python main.py --windowed --debug
```

This enables:
- Windowed mode instead of fullscreen
- Detailed console logging
- Emergency exit via Escape key

### Logging

Use the logging system for debugging:

```python
from src.logger import logger

# Log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

Logs are saved in the `logs` directory with timestamps.

## Deployment

### Creating a Standalone Package

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create the executable:
   ```bash
   pyinstaller --onefile --windowed --icon=assets/image_ctu.ico main.py
   ```

3. Copy required assets to the `dist` directory:
   ```bash
   mkdir -p dist/assets
   cp -r assets/* dist/assets/
   ```

### Kiosk Mode Setup

For deployment as a kiosk, configure Windows to:

1. **Auto-start the application**:
   - Create a shortcut to the executable in the Windows Startup folder
   - Set the shortcut to run maximized

2. **Restrict system access**:
   - Use Windows Kiosk mode or a third-party kiosk software
   - Configure auto-login for the kiosk user account
   - Disable Windows hotkeys (Alt+Tab, Ctrl+Alt+Del, etc.)

3. **Hardware setup**:
   - Secure the touchscreen and PC to prevent tampering
   - Ensure proper ventilation for continuous operation
   - Use a surge protector for power

## Hardware Integration

### Coin Acceptor Setup

The system is designed to work with a pulse-based coin acceptor connected via USB-to-Serial adapter:

1. **Hardware wiring**:
   - Connect the coin acceptor to an Arduino or similar microcontroller
   - Program the Arduino to send pulse counts via serial:
     ```
     COIN:1  // 1 peso coin (1 pulse)
     COIN:2  // 5 peso coin (2 pulses)
     COIN:3  // 10 peso coin (3 pulses)
     COIN:4  // 20 peso coin (4 pulses)
     ```

2. **Serial protocol**:
   - Baudrate: 9600 bps
   - Data format: 8-N-1 (8 data bits, no parity, 1 stop bit)
   - Line ending: Newline (\n)

3. **Configuration**:
   - Update `COIN_ACCEPTOR_PORT` in `config.py` to match your system's COM port
   - Verify coin values in `COIN_VALUES` match your acceptor's pulse mapping

### Printer Configuration

The system uses the default system printer via SumatraPDF:

1. **Recommended printer settings**:
   - Paper size: A4
   - Default mode: Black and white (to save costs)
   - High-capacity paper tray

2. **SumatraPDF integration**:
   - Ensure SumatraPDF is installed in one of the paths listed in `SUMATRA_PATHS`
   - Test printing manually before deployment

## Maintenance and Troubleshooting

### Log Analysis

The application generates detailed logs in the `logs` directory. Key events to monitor:

- **Payment events**: Track successful payments and potential issues
- **Print jobs**: Monitor print successes and failures
- **Hardware errors**: Identify hardware connection issues

Example log analysis script:

```python
import os
import re
from collections import Counter

def analyze_logs(log_dir):
    payment_events = []
    print_events = []
    errors = []
    
    for filename in os.listdir(log_dir):
        if not filename.startswith('pisoprint_'):
            continue
            
        with open(os.path.join(log_dir, filename), 'r') as f:
            for line in f:
                if '[PAYMENT]' in line:
                    payment_events.append(line)
                if '[PRINT_JOB]' in line:
                    print_events.append(line)
                if 'ERROR' in line:
                    errors.append(line)
    
    print(f"Total payments: {len(payment_events)}")
    print(f"Total print jobs: {len(print_events)}")
    print(f"Total errors: {len(errors)}")
    
    # Analyze most common errors
    error_types = Counter()
    for error in errors:
        match = re.search(r'\[([^\]]+)\] (.+)', error)
        if match:
            component = match.group(1)
            error_types[component] += 1
    
    print("\nMost common error sources:")
    for component, count in error_types.most_common(5):
        print(f"- {component}: {count}")
```

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Coin acceptor not detecting coins | Serial connection issue | Check COM port setting and cable connections |
| | Arduino not responding | Restart the Arduino or check its power supply |
| Print job fails | Printer offline | Check printer connection and paper supply |
| | SumatraPDF not found | Verify SumatraPDF installation path in config |
| Application crashes | Exception in screen handling | Check the logs for the specific error and stack trace |
| | Hardware disconnection | Ensure all hardware is properly connected |
| Blank screen | Fullscreen mode issue | Press F12 to toggle fullscreen or restart the application |

## Future Enhancements

Consider these potential improvements for future versions:

1. **Additional Payment Methods**:
   - QR code payments (GCash, PayMaya)
   - NFC/RFID card support
   - Support for paper bills

2. **Enhanced PDF Handling**:
   - PDF editing (crop, rotate pages)
   - More printing options (page range, scaling)
   - Document scanning capability

3. **User Experience Improvements**:
   - User accounts with print history
   - Email receipt option
   - Multiple language support

4. **Administrative Features**:
   - Remote management dashboard
   - Usage statistics and reporting
   - Automated maintenance alerts

## Contributing

Contributions to the PisoPrint Vendo project are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add appropriate tests
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.