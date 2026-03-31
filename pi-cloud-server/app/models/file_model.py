"""
Pi Cloud Server - File Metadata Model
======================================

This module contains the SQLAlchemy model for file metadata.
"""

from datetime import datetime
from app import db


class FileMetadata(db.Model):
    """
    SQLAlchemy model for storing file metadata.
    
    This model stores information about uploaded files.
    The actual file content is stored on the filesystem,
    while this model stores metadata for easy querying.
    
    Attributes:
        id: Unique identifier for the file
        filename: Name used to store file on disk (may include UUID)
        original_filename: Original name of the uploaded file
        filepath: Full path to the file on disk
        size: File size in bytes
        mimetype: MIME type of the file
        checksum: MD5 hash of the file for integrity checking
        upload_date: Timestamp when file was uploaded
        updated_at: Timestamp when record was last updated
        description: Optional description of the file
    """
    
    __tablename__ = 'files'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # File identification
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False, unique=True)
    
    # File metadata
    size = db.Column(db.BigInteger, nullable=False, default=0)
    mimetype = db.Column(db.String(128), nullable=True)
    checksum = db.Column(db.String(64), nullable=True)
    
    # Timestamps
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Optional metadata
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        """String representation of the model."""
        return f'<FileMetadata {self.id}: {self.original_filename}>'
    
    def to_dict(self):
        """
        Convert model to dictionary for JSON serialization.
        
        Returns:
            Dictionary containing file metadata
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'size': self.size,
            'size_human': self.size_human,
            'mimetype': self.mimetype,
            'checksum': self.checksum,
            'upload_date': self.upload_date.isoformat() + 'Z' if self.upload_date else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'description': self.description
        }
    
    @property
    def size_human(self):
        """
        Return human-readable file size.
        
        Returns:
            String representation of file size (e.g., "1.5 MB")
        """
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @classmethod
    def get_by_id(cls, file_id):
        """
        Get file by ID.
        
        Args:
            file_id: ID of the file to retrieve
            
        Returns:
            FileMetadata instance or None if not found
        """
        return cls.query.get(file_id)
    
    @classmethod
    def get_all(cls, page=1, per_page=20):
        """
        Get paginated list of all files.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 20)
            
        Returns:
            Pagination object containing files
        """
        return cls.query.order_by(cls.upload_date.desc()).paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
    
    @classmethod
    def get_total_size(cls):
        """
        Get total size of all stored files.
        
        Returns:
            Total size in bytes
        """
        result = db.session.query(db.func.sum(cls.size)).scalar()
        return result or 0
    
    @classmethod
    def get_count(cls):
        """
        Get total number of files.
        
        Returns:
            Total file count
        """
        return cls.query.count()
    
    def save(self):
        """Save the current instance to database."""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete the current instance from database."""
        db.session.delete(self)
        db.session.commit()
