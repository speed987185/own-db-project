"""
Pi Cloud Server - Flask Application Factory
============================================

This module contains the Flask application factory function.
It creates and configures the Flask application.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions (without app)
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """
    Application factory function.
    
    Creates and configures the Flask application.
    
    Args:
        config_name: Configuration class name (default: based on FLASK_ENV)
    
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create storage directory if it doesn't exist
    ensure_storage_directory(app)
    
    # Create database tables
    with app.app_context():
        # Import models to ensure they are registered
        from app.models import file_model
        db.create_all()
        app.logger.info("Database tables created")
    
    # Log startup message
    app.logger.info(f"Pi Cloud Server started in {config_name} mode")
    
    return app


def setup_logging(app):
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
    """
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_file = app.config.get('LOG_FILE', None)
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    app.logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Clear existing handlers and add new ones
    app.logger.handlers = []
    app.logger.addHandler(console_handler)
    
    # File handler (if log file path is specified)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


def register_blueprints(app):
    """
    Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    # Import and register blueprints
    from app.routes.file_routes import file_bp
    
    # Register with /api prefix
    app.register_blueprint(file_bp, url_prefix='/api')
    
    app.logger.debug("Blueprints registered")


def ensure_storage_directory(app):
    """
    Ensure the storage directory exists.
    
    Args:
        app: Flask application instance
    """
    storage_path = app.config.get('STORAGE_PATH', './storage')
    
    if not os.path.isabs(storage_path):
        # Make relative paths relative to app root
        storage_path = os.path.join(app.root_path, '..', storage_path)
    
    storage_path = os.path.abspath(storage_path)
    
    if not os.path.exists(storage_path):
        os.makedirs(storage_path, exist_ok=True)
        app.logger.info(f"Created storage directory: {storage_path}")
    
    # Update config with absolute path
    app.config['STORAGE_PATH'] = storage_path
