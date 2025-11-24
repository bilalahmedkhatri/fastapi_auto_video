"""
Passenger WSGI Bridge for FastAPI on cPanel
This file is required for deploying FastAPI to cPanel shared hosting.

Author: Auto Video Generator Team
Date: 2025-11-23
"""

import sys
import os

# Add application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import FastAPI app from main.py
from main import app

# Passenger expects 'application' variable
application = app
