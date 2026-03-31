"""
Pi Cloud Server - Database Models
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class File(db.Model):
    """
    File metadata model.
    
    Stores information about files in the local cloud storage.
    Actual file content will be stored on filesystem (SSD on Raspberry Pi).
    """
    
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.BigInteger, default=0)
    file_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional fields for future expansion
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer)  # For future multi-user support
    
    def to_dict(self):
        """Convert model to dictionary for JSON response."""
        return {
            'id': self.id,
            'filename': self.filename,
            'size': self.size,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'description': self.description
        }
