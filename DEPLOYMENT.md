# SecureScout Deployment Guide

This guide explains how to deploy SecureScout in different environments using Docker containers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Production Deployment](#production-deployment)
4. [Configuration Options](#configuration-options)
5. [Maintenance](#maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying SecureScout, ensure you have the following installed:

- Docker (20.10.x or newer)
- Docker Compose (2.x or newer)
- Git
- Bash (for Linux/macOS) or PowerShell (for Windows)

## Local Development Deployment

### Quick Start

For a quick development setup:

1. Clone the repository:
   ```bash
   git clone https://github.com/aegntic/sec-scout.git
   cd sec-scout
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with your desired configurations

4. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

5. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8001

### Manual Development Setup

If you prefer to run the services individually:

1. Set up the backend:
   ```bash
   cd SecureScout
   pip install -r requirements.txt
   python -m backend.app
   ```

2. Set up the frontend:
   ```bash
   cd SecureScout/frontend
   npm install
   npm start
   ```

## Production Deployment

### Using Docker Compose

For a production deployment using Docker Compose:

1. Clone the repository on your production server:
   ```bash
   git clone https://github.com/aegntic/sec-scout.git
   cd sec-scout
   ```

2. Create a `.env` file with production settings:
   ```bash
   cp .env.template .env
   ```

3. **Important**: Edit the `.env` file and change all security-related variables:
   - Generate strong random keys for `SECRET_KEY` and `JWT_SECRET_KEY`
   - Set a strong admin password for `DEFAULT_ADMIN_PASSWORD`
   - Configure other environment settings as appropriate

4. Deploy using Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Set up a reverse proxy (Nginx or similar) for SSL termination and proper hostname handling

### Using Kubernetes

For deploying in a Kubernetes environment, use the provided Kubernetes manifests:

1. Create a namespace:
   ```bash
   kubectl create namespace securescout
   ```

2. Create a secret with your environment variables:
   ```bash
   kubectl create secret generic securescout-env --from-env-file=.env -n securescout
   ```

3. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f kubernetes/
   ```

4. Access the application through the configured Ingress

## Configuration Options

### Environment Variables

Key environment variables for configuring SecureScout:

| Variable | Description | Default |
|----------|-------------|---------|
| SECURESCOUT_ENV | Environment type (development, testing, production) | development |
| SECRET_KEY | Flask secret key | dev-key-change-in-production |
| JWT_SECRET_KEY | JWT token signing key | jwt-dev-key-change-in-production |
| CREATE_DEFAULT_ADMIN | Create default admin on startup | true |
| DEFAULT_ADMIN_USERNAME | Default admin username | admin |
| DEFAULT_ADMIN_PASSWORD | Default admin password | SecureScout@2025! |
| DEFAULT_ADMIN_EMAIL | Default admin email | admin@securescout.local |
| ALLOW_SELF_REGISTRATION | Allow users to self-register | false |
| ACCESS_TOKEN_LIFETIME_MINUTES | JWT access token lifetime | 30 |
| REFRESH_TOKEN_LIFETIME_DAYS | JWT refresh token lifetime | 7 |
| REDIS_URL | Redis connection URL | redis://redis:6379/0 |

### Persistent Storage

The Docker Compose setup maps the following directories for persistent storage:

- `./data`: Database and application data
- `./logs`: Application logs
- `./reports`: Generated security reports

Ensure these directories have appropriate permissions.

## Maintenance

### Updating

To update to a new version:

1. Pull the latest code:
   ```bash
   git pull
   ```

2. Rebuild and restart the containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Backup and Restore

To back up your data:

1. Stop the containers:
   ```bash
   docker-compose down
   ```

2. Back up the data directory:
   ```bash
   tar -czf securescout-backup-$(date +%Y%m%d).tar.gz data
   ```

To restore from backup:

1. Stop the containers:
   ```bash
   docker-compose down
   ```

2. Extract the backup to replace the data directory:
   ```bash
   rm -rf data
   tar -xzf securescout-backup-20230101.tar.gz
   ```

3. Restart the containers:
   ```bash
   docker-compose up -d
   ```

## Troubleshooting

### Common Issues

1. **Cannot access the application after deployment**
   - Check if all containers are running: `docker-compose ps`
   - Check container logs: `docker-compose logs -f`
   - Verify the firewall settings allow traffic on ports 80 and 8001

2. **Login issues after deployment**
   - Ensure the JWT_SECRET_KEY is consistent if you're upgrading
   - Check backend logs for authentication errors

3. **Application performance issues**
   - Check resource usage: `docker stats`
   - Consider increasing container resource limits in the docker-compose.yml file

### Viewing Logs

Access container logs using:

```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Getting Help

If you encounter issues not covered by this guide, please:

1. Check the GitHub repository issues section
2. Create a new issue with detailed information about the problem
3. Include logs and environment information when reporting issues