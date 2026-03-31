"""
Pi Cloud Server - File Routes
==============================

This module contains all API routes for file operations.
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename

from app import db
from app.models.file_model import FileMetadata
from app.utils.helpers import (
    generate_unique_filename,
    calculate_file_checksum,
    validate_file_size,
    validate_file_extension,
    get_mime_type,
    format_file_size
)

# Create blueprint for file routes
file_bp = Blueprint('files', __name__)


# =============================================================================
# Health Check Route
# =============================================================================

@file_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns server status and timestamp.
    Used for monitoring and checking if the server is running.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Pi Cloud Server is running',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


# =============================================================================
# File Upload Route
# =============================================================================

@file_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the server.
    
    Accepts multipart/form-data with a 'file' field.
    Stores the file on disk and saves metadata to database.
    
    Returns:
        JSON response with file metadata or error
    """
    # Check if file was provided
    if 'file' not in request.files:
        current_app.logger.warning("Upload attempt without file")
        return jsonify({
            'success': False,
            'error': 'No file provided',
            'message': 'Please include a file in your request'
        }), 400
    
    file = request.files['file']
    
    # Check if filename is empty (user didn't select a file)
    if file.filename == '':
        current_app.logger.warning("Upload attempt with empty filename")
        return jsonify({
            'success': False,
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400
    
    # Get original filename and secure it
    original_filename = file.filename
    safe_filename = secure_filename(original_filename)
    
    if not safe_filename:
        return jsonify({
            'success': False,
            'error': 'Invalid filename',
            'message': 'The filename contains invalid characters'
        }), 400
    
    # Validate file extension
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', '*')
    if not validate_file_extension(safe_filename, allowed_extensions):
        return jsonify({
            'success': False,
            'error': 'File type not allowed',
            'message': f'This file type is not allowed'
        }), 400
    
    # Read file content to check size
    file_content = file.read()
    file_size = len(file_content)
    file.seek(0)  # Reset file pointer
    
    # Validate file size
    max_size = current_app.config.get('MAX_FILE_SIZE', 100 * 1024 * 1024)
    if not validate_file_size(file_size, max_size):
        return jsonify({
            'success': False,
            'error': 'File too large',
            'message': f'Maximum file size is {format_file_size(max_size)}'
        }), 400
    
    try:
        # Generate unique filename to avoid collisions
        unique_filename = generate_unique_filename(safe_filename)
        
        # Get storage path
        storage_path = current_app.config['STORAGE_PATH']
        filepath = os.path.join(storage_path, unique_filename)
        
        # Save file to disk
        file.save(filepath)
        current_app.logger.info(f"File saved to: {filepath}")
        
        # Calculate checksum
        checksum = calculate_file_checksum(filepath)
        
        # Detect MIME type
        mimetype = get_mime_type(filepath) or file.content_type
        
        # Get optional description
        description = request.form.get('description', None)
        
        # Create database record
        file_record = FileMetadata(
            filename=unique_filename,
            original_filename=original_filename,
            filepath=filepath,
            size=file_size,
            mimetype=mimetype,
            checksum=checksum,
            description=description
        )
        file_record.save()
        
        current_app.logger.info(f"File uploaded successfully: {original_filename} (ID: {file_record.id})")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'data': file_record.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading file: {str(e)}")
        
        # Clean up file if it was saved
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading the file'
        }), 500


# =============================================================================
# List Files Route
# =============================================================================

@file_bp.route('/files', methods=['GET'])
def list_files():
    """
    List all uploaded files with pagination.
    
    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
    
    Returns:
        JSON response with list of files and pagination info
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination parameters
        page = max(1, page)
        per_page = min(max(1, per_page), 100)  # Max 100 items per page
        
        # Get paginated files
        pagination = FileMetadata.get_all(page=page, per_page=per_page)
        
        # Build response
        files = [f.to_dict() for f in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'files': files,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list files',
            'message': 'An error occurred while retrieving files'
        }), 500


# =============================================================================
# Get Single File Info Route
# =============================================================================

@file_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file_info(file_id):
    """
    Get metadata for a specific file.
    
    Args:
        file_id: ID of the file to retrieve
    
    Returns:
        JSON response with file metadata
    """
    try:
        file_record = FileMetadata.get_by_id(file_id)
        
        if not file_record:
            return jsonify({
                'success': False,
                'error': 'File not found',
                'message': f'No file found with ID {file_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': file_record.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting file info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get file info',
            'message': 'An error occurred while retrieving file information'
        }), 500


# =============================================================================
# Download File Route
# =============================================================================

@file_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """
    Download a file from the server.
    
    Args:
        file_id: ID of the file to download
    
    Returns:
        File as attachment or JSON error
    """
    try:
        file_record = FileMetadata.get_by_id(file_id)
        
        if not file_record:
            return jsonify({
                'success': False,
                'error': 'File not found',
                'message': f'No file found with ID {file_id}'
            }), 404
        
        # Check if file exists on disk
        if not os.path.exists(file_record.filepath):
            current_app.logger.error(f"File missing from disk: {file_record.filepath}")
            return jsonify({
                'success': False,
                'error': 'File not found on disk',
                'message': 'The file exists in database but not on disk'
            }), 404
        
        current_app.logger.info(f"File downloaded: {file_record.original_filename} (ID: {file_id})")
        
        # Send file as attachment
        return send_file(
            file_record.filepath,
            as_attachment=True,
            download_name=file_record.original_filename,
            mimetype=file_record.mimetype
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Download failed',
            'message': 'An error occurred while downloading the file'
        }), 500


# =============================================================================
# Delete File Route
# =============================================================================

@file_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    Delete a file from the server.
    
    Removes both the file from disk and the metadata from database.
    
    Args:
        file_id: ID of the file to delete
    
    Returns:
        JSON response confirming deletion
    """
    try:
        file_record = FileMetadata.get_by_id(file_id)
        
        if not file_record:
            return jsonify({
                'success': False,
                'error': 'File not found',
                'message': f'No file found with ID {file_id}'
            }), 404
        
        filepath = file_record.filepath
        original_filename = file_record.original_filename
        
        # Delete from database first
        file_record.delete()
        
        # Delete from disk
        if os.path.exists(filepath):
            os.remove(filepath)
            current_app.logger.info(f"File deleted from disk: {filepath}")
        else:
            current_app.logger.warning(f"File not found on disk during deletion: {filepath}")
        
        current_app.logger.info(f"File deleted: {original_filename} (ID: {file_id})")
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Delete failed',
            'message': 'An error occurred while deleting the file'
        }), 500


# =============================================================================
# Storage Statistics Route
# =============================================================================

@file_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get storage statistics.
    
    Returns total file count, total size, and storage path.
    
    Returns:
        JSON response with storage statistics
    """
    try:
        total_files = FileMetadata.get_count()
        total_size = FileMetadata.get_total_size()
        
        return jsonify({
            'success': True,
            'data': {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_human': format_file_size(total_size),
                'storage_path': current_app.config['STORAGE_PATH']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'message': 'An error occurred while retrieving statistics'
        }), 500


# =============================================================================
# Error Handlers
# =============================================================================

@file_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error (413)."""
    max_size = current_app.config.get('MAX_FILE_SIZE', 100 * 1024 * 1024)
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': f'Maximum file size is {format_file_size(max_size)}'
    }), 413


@file_bp.errorhandler(404)
def not_found(error):
    """Handle not found error (404)."""
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404


@file_bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error (500)."""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
