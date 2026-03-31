"""
Pi Cloud Server - API Routes
"""

from flask import Blueprint, jsonify, request
from models import db, File

api = Blueprint('api', __name__)


@api.route('/')
def index():
    """Health check and welcome endpoint."""
    return jsonify({
        'name': 'Pi Cloud Server',
        'status': 'running',
        'version': '0.1.0-prototype',
        'description': 'Local cloud storage server for Raspberry Pi'
    })


@api.route('/files', methods=['GET'])
def list_files():
    """List all file metadata."""
    files = File.query.order_by(File.created_at.desc()).all()
    return jsonify({
        'success': True,
        'count': len(files),
        'files': [f.to_dict() for f in files]
    })


@api.route('/files', methods=['POST'])
def create_file():
    """Create new file metadata entry."""
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({
            'success': False,
            'error': 'filename is required'
        }), 400
    
    file = File(
        filename=data['filename'],
        size=data.get('size', 0),
        file_type=data.get('file_type'),
        description=data.get('description')
    )
    
    db.session.add(file)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'File metadata created',
        'file': file.to_dict()
    }), 201


@api.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """Get single file metadata."""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    return jsonify({
        'success': True,
        'file': file.to_dict()
    })


@api.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete file metadata."""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    db.session.delete(file)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'File deleted'
    })


@api.route('/stats', methods=['GET'])
def get_stats():
    """Get storage statistics."""
    total_files = File.query.count()
    total_size = db.session.query(db.func.sum(File.size)).scalar() or 0
    
    return jsonify({
        'success': True,
        'stats': {
            'total_files': total_files,
            'total_size_bytes': total_size
        }
    })
