# Docker Data Volume

This directory contains data files for the ArrowTuner Docker containers.

## Contents

- `arrow_database.db` - SQLite database with arrow specifications
- `data/` - Data directory with processed JSON files and images

## Usage

This directory is mounted as a volume in Docker containers:

```yaml
volumes:
  - ./docker-data:/app/data
```

## Last Updated

2025-07-25 19:09:48

## Statistics

- Database arrows: 152
- Processed files: 13
- Image files: 446

## Permissions

Files are owned by user 1000:1000 for Docker compatibility.
