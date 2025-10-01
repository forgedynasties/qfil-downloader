# QFIL Downloader - Docker Deployment

## 🐳 Docker Setup

This Flask application can be easily deployed using Docker and Docker Compose.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd qfil-downloader
   ```

2. **Update docker-compose.yml:**
   Edit the volumes section to point to your AOSP projects:
   ```yaml
   volumes:
     - /your/actual/path/to/aosp/projects:/projects:ro
   ```

3. **Build and run:**
   ```bash
   docker compose up -d
   ```

4. **Access the application:**
   Open http://localhost:5000

### Docker Commands

#### Using Docker Compose (Recommended)

```bash
# Build and start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop the application
docker compose down

# Rebuild after code changes
docker compose up --build -d
```

#### Using Docker directly

```bash
# Build the image
docker build -t qfil-downloader .

# Run the container
docker run -d \
  --name qfil-downloader \
  -p 5000:5000 \
  -v $(pwd)/projects.json:/app/projects.json \
  -v /path/to/your/aosp/projects:/projects:ro \
  qfil-downloader
```

### Configuration

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `SECRET_KEY` | `your-secret-key-change-this` | Flask secret key |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `5000` | Server port |

#### Volumes

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./projects.json` | `/app/projects.json` | Project configurations |
| `/your/aosp/projects` | `/projects` | AOSP project files (read-only) |
| `qfil_temp` | `/app/temp` | Temporary download files |

### Production Deployment

For production deployment:

1. **Update the secret key:**
   ```yaml
   environment:
     - SECRET_KEY=your-secure-random-secret-key-here
   ```

2. **Use reverse proxy (recommended):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable SSL/TLS with Let's Encrypt or similar**

### Monitoring

#### Health Check

The container includes a built-in health check:
```bash
# Check container health
docker ps

# Manual health check
curl -f http://localhost:5000/
```

#### Logs

```bash
# View application logs
docker compose logs qfil-downloader

# Follow logs in real-time
docker compose logs -f qfil-downloader
```

### Troubleshooting

#### Common Issues

1. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R 1000:1000 ./projects.json
   ```

2. **Port already in use:**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8080:5000"  # Use port 8080 instead
   ```

3. **Volume mount issues:**
   - Ensure paths exist on host system
   - Check file permissions
   - Verify AOSP project structure

#### Container Shell Access

```bash
# Access container shell for debugging
docker compose exec qfil-downloader /bin/bash
```

### Scaling

For higher load, scale with multiple workers:

```yaml
# In docker-compose.yml
command: ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "app:app"]
```

Or deploy multiple instances:
```bash
docker compose up --scale qfil-downloader=3
```

### Updates

#### Automated Update Scripts

Use the provided update scripts for easy container updates:

**Linux/macOS:**
```bash
# Quick update (recommended for code changes)
./update.sh quick

# Clean update (rebuilds everything)
./update.sh clean

# Rolling update (zero downtime)
./update.sh rolling
```

**Windows:**
```cmd
# Quick update (recommended for code changes)
update.bat quick

# Clean update (rebuilds everything)
update.bat clean

# Rolling update (zero downtime)
update.bat rolling
```

#### Manual Update Methods

**Quick Update (Code Changes):**
```bash
docker compose down
docker compose up --build -d
```

**Clean Update (Fresh Start):**
```bash
docker compose down --volumes --remove-orphans
docker image prune -f
docker compose up --build -d
```

**Rolling Update (Zero Downtime):**
```bash
docker compose build
docker compose up -d --scale qfil-downloader=2 --no-recreate
sleep 30
docker compose up -d --scale qfil-downloader=1
```

#### Update Best Practices

1. **Always backup `projects.json`** before updates
2. **Test updates** in a staging environment first
3. **Use quick updates** for minor code changes
4. **Use clean updates** for major changes or dependency updates
5. **Use rolling updates** for production zero-downtime deployments

#### Git-based Updates

If using Git for deployment:
```bash
# Pull latest changes
git pull origin main

# Run update script
./update.sh quick
```

### Backup

Important files to backup:
- `projects.json` - Project configurations
- Any custom configuration files

```bash
# Backup project configurations
docker compose exec qfil-downloader cat /app/projects.json > backup-projects.json

# Automated backup (included in update scripts)
cp projects.json projects.json.backup.$(date +%Y%m%d_%H%M%S)
```