# Pi Cloud Server

A lightweight local cloud storage server designed for Raspberry Pi.

---

## ⚠️ Prototype Notice

> **This repository contains a prototype implementation built for demonstration and submission purposes. The current version is developed and tested on a standard computer. Final deployment and hardware integration with Raspberry Pi will be performed after receiving approval from Blueprint Hack Club.**

---

## What is this?

Pi Cloud Server is a self-hosted cloud storage solution that runs on a Raspberry Pi. It provides:

- **File metadata storage** using PostgreSQL database
- **REST API** for managing files
- **Local network access** to your personal cloud

Think of it as your own mini Dropbox, running on a $35 computer in your home.

---

## What this demonstrates

- Flask backend development
- SQLAlchemy ORM integration
- PostgreSQL database usage
- RESTful API design
- Modular Python project structure

---

## Project Structure

```
pi-cloud-server/
├── app.py           # Main Flask application
├── config.py        # Configuration settings
├── models.py        # Database models (SQLAlchemy)
├── routes.py        # API endpoints
├── requirements.txt # Python dependencies
├── schema.sql       # Database schema (optional)
├── TODO.md          # Future development plans
└── storage/         # File storage directory (future use)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE picloud_db;"
psql -U postgres -c "CREATE USER picloud WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE picloud_db TO picloud;"
```

### 3. Run the server

```bash
python app.py
```

Server will start at `http://localhost:5000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server status |
| GET | `/files` | List all files |
| POST | `/files` | Create file metadata |
| GET | `/files/<id>` | Get single file |
| DELETE | `/files/<id>` | Delete file |
| GET | `/stats` | Storage statistics |

---

## Example Usage

### Check server status
```bash
curl http://localhost:5000/
```

### Create file metadata
```bash
curl -X POST http://localhost:5000/files \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.pdf", "size": 1024, "file_type": "application/pdf"}'
```

### List all files
```bash
curl http://localhost:5000/files
```

### Delete a file
```bash
curl -X DELETE http://localhost:5000/files/1
```

---

## Database Configuration

Default connection string:
```
postgresql://picloud:password@localhost:5432/picloud_db
```

Override with environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
```

---

## Future Plans

After Blueprint Hack Club grant approval:

- Deploy on Raspberry Pi 4
- Integrate external SSD storage
- Add actual file upload/download
- Implement user authentication
- Create web dashboard

See `TODO.md` for full roadmap.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL, SQLAlchemy
- **Target Hardware:** Raspberry Pi 4

---

## License

MIT License

---

*Built for Blueprint Hack Club*
