# Pi Cloud Server

## A alternative to big databases for our personal uses

**Version:** 1.0.0  
**Author:** Your Name  
**License:** MIT

---

##  Project Description :

this is a project by me and my friends we made a our very own data base using the pi power and run on the software made by us in debian linux . this project wsa made to complete our neccesaries and why not to include it to the blueprints as we all love it..

Pi Cloud Server is a lightweight, self-hosted cloud storage solution designed to run on a Raspberry Pi. It provides:

- **File Storage:** Upload, download, and manage files stored on your Pi's SSD/SD card
- **Database Backend:** PostgreSQL database to track file metadata
- **REST API:** Clean Flask-based API for all operations
- **LAN Access:** Access your files from any device on your WiFi network
- **Optional Internet Access:** Expose your server online using ngrok

This is perfect for:

- Personal file backup
- Home media server
- Learning about backend development
- IoT data collection
- Private document storage



##  Features

-  Upload files via REST API
-  List all stored files with metadata
-  Download files by ID
-  Delete files
-  File metadata stored in PostgreSQL
-  Actual files stored on filesystem (SSD recommended)
-  Works on local WiFi network
-  Optional ngrok integration for public access
-  Comprehensive logging
-  Error handling with JSON responses
-  Environment-based configuration



##  Folder Structure

```
pi-cloud-server/
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   ├── __init__.py      # Models package init
│   │   └── file_model.py    # File metadata model
│   ├── routes/
│   │   ├── __init__.py      # Routes package init
│   │   └── file_routes.py   # File API endpoints
│   └── utils/
│       ├── __init__.py      # Utils package init
│       └── helpers.py       # Helper functions
│
├── storage/                  # Uploaded files stored here
│   └── .gitkeep             # Keep folder in git
│
├── scripts/
│   └── setup.sh             # Automated setup script
│
├── docs/
│   └── ARCHITECTURE.md      # Detailed architecture docs
│
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── TODO.md                  # Project roadmap
└── README.md                # This file
```

---
# PCB DESIGN:
<img width="1247" height="973" alt="image" src="https://github.com/user-attachments/assets/5278bfda-9c32-47a3-af0d-71c7a102c26c" />
this a pcb board made to connect pi to its pin using connector that give pi an extra ports and hdmi port and a cooling system can also be connected using those ports 

# CAD DESIGN OF  A DATA BASE:

![Uploading image.png…]()
This is a full body of a database the front can be removed and attached so we can add the component very well you can checkouut the parts it is divided into 2 part front and back there is a slot to add your ssd so they stay unshaken and there are ports cut for your pi ports and also for the xternal board that i mentioned before..




### Hardware Requirements

- Raspberry Pi 3B+ or newer (4 recommended)
- MicroSD card (32GB+ recommended)
- External SSD (recommended for file storage)/hhd
- Power supply
- Ethernet cable or WiFi connection

 # i have made a external pcb board for more connection you can look for it in the pcb and shemantic folder.

### Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.9+
- PostgreSQL 13+
- pip (Python package manager)

---

## 🚀 Complete Setup Guide for software installation:

### Step 1: Update Your Raspberry Pi

First, make sure your Pi is up to date:

```bash
# Update package list
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Reboot to apply updates
sudo reboot
```

### Step 2: Install Required System Packages

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install libpq-dev (required for psycopg2)
sudo apt install -y libpq-dev

# Verify installations
python3 --version
psql --version
```

### Step 3: Set Up PostgreSQL Database

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check PostgreSQL status
sudo systemctl status postgresql
```

Now create the database and user:

```bash
# Switch to postgres user
sudo -u postgres psql
```

Inside the PostgreSQL shell, run these commands:

```sql
-- Create a new database user
CREATE USER picloud WITH PASSWORD 'your_secure_password_here';

-- Create the database
CREATE DATABASE picloud_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE picloud_db TO picloud;

-- Connect to the database to grant schema permissions
\c picloud_db

-- Grant schema permissions (required for PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO picloud;

-- Exit PostgreSQL shell
\q
```

Verify the database connection:

```bash
# Test the connection
psql -h localhost -U picloud -d picloud_db
# Enter your password when prompted
# Type \q to exit
```

### Step 4: Clone the Project

```bash
# Navigate to your preferred directory
cd ~

# Clone the repository
git clone https://github.com/yourusername/pi-cloud-server.git

# Or if setting up manually, create the directory
mkdir -p pi-cloud-server
cd pi-cloud-server
```

### Step 5: Set Up Python Virtual Environment

```bash
# Navigate to project directory
cd ~/pi-cloud-server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify you're in the virtual environment
# Your prompt should show (venv) at the beginning
which python
# Should output: /home/pi/pi-cloud-server/venv/bin/python
```

### Step 6: Install Python Dependencies

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 7: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env
```

Update the `.env` file with your settings:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key-change-this

# Database Configuration
DATABASE_URL=postgresql://picloud:your_secure_password_here@localhost:5432/picloud_db

# Storage Configuration
STORAGE_PATH=/home/pi/pi-cloud-server/storage
MAX_FILE_SIZE=104857600

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 8: Create Storage Directory

```bash
# Create storage directory if it doesn't exist
mkdir -p storage

# Set proper permissions
chmod 755 storage
```

### Step 9: Initialize the Database

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run the application once to create tables
python run.py
# Press Ctrl+C after you see "Running on http://0.0.0.0:5000"
```

---

##  Running the Server

### Development Mode

```bash
# Navigate to project directory
cd ~/pi-cloud-server

# Activate virtual environment
source venv/bin/activate

# Run the server
python run.py
```

You should see:

```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.XXX:5000
```

### Production Mode with Gunicorn

For production, use Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
```

### Run as a System Service (Auto-start on Boot)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/picloud.service
```

Add this content:

```ini
[Unit]
Description=Pi Cloud Server
After=network.target postgresql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-cloud-server
Environment="PATH=/home/pi/pi-cloud-server/venv/bin"
ExecStart=/home/pi/pi-cloud-server/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable picloud

# Start the service
sudo systemctl start picloud

# Check status
sudo systemctl status picloud

# View logs
sudo journalctl -u picloud -f
```

---

##  API Documentation

### Base URL

- Local: `http://localhost:5000/api`
- LAN: `http://192.168.x.x:5000/api`

### Endpoints

#### 1. Health Check

Check if the server is running.

```bash
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "message": "Pi Cloud Server is running",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Upload File

Upload a file to the server.

```bash
POST /api/files/upload
Content-Type: multipart/form-data
```

**Parameters:**

- `file` (required): The file to upload

**Example using curl:**

```bash
curl -X POST \
  -F "file=@/path/to/your/file.pdf" \
  http://192.168.1.100:5000/api/files/upload
```

**Response:**

```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "id": 1,
    "filename": "file.pdf",
    "original_filename": "file.pdf",
    "size": 102400,
    "mimetype": "application/pdf",
    "upload_date": "2024-01-15T10:30:00Z"
  }
}
```

#### 3. List All Files

Get a list of all uploaded files.

```bash
GET /api/files
```

**Optional Query Parameters:**

- `page` (default: 1): Page number
- `per_page` (default: 20): Items per page

**Example:**

```bash
curl http://192.168.1.100:5000/api/files
curl http://192.168.1.100:5000/api/files?page=1&per_page=10
```

**Response:**

```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": 1,
        "filename": "file.pdf",
        "original_filename": "file.pdf",
        "size": 102400,
        "size_human": "100 KB",
        "mimetype": "application/pdf",
        "upload_date": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

#### 4. Get File Info

Get metadata for a specific file.

```bash
GET /api/files/<file_id>
```

**Example:**

```bash
curl http://192.168.1.100:5000/api/files/1
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "file.pdf",
    "original_filename": "file.pdf",
    "size": 102400,
    "size_human": "100 KB",
    "mimetype": "application/pdf",
    "upload_date": "2024-01-15T10:30:00Z"
  }
}
```

#### 5. Download File

Download a file from the server.

```bash
GET /api/files/<file_id>/download
```

**Example:**

```bash
curl -O http://192.168.1.100:5000/api/files/1/download
```

#### 6. Delete File

Delete a file from the server.

```bash
DELETE /api/files/<file_id>
```

**Example:**

```bash
curl -X DELETE http://192.168.1.100:5000/api/files/1
```

**Response:**

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

#### 7. Storage Statistics

Get storage usage statistics.

```bash
GET /api/stats
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_files": 10,
    "total_size": 1048576,
    "total_size_human": "1 MB",
    "storage_path": "/home/pi/pi-cloud-server/storage"
  }
}
```

---

##  Accessing from Other Devices

### Step 1: Find Your Raspberry Pi's IP Address

```bash
# Method 1: Using hostname command
hostname -I

# Method 2: Using ip command
ip addr show | grep "inet " | grep -v 127.0.0.1

# Method 3: Using ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1
```

You'll see something like: `192.168.1.100`

### Step 2: Make Sure Server is Listening on All Interfaces

The server must be configured to listen on `0.0.0.0` (all interfaces), not just `127.0.0.1` (localhost).

Check your `.env` file:

```bash
HOST=0.0.0.0
PORT=5000
```

### Step 3: Configure Firewall (if enabled)

```bash
# Check if UFW is active
sudo ufw status

# If active, allow port 5000
sudo ufw allow 5000

# Verify the rule was added
sudo ufw status
```

### Step 4: Access from Another Device

On any device connected to the same WiFi network:

1. Open a web browser
2. Go to: `http://192.168.1.100:5000/api/health`
3. You should see the health check response

### Testing with curl from Another Computer

```bash
# Replace with your Pi's IP address
curl http://192.168.1.100:5000/api/health

# Upload a file
curl -X POST -F "file=@test.txt" http://192.168.1.100:5000/api/files/upload

# List files
curl http://192.168.1.100:5000/api/files
```

---

##  Exposing Online with ngrok

ngrok creates a secure tunnel to your local server, making it accessible from anywhere on the internet.

### Step 1: Install ngrok

```bash
# Download ngrok for ARM (Raspberry Pi)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz

# For 32-bit Raspberry Pi OS, use:
# wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz

# Extract
tar -xvzf ngrok-v3-stable-linux-arm64.tgz

# Move to PATH
sudo mv ngrok /usr/local/bin/

# Verify installation
ngrok version
```

### Step 2: Create ngrok Account

1. Go to https://ngrok.com/
2. Sign up for a free account
3. Go to Dashboard > Your Authtoken
4. Copy your authtoken

### Step 3: Configure ngrok

```bash
# Add your authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 4: Start ngrok Tunnel

Make sure your Flask server is running, then:

```bash
# Start ngrok tunnel to port 5000
ngrok http 5000
```

You'll see output like:

```
Session Status                online
Account                       your@email.com (Plan: Free)
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

### Step 5: Access Your Server Online

Use the ngrok URL (e.g., `https://abc123.ngrok.io`) to access your server from anywhere:

```bash
curl https://abc123.ngrok.io/api/health
```

### Running ngrok in Background

```bash
# Install screen (if not installed)
sudo apt install screen

# Start a screen session
screen -S ngrok

# Run ngrok
ngrok http 5000

# Detach from screen: Press Ctrl+A, then D

# Reattach later
screen -r ngrok
```

### Important Notes about ngrok

- Free tier URLs change each time you restart ngrok
- Free tier has limited connections per minute
- For a static URL, upgrade to a paid plan
- Don't share your ngrok URL publicly if storing sensitive data

---

##  Troubleshooting

### Common Issues and Solutions

#### 1. "Connection refused" when accessing from another device

```bash
# Check if server is running
sudo systemctl status picloud

# Check if listening on correct interface
ss -tlnp | grep 5000

# Should show: 0.0.0.0:5000 (not 127.0.0.1:5000)
```

#### 2. PostgreSQL connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Test connection
psql -h localhost -U picloud -d picloud_db
```

#### 3. "Permission denied" errors for storage folder

```bash
# Fix permissions
sudo chown -R pi:pi /home/pi/pi-cloud-server/storage
chmod 755 /home/pi/pi-cloud-server/storage
```

#### 4. "Module not found" errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 5. Port 5000 already in use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>
```

### Viewing Logs

```bash
# Application logs (if running as service)
sudo journalctl -u picloud -f

# PostgreSQL logs
sudo tail -f /var/log/postgresql/*.log

# System logs
sudo tail -f /var/log/syslog
```

---

##  Security Considerations

### For Local Network Use

1. **Change default passwords**: Never use default PostgreSQL passwords
2. **Update regularly**: Keep your Pi and packages updated
3. **Use strong passwords**: For both PostgreSQL and any API auth you add
4. **Backup data**: Regularly backup your database and files

### For Internet Exposure (ngrok)

1. **Add authentication**: Implement API keys or JWT authentication
2. **Use HTTPS**: ngrok provides HTTPS by default
3. **Rate limiting**: Add rate limiting to prevent abuse
4. **Don't store sensitive data**: Be cautious about what you store
5. **Monitor access**: Check ngrok dashboard for access logs

### Adding Basic API Key Authentication

Add this to your `.env`:

```bash
API_KEY=your-secret-api-key-here
```

Then check the API key in your routes (example provided in code comments).

---

## Contact if you had any problem regarding this project

gmail:mjlabishek123@gmail.com

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing issues on GitHub
3. Open a new issue with:
   - Your Raspberry Pi model
   - OS version (`cat /etc/os-release`)
   - Python version (`python3 --version`)
   - Complete error message
   - Steps to reproduce

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Flask framework
- SQLAlchemy ORM
- PostgreSQL
- Raspberry Pi Foundation

---

**Happy Hosting! 🎉**
blueprint is awesome.
