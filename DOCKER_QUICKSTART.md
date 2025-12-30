# Docker Quick Start

## Prerequisites
- Docker and Docker Compose installed
- `.env` file configured with your MongoDB connection

## Quick Commands

### Start Application
```bash
docker compose up -d --build
```

### View Logs
```bash
docker compose logs -f fastapi
```

### Stop Application
```bash
docker compose down
```

### Restart Application
```bash
docker compose restart
```

### Rebuild After Code Changes
```bash
docker compose down
docker compose up -d --build
```

## Access Points

> **Note:** The default port is 8000. Change `PORT` in `.env` to use a different port (e.g., `PORT=8001` for port 8001 on the host).

- API: http://localhost:${PORT:-8000}
- Swagger UI: http://localhost:${PORT:-8000}/docs
- Health Check: http://localhost:${PORT:-8000}/health

## Environment Configuration

Edit `.env` file with your settings:
- `MONGO_URL`: Your MongoDB connection string
- `SECRET_KEY`: Strong random secret (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `ENVIRONMENT`: Set to `production`

## Troubleshooting

**Container won't start?**
```bash
docker compose logs fastapi
```

**Port 8000 already in use?**
Edit `PORT=8001` in `.env` and run:
```bash
docker compose restart
```

**Need to rebuild completely?**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

For detailed documentation, see [DOCKER_SETUP.md](DOCKER_SETUP.md)
