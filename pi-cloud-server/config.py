"""
Pi Cloud Server - Configuration
"""

import os

# Database Configuration
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://picloud:password@localhost:5432/picloud_db'
)

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Server Configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# Storage Configuration (for future Raspberry Pi deployment)
STORAGE_PATH = os.environ.get('STORAGE_PATH', './storage')
