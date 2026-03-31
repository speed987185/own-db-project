"""
Pi Cloud Server - Helper Functions
====================================

This module contains utility functions used throughout the application.
"""

import os
import uuid
import hashlib
import mimetypes

# Try to import python-magic for better MIME type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


def generate_unique_filename(original_filename):
    """
    Generate a unique filename to avoid collisions.
    
    Prepends a UUID to the original filename to ensure uniqueness.
    
    Args:
        original_filename: The original name of the file
        
    Returns:
        A unique filename string
        
    Example:
        >>> generate_unique_filename("document.pdf")
        "550e8400-e29b-41d4-a716-446655440000_document.pdf"
    """
    # Extract file extension
    _, extension = os.path.splitext(original_filename)
    
    # Generate UUID
    unique_id = str(uuid.uuid4())
    
    # Create unique filename
    unique_filename = f"{unique_id}_{original_filename}"
    
    return unique_filename


def calculate_file_checksum(filepath, algorithm='md5'):
    """
    Calculate the checksum of a file.
    
    Uses MD5 by default but supports other algorithms.
    
    Args:
        filepath: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha256', etc.)
        
    Returns:
        Hexadecimal checksum string
        
    Example:
        >>> calculate_file_checksum("/path/to/file.pdf")
        "d41d8cd98f00b204e9800998ecf8427e"
    """
    hash_func = hashlib.new(algorithm)
    
    # Read file in chunks to handle large files
    chunk_size = 8192  # 8KB chunks
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def validate_file_size(file_size, max_size):
    """
    Validate that file size is within allowed limit.
    
    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if file size is valid, False otherwise
        
    Example:
        >>> validate_file_size(1024, 1048576)  # 1KB, max 1MB
        True
    """
    return file_size <= max_size


def validate_file_extension(filename, allowed_extensions):
    """
    Validate that file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: String of allowed extensions (comma-separated)
                           or '*' for all extensions
        
    Returns:
        True if extension is allowed, False otherwise
        
    Example:
        >>> validate_file_extension("doc.pdf", "pdf,doc,txt")
        True
        >>> validate_file_extension("doc.exe", "pdf,doc,txt")
        False
    """
    # Allow all extensions if set to '*'
    if allowed_extensions == '*':
        return True
    
    # Get file extension (without the dot)
    _, extension = os.path.splitext(filename)
    extension = extension.lower().lstrip('.')
    
    # Parse allowed extensions
    if isinstance(allowed_extensions, str):
        allowed = [ext.strip().lower() for ext in allowed_extensions.split(',')]
    else:
        allowed = [ext.lower() for ext in allowed_extensions]
    
    return extension in allowed


def get_mime_type(filepath):
    """
    Detect the MIME type of a file.
    
    Uses python-magic if available (more accurate),
    otherwise falls back to mimetypes module.
    
    Args:
        filepath: Path to the file
        
    Returns:
        MIME type string (e.g., 'application/pdf')
        
    Example:
        >>> get_mime_type("/path/to/document.pdf")
        "application/pdf"
    """
    if HAS_MAGIC:
        try:
            # Use python-magic for accurate detection
            mime = magic.Magic(mime=True)
            return mime.from_file(filepath)
        except Exception:
            pass
    
    # Fall back to mimetypes module
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type or 'application/octet-stream'


def format_file_size(size_bytes):
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
        
    Example:
        >>> format_file_size(1536)
        "1.5 KB"
        >>> format_file_size(1073741824)
        "1.0 GB"
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    for unit in units:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def sanitize_filename(filename):
    """
    Sanitize a filename by removing potentially dangerous characters.
    
    This is a secondary sanitization after werkzeug's secure_filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename string
    """
    # Remove null bytes and other control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)
    
    # Remove or replace potentially problematic characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    
    return filename


def get_storage_usage(storage_path):
    """
    Calculate total storage usage for a directory.
    
    Args:
        storage_path: Path to the storage directory
        
    Returns:
        Dictionary with usage statistics
    """
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(storage_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
                file_count += 1
    
    return {
        'total_size': total_size,
        'total_size_human': format_file_size(total_size),
        'file_count': file_count
    }


def ensure_directory_exists(path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        True if directory exists or was created
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        return True
    return os.path.isdir(path)
