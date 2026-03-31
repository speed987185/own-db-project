#!/bin/bash

# =============================================================================
# Pi Cloud Server - Automated Setup Script
# =============================================================================
# This script automates the setup of the Pi Cloud Server on a Raspberry Pi
# Run with: sudo bash scripts/setup.sh
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="picloud_db"
DB_USER="picloud"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use sudo)"
        exit 1
    fi
}

# Get the actual user (not root when using sudo)
get_actual_user() {
    if [ -n "$SUDO_USER" ]; then
        echo "$SUDO_USER"
    else
        echo "$(whoami)"
    fi
}

# =============================================================================
# Installation Functions
# =============================================================================

update_system() {
    print_header "Updating System Packages"
    apt update
    apt upgrade -y
    print_success "System updated successfully"
}

install_system_dependencies() {
    print_header "Installing System Dependencies"
    
    # Python and pip
    apt install -y python3 python3-pip python3-venv
    print_success "Python installed"
    
    # PostgreSQL
    apt install -y postgresql postgresql-contrib
    print_success "PostgreSQL installed"
    
    # Required for psycopg2
    apt install -y libpq-dev
    print_success "libpq-dev installed"
    
    # Additional useful tools
    apt install -y curl wget git
    print_success "Additional tools installed"
    
    # For python-magic
    apt install -y libmagic1
    print_success "libmagic installed"
}

setup_postgresql() {
    print_header "Setting Up PostgreSQL"
    
    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    print_success "PostgreSQL service started and enabled"
    
    # Generate a random password if not provided
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)
        print_warning "Generated database password: $DB_PASSWORD"
        print_warning "SAVE THIS PASSWORD! You will need it for the .env file"
    fi
    
    # Check if user exists
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        print_warning "Database user '$DB_USER' already exists"
    else
        # Create database user
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        print_success "Database user '$DB_USER' created"
    fi
    
    # Check if database exists
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        print_warning "Database '$DB_NAME' already exists"
    else
        # Create database
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        print_success "Database '$DB_NAME' created"
    fi
    
    # Grant privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    print_success "Privileges granted"
}

setup_python_environment() {
    print_header "Setting Up Python Environment"
    
    ACTUAL_USER=$(get_actual_user)
    
    # Navigate to project directory
    cd "$PROJECT_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        sudo -u "$ACTUAL_USER" python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Install dependencies
    sudo -u "$ACTUAL_USER" ./venv/bin/pip install --upgrade pip
    sudo -u "$ACTUAL_USER" ./venv/bin/pip install -r requirements.txt
    print_success "Python dependencies installed"
}

create_env_file() {
    print_header "Creating Environment File"
    
    ACTUAL_USER=$(get_actual_user)
    
    if [ -f "$PROJECT_DIR/.env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Create .env file
    cat > "$PROJECT_DIR/.env" << EOF
# Pi Cloud Server - Environment Configuration
# Generated by setup script on $(date)

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=$SECRET_KEY

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Storage Configuration
STORAGE_PATH=$PROJECT_DIR/storage
MAX_FILE_SIZE=104857600

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=$PROJECT_DIR/logs/picloud.log
EOF

    chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    
    print_success ".env file created"
}

create_directories() {
    print_header "Creating Required Directories"
    
    ACTUAL_USER=$(get_actual_user)
    
    # Create storage directory
    mkdir -p "$PROJECT_DIR/storage"
    chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/storage"
    chmod 755 "$PROJECT_DIR/storage"
    print_success "Storage directory created"
    
    # Create logs directory
    mkdir -p "$PROJECT_DIR/logs"
    chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/logs"
    chmod 755 "$PROJECT_DIR/logs"
    print_success "Logs directory created"
}

setup_systemd_service() {
    print_header "Setting Up Systemd Service"
    
    ACTUAL_USER=$(get_actual_user)
    
    # Create service file
    cat > /etc/systemd/system/picloud.service << EOF
[Unit]
Description=Pi Cloud Server
After=network.target postgresql.service

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "Systemd service created"
    
    print_info "To enable and start the service, run:"
    print_info "  sudo systemctl enable picloud"
    print_info "  sudo systemctl start picloud"
}

configure_firewall() {
    print_header "Configuring Firewall"
    
    # Check if UFW is installed and active
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            ufw allow 5000
            print_success "Firewall rule added for port 5000"
        else
            print_info "UFW is installed but not active"
        fi
    else
        print_info "UFW is not installed, skipping firewall configuration"
    fi
}

print_summary() {
    print_header "Setup Complete!"
    
    IP_ADDR=$(hostname -I | awk '{print $1}')
    
    echo -e "${GREEN}Pi Cloud Server has been set up successfully!${NC}\n"
    
    echo "=== Important Information ==="
    echo ""
    echo "Database Credentials:"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo "Server Details:"
    echo "  Local URL: http://localhost:5000"
    echo "  LAN URL: http://$IP_ADDR:5000"
    echo ""
    echo "=== Next Steps ==="
    echo ""
    echo "1. Review and update .env file if needed:"
    echo "   nano $PROJECT_DIR/.env"
    echo ""
    echo "2. Start the development server:"
    echo "   cd $PROJECT_DIR"
    echo "   source venv/bin/activate"
    echo "   python run.py"
    echo ""
    echo "3. Or enable and start the systemd service:"
    echo "   sudo systemctl enable picloud"
    echo "   sudo systemctl start picloud"
    echo ""
    echo "4. Test the API:"
    echo "   curl http://localhost:5000/api/health"
    echo ""
    echo "For more information, see README.md"
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    print_header "Pi Cloud Server - Setup Script"
    
    echo "This script will:"
    echo "  1. Update system packages"
    echo "  2. Install Python, PostgreSQL, and dependencies"
    echo "  3. Set up the database"
    echo "  4. Create Python virtual environment"
    echo "  5. Install Python packages"
    echo "  6. Configure the application"
    echo ""
    
    read -p "Continue with setup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled"
        exit 0
    fi
    
    check_root
    
    update_system
    install_system_dependencies
    setup_postgresql
    create_directories
    setup_python_environment
    create_env_file
    setup_systemd_service
    configure_firewall
    
    print_summary
}

# Run main function
main "$@"
