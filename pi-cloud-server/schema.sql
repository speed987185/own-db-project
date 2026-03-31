-- Pi Cloud Server - Database Schema
-- PostgreSQL

-- Create files table
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    size BIGINT DEFAULT 0,
    file_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    user_id INTEGER
);

-- Optional: Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at DESC);
