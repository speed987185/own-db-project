# Pi Cloud Server - Architecture Documentation

## Overview

Pi Cloud Server is a lightweight, self-hosted cloud storage solution designed for Raspberry Pi. This document explains the system architecture, design decisions, and component interactions.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT DEVICES                                  │
│         (Laptop, Phone, Tablet, IoT Device, CLI tools like curl)            │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      │ HTTP/HTTPS (REST API)
                                      │
                    ┌─────────────────▼─────────────────┐
                    │         NETWORK LAYER             │
                    │  ┌─────────────────────────────┐  │
                    │  │   Local WiFi (LAN)          │  │
                    │  │   192.168.x.x:5000          │  │
                    │  └─────────────────────────────┘  │
                    │  ┌─────────────────────────────┐  │
                    │  │   ngrok (Optional)          │  │
                    │  │   https://xxx.ngrok.io      │  │
                    │  └─────────────────────────────┘  │
                    └─────────────────┬─────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                            RASPBERRY PI                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         APPLICATION LAYER                              │  │
│  │                                                                        │  │
│  │  ┌────────────────────────────────────────────────────────────────┐   │  │
│  │  │                    FLASK APPLICATION                            │   │  │
│  │  │  ┌──────────────────────────────────────────────────────────┐  │   │  │
│  │  │  │                    BLUEPRINTS                             │  │   │  │
│  │  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │  │   │  │
│  │  │  │  │   Health    │ │    Files    │ │      Stats          │ │  │   │  │
│  │  │  │  │   Route     │ │   Routes    │ │      Route          │ │  │   │  │
│  │  │  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │  │   │  │
│  │  │  └──────────────────────────────────────────────────────────┘  │   │  │
│  │  │                              │                                  │   │  │
│  │  │  ┌───────────────────────────▼──────────────────────────────┐  │   │  │
│  │  │  │                    UTILITIES                              │  │   │  │
│  │  │  │  • File validation    • Checksum calculation              │  │   │  │
│  │  │  │  • MIME detection     • Size formatting                   │  │   │  │
│  │  │  └──────────────────────────────────────────────────────────┘  │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────┐  ┌─────────────────────────────────────┐ │  │
│  │  │      SQLAlchemy ORM     │  │         Gunicorn (Production)       │ │  │
│  │  │   (Database Abstraction)│  │         (WSGI Server)               │ │  │
│  │  └───────────┬─────────────┘  └─────────────────────────────────────┘ │  │
│  └──────────────┼────────────────────────────────────────────────────────┘  │
│                 │                                                            │
│  ┌──────────────▼────────────────────────────────────────────────────────┐  │
│  │                         DATA LAYER                                     │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────────┐ │  │
│  │  │        PostgreSQL           │  │        File System              │ │  │
│  │  │        Database             │  │        Storage                  │ │  │
│  │  │                             │  │                                 │ │  │
│  │  │  ┌───────────────────────┐  │  │  /home/pi/pi-cloud-server/     │ │  │
│  │  │  │     files table       │  │  │  └── storage/                  │ │  │
│  │  │  │  - id                 │  │  │      ├── uuid1_file1.pdf       │ │  │
│  │  │  │  - filename           │  │  │      ├── uuid2_image.jpg       │ │  │
│  │  │  │  - original_filename  │  │  │      ├── uuid3_doc.docx        │ │  │
│  │  │  │  - filepath           │  │  │      └── ...                   │ │  │
│  │  │  │  - size               │  │  │                                 │ │  │
│  │  │  │  - mimetype           │  │  │  (Recommended: External SSD)   │ │  │
│  │  │  │  - checksum           │  │  │                                 │ │  │
│  │  │  │  - upload_date        │  │  └─────────────────────────────────┘ │  │
│  │  │  └───────────────────────┘  │                                      │  │
│  │  └─────────────────────────────┘                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Flask Application (`app/__init__.py`)

The application uses the **Factory Pattern** for creating the Flask app:

```python
def create_app(config_name=None):
    app = Flask(__name__)
    # Load config, init extensions, register blueprints
    return app
```

**Benefits:**

- Easy testing with different configurations
- Multiple app instances if needed
- Clean separation of concerns

### 2. Configuration (`app/config.py`)

Three configuration classes:

- `DevelopmentConfig`: Debug mode, verbose logging
- `ProductionConfig`: Security-focused, minimal logging
- `TestingConfig`: In-memory SQLite, temp storage

### 3. Database Model (`app/models/file_model.py`)

```
FileMetadata Table
├── id (Primary Key, Auto-increment)
├── filename (Stored filename with UUID)
├── original_filename (User's original filename)
├── filepath (Full path on disk)
├── size (File size in bytes)
├── mimetype (MIME type)
├── checksum (MD5 hash)
├── upload_date (Timestamp)
├── updated_at (Timestamp)
└── description (Optional text)
```

### 4. API Routes (`app/routes/file_routes.py`)

| Endpoint                   | Method | Description    |
| -------------------------- | ------ | -------------- |
| `/api/health`              | GET    | Health check   |
| `/api/files/upload`        | POST   | Upload file    |
| `/api/files`               | GET    | List all files |
| `/api/files/<id>`          | GET    | Get file info  |
| `/api/files/<id>/download` | GET    | Download file  |
| `/api/files/<id>`          | DELETE | Delete file    |
| `/api/stats`               | GET    | Storage stats  |

### 5. Utility Functions (`app/utils/helpers.py`)

- `generate_unique_filename()`: Adds UUID prefix to prevent collisions
- `calculate_file_checksum()`: MD5 hash for integrity
- `validate_file_size()`: Check against max limit
- `validate_file_extension()`: Check allowed types
- `get_mime_type()`: Detect file type
- `format_file_size()`: Human-readable sizes

---

## Data Flow

### File Upload Flow

```
1. Client sends POST /api/files/upload with file
                    │
2. Flask receives multipart/form-data
                    │
3. Validation checks:
   - File exists?
   - Size within limit?
   - Extension allowed?
                    │
4. Generate unique filename (UUID prefix)
                    │
5. Save file to /storage directory
                    │
6. Calculate MD5 checksum
                    │
7. Detect MIME type
                    │
8. Create database record
                    │
9. Return JSON response with file metadata
```

### File Download Flow

```
1. Client sends GET /api/files/<id>/download
                    │
2. Query database for file record
                    │
3. Check if file exists on disk
                    │
4. Send file with proper headers
```

---

## Security Considerations

### Current Implementation

1. **Filename Sanitization**: Using `werkzeug.secure_filename()`
2. **Unique Filenames**: UUID prefix prevents overwrites
3. **Size Limits**: Configurable max file size
4. **Extension Filtering**: Optional allowed extensions list

### Recommended Additions

1. **API Key Authentication**: Check header on each request
2. **Rate Limiting**: Prevent abuse
3. **HTTPS**: Use nginx reverse proxy or ngrok
4. **Input Validation**: Strict checking of all inputs

---

## Deployment Options

### Development

```bash
python run.py
```

### Production (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
```

### Systemd Service

```ini
[Unit]
Description=Pi Cloud Server
After=network.target postgresql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-cloud-server
ExecStart=/home/pi/pi-cloud-server/venv/bin/gunicorn \
          --bind 0.0.0.0:5000 --workers 2 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Performance Considerations

### Raspberry Pi Limitations

- **CPU**: Quad-core ARM (limited compared to x86)
- **RAM**: 2-8GB depending on model
- **Storage**: SD card (slow) vs SSD (recommended)
- **Network**: 1Gbps Ethernet on Pi 4

### Optimizations

1. **Use External SSD**: Much faster than SD card
2. **Limit Workers**: 2 Gunicorn workers is optimal
3. **Chunk Large Files**: Stream instead of loading into memory
4. **Database Indexing**: Index frequently queried fields
5. **Connection Pooling**: SQLAlchemy pool settings

### Recommended Hardware

- Raspberry Pi 4 (4GB or 8GB)
- USB 3.0 SSD (256GB+)
- Active cooling (heatsink + fan)
- Reliable power supply (3A)

---

## Scaling Options

While designed for single-Pi deployment, scaling options include:

1. **Vertical**: Upgrade to Pi 5 or more RAM
2. **Storage**: Add larger/faster SSD
3. **Caching**: Add Redis for metadata caching
4. **CDN**: Use Cloudflare for static files
5. **Cluster**: Multiple Pis with shared storage (advanced)

---

## Monitoring & Maintenance

### Health Checks

```bash
curl http://localhost:5000/api/health
```

### Log Viewing

```bash
# If using systemd
sudo journalctl -u picloud -f

# If using log file
tail -f /home/pi/pi-cloud-server/logs/picloud.log
```

### Database Maintenance

```bash
# Connect to database
psql -h localhost -U picloud -d picloud_db

# Check table size
SELECT pg_size_pretty(pg_total_relation_size('files'));

# Vacuum (cleanup)
VACUUM ANALYZE files;
```

### Storage Cleanup

```bash
# Check disk usage
df -h

# Check storage folder size
du -sh /home/pi/pi-cloud-server/storage
```

---

## Troubleshooting

| Issue              | Solution                              |
| ------------------ | ------------------------------------- |
| Connection refused | Check if server is running on 0.0.0.0 |
| Database error     | Verify PostgreSQL is running          |
| Permission denied  | Check storage folder permissions      |
| Out of memory      | Reduce Gunicorn workers               |
| Slow uploads       | Use external SSD instead of SD card   |

---

_Architecture document version: 1.0_
