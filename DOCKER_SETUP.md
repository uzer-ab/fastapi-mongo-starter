# Docker Setup Guide

This guide provides step-by-step instructions for running the FastAPI MongoDB Starter project using Docker and Docker Compose in **production mode**.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker Engine** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

### Installation Links

- [Docker Desktop for Windows/Mac](https://www.docker.com/products/docker-desktop)
- [Docker Engine for Linux](https://docs.docker.com/engine/install/)

Verify your installation:

```bash
docker --version
docker compose version
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd fastapi-mongo-starter
```

### 2. Environment Configuration

**IMPORTANT:** This Docker setup is configured for production and uses your existing `.env` file.

#### Create or Update Your .env File

If you don't have a `.env` file, create one from the example:

```bash
cp .env.example .env
```

Edit `.env` with your production values:

```env
# MongoDB Configuration
# Use MongoDB Atlas (cloud) or any MongoDB connection string
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net
MONGODB_NAME=fastapi-app

# Application Security
# IMPORTANT: Generate a strong secret key for production
SECRET_KEY=your-super-secret-key-here-change-this-in-production

# Server Configuration
HOST=0.0.0.0
PORT=8000  # External port (host). Container always uses internal port 8000.
WORKERS=4

# Environment
ENVIRONMENT=production
```

#### Generate a Secure Secret Key

To generate a secure secret key for production:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32
```

### 3. Build and Start Services

Run the following command to build and start the application:

```bash
docker compose up -d --build
```

**Flags:**

- `-d` or `--detach`: Run containers in the background
- `--build`: Force rebuild of the Docker image

**What this does:**

- Builds the FastAPI application Docker image
- Copies your `.env` file into the container
- Creates a bridge network
- Starts FastAPI application container
- Connects to your MongoDB instance (Atlas or local)

### 4. Verify Services are Running

Check the status of running containers:

```bash
docker compose ps
```

Expected output:

```
NAME                     IMAGE                             STATUS         PORTS
fastapi_app_mongo        fastapi-mongo-starter-fastapi     Up 30 seconds  0.0.0.0:8000->8000/tcp
```

### 5. View Logs

To view application logs:

```bash
docker compose logs -f fastapi
```

Press `Ctrl+C` to exit log viewing.

### 6. Access the Application

Once the services are running, you can access:

> **Note:** Default port is 8000. Change `PORT` in `.env` to use a different port.

| Service             | URL                                        | Description                   |
| ------------------- | ------------------------------------------ | ----------------------------- |
| **API Root**        | http://localhost:${PORT:-8000}             | Root endpoint                 |
| **Swagger UI**      | http://localhost:${PORT:-8000}/docs        | Interactive API documentation |
| **ReDoc**           | http://localhost:${PORT:-8000}/redoc       | Alternative API documentation |
| **Health Check**    | http://localhost:${PORT:-8000}/health      | Basic health check            |
| **Readiness Check** | http://localhost:${PORT:-8000}/ready       | Database connection check     |

### 7. Test the API

Test the health endpoint:

```bash
curl http://localhost:${PORT:-8000}/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-29T12:00:00.000000Z"
}
```

## Docker Commands Reference

### Starting Services

```bash
# Start services (build if needed)
docker compose up -d

# Start services with rebuild
docker compose up -d --build

# Start without detached mode (see logs in terminal)
docker compose up
```

### Stopping Services

```bash
# Stop services (containers remain)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers, networks, and volumes
docker compose down -v
```

### Rebuilding Services

```bash
# Rebuild specific service
docker compose build fastapi

# Rebuild all services
docker compose build

# Force rebuild (no cache)
docker compose build --no-cache
```

### Viewing Logs

```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs from specific service
docker compose logs -f fastapi
docker compose logs -f mongodb

# View last 100 lines
docker compose logs --tail=100 fastapi
```

### Executing Commands in Containers

```bash
# Access FastAPI container shell
docker compose exec fastapi /bin/bash

# Access MongoDB shell
docker compose exec mongodb mongosh -u admin -p admin123
```

### Container Management

```bash
# List running containers
docker compose ps

# List all containers (including stopped)
docker compose ps -a

# Restart specific service
docker compose restart fastapi

# Restart all services
docker compose restart
```

## Configuration Notes

### MongoDB Connection

This setup uses your existing MongoDB connection from `.env`:

- **MongoDB Atlas (Cloud)**: Recommended for production
- **Local MongoDB**: Can also be configured via `MONGO_URL`

The Docker container connects to your MongoDB instance specified in the `.env` file.

### Environment Variables

All configuration is loaded from your `.env` file:

- `MONGO_URL`: Your MongoDB connection string
- `MONGODB_NAME`: Database name
- `SECRET_KEY`: JWT secret key
- `HOST`, `PORT`, `WORKERS`: Server configuration
  - `PORT` controls the **external/host** port (e.g., 8000, 8001)
  - The container always uses internal port 8000
- `ENVIRONMENT`: Set to `production` for production mode

## Troubleshooting

### Port Already in Use

If you get an error about port 8000 or 27017 already being in use:

```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :27017

# Or use netstat
netstat -tulpn | grep 8000
netstat -tulpn | grep 27017
```

**Solution:** Either stop the service using that port or change the port in `docker-compose.yml`:

```yaml
ports:
  - "8080:8000" # Map host port 8080 to container port 8000
```

### Container Keeps Restarting

Check the logs to identify the issue:

```bash
docker compose logs fastapi
```

Common causes:

- MongoDB not ready (health check will wait)
- Missing environment variables
- Application errors

### Cannot Connect to MongoDB

Check your MongoDB connection string in `.env`:

```bash
# Verify your MONGO_URL is correct
cat .env | grep MONGO_URL
```

Check the application logs for connection errors:

```bash
docker compose logs fastapi | grep -i mongo
```

### Application Shows Old Code

Rebuild the image with no cache:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### View Container Resource Usage

```bash
docker stats
```

## Cleanup

### Remove All Containers and Networks

```bash
docker compose down
```

### Remove Everything

```bash
# Stop and remove containers
docker compose down

# Also remove images
docker rmi fastapi-mongo-starter-fastapi

# Remove all unused images
docker image prune -a
```

## Summary

This Docker setup provides:

- **Production-ready** configuration
- **Environment-based** configuration from `.env` file
- **Secure** with non-root user and no hardcoded credentials
- **Optimized** multi-stage build for smaller images
- **Health checks** for monitoring
- **Flexible** works with MongoDB Atlas or local MongoDB

Simply configure your `.env` file and run `docker compose up -d --build`!

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
