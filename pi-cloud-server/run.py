#!/usr/bin/env python3
"""
Pi Cloud Server - Application Entry Point
==========================================

This is the main entry point for the Pi Cloud Server application.
Run this file to start the Flask development server.

Usage:
    python run.py

For production, use Gunicorn:
    gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
"""

import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    Pi Cloud Server                           ║
╠══════════════════════════════════════════════════════════════╣
║  Local URL:    http://localhost:{port}                         ║
║  Network URL:  http://<your-ip>:{port}                         ║
║                                                              ║
║  API Endpoints:                                              ║
║    GET  /api/health          - Health check                  ║
║    POST /api/files/upload    - Upload a file                 ║
║    GET  /api/files           - List all files                ║
║    GET  /api/files/<id>      - Get file info                 ║
║    GET  /api/files/<id>/download - Download file             ║
║    DELETE /api/files/<id>    - Delete a file                 ║
║    GET  /api/stats           - Storage statistics            ║
║                                                              ║
║  Press Ctrl+C to stop the server                             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run the development server
    app.run(
        host=host,
        port=port,
        debug=debug
    )
