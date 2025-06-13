#!/usr/bin/env python3
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now import the app
from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)