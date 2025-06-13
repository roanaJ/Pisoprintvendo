# PisoPrint Vendo

A self-service PDF printing kiosk system with integrated coin payment functionality.

## Overview

PisoPrint Vendo is a Python-based kiosk application that allows users to print PDF documents through a user-friendly interface. The system includes a coin acceptor for payment processing and is designed to run on a touchscreen device in fullscreen kiosk mode.

## Features

- PDF file selection and preview
- Variable copy count selection
- Automatic pricing calculation based on page count and color options
- Coin acceptor integration with support for ₱1, ₱5, ₱10, and ₱20 coins
- Simplified printing workflow
- User-friendly kiosk interface
- Detailed guides and information screens

## System Requirements

- Python 3.8 or higher
- Windows OS (for printing functionality via SumatraPDF)
- Hardware:
  - Touchscreen display
  - Coin acceptor (connected via serial port)
  - Printer (configured as system default)
  - Computer with Bluetooth capability (for file reception)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pisoprint-vendo.git
cd pisoprint-vendo
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the required dependencies

```bash
pip install -e .
```

### 4. Install SumatraPDF

Download and install [SumatraPDF](https://www.sumatrapdfreader.org/download-free-pdf-viewer) with default settings.

### 5. Configure hardware

- Connect the coin acceptor to the appropriate COM port (default: COM4)
- Ensure the printer is configured as the default system printer

## Running the Application

```bash
python main.py
```

The application will start in fullscreen kiosk mode.

## Hardware Setup

### Coin Acceptor

The coin acceptor should be connected via serial port (default: COM4) and configured to send pulse counts:
- 1 pulse = ₱1 coin
- 2 pulses = ₱5 coin
- 3 pulses = ₱10 coin
- 4 pulses = ₱20 coin

### Printer

The system uses the default system printer. Ensure it is properly configured with A4 paper loaded.

## Workflow

1. User selects "SEND PDF VIA BT" on the main screen
2. User selects a PDF file to print
3. System displays a preview of the PDF
4. User selects the desired number of copies
5. System calculates the total cost
6. User inserts coins to pay
7. System processes payment and prints the document

## Pricing

- Black & White: ₱3.00 per page
- Colored: ₱5.00 per page

## Project Structure

```
pisoprint-vendo/
├── assets/
│   └── image_ctu.ico/png
├── src/
│   ├── screens/
│   │   ├── main_screen.py
│   │   ├── guide_screen.py
│   │   ├── receive_screen.py
│   │   ├── preview_screen.py
│   │   ├── selection_screen.py
│   │   ├── payment_screen.py
│   │   └── printing_screen.py
│   ├── utils/
│   │   ├── coin_acceptor.py
│   │   └── pdf_printer.py
│   └── pisoprint_app.py
├── main.py
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Adding New Screens

To create a new screen, follow these steps:

1. Create a new Python file in the `src/screens/` directory
2. Create a class that takes the app instance as an argument
3. Add a method to `PisoPrintSystem` to show the new screen

Example:

```python
# src/screens/new_screen.py
import tkinter as tk

class NewScreen:
    def __init__(self, app):
        self.app = app
        # Screen UI implementation
        
# src/pisoprint_app.py
def show_new_screen(self):
    self.clear_screen()
    NewScreen(self)
```

## Troubleshooting

### Coin Acceptor Not Working

- Check that the coin acceptor is connected to the correct COM port
- Ensure the baudrate is set correctly (default: 9600)
- Verify that the Arduino firmware is sending the correct pulse counts

### Printing Issues

- Ensure SumatraPDF is installed and in the correct path
- Check that the printer is set as the default system printer
- Verify that the printer has paper and is ready to print

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For assistance, please contact:
- Email: support@pisoprint.com
- Phone: (032) 123-4567