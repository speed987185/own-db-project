#!/usr/bin/env python3
"""
Pi Cloud Server - Main Application

A prototype local cloud storage server designed for Raspberry Pi.
Run with: python app.py
"""

from flask import Flask
from models import db
from routes import api
import config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
    # Initialize database
    db.init_app(app)
    
    # Register routes
    app.register_blueprint(api)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    ║         Pi Cloud Server (Prototype)       ║
    ╠═══════════════════════════════════════════╣
    ║  Local:  http://localhost:5000            ║
    ║                                           ║
    ║  Endpoints:                               ║
    ║    GET  /           - Status              ║
    ║    GET  /files      - List files          ║
    ║    POST /files      - Create file         ║
    ║    DELETE /files/id - Delete file         ║
    ║    GET  /stats      - Statistics          ║
    ╚═══════════════════════════════════════════╝
    """)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
