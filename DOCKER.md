# Docker Deployment Guide

This guide explains how to build and run the Spain Eclipse Sites application using Docker.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 1.29 or higher)

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

4. **Access the application:**
   Open your browser to http://localhost:8000

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t eclipse-sites:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name eclipse-sites \
     -p 8000:8000 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     eclipse-sites:latest
   ```

3. **View logs:**
   ```bash
   docker logs -f eclipse-sites
   ```

4. **Stop the container:**
   ```bash
   docker stop eclipse-sites
   docker rm eclipse-sites
   ```

## Configuration

### Environment Variables

You can override configuration using environment variables:

```bash
docker run -d \
  -e ECLIPSE_SITES_SERVER_PORT=9000 \
  -e ECLIPSE_SITES_LOGGING_LEVEL=DEBUG \
  -p 9000:9000 \
  eclipse-sites:latest
```

Or in `docker-compose.yml`:

```yaml
environment:
  - ECLIPSE_SITES_SERVER_PORT=9000
  - ECLIPSE_SITES_LOGGING_LEVEL=DEBUG
```

### Available Environment Variables

See `.env.example` for all available environment variables.

## Data Persistence

The following directories are mounted as volumes to persist data:

- `./data` - Site data, CSV files, KML files, images
- `./logs` - Application logs
- `./.cache` - API response cache

## Health Checks

The container includes a health check that verifies the web server is responding:

```bash
docker ps  # Check HEALTH status column
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs web
```

### Port already in use

Change the port in `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Use port 9000 instead
```

### Permission issues with volumes

Ensure the directories exist and have proper permissions:
```bash
mkdir -p data logs .cache
chmod 755 data logs .cache
```

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (nginx, Traefik) for SSL/TLS
2. **Set resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
   ```
3. **Enable log rotation** for the logs volume
4. **Use Docker secrets** for sensitive configuration
5. **Set up monitoring** and alerting

## Kubernetes/OpenShift

For Kubernetes or OpenShift deployment, see the deployment manifests in the `k8s/` directory (if available) or refer to the REFACTORING_SUGGESTIONS.md document for configuration examples.

## Building for Different Architectures

To build for ARM64 (e.g., Apple Silicon):
```bash
docker buildx build --platform linux/arm64 -t eclipse-sites:arm64 .
```

To build multi-platform:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t eclipse-sites:latest .
```

## Made with Bob