# Deployment Guide

## 🚀 Deployment Options

### Local Development
```bash
# Start development server
python app.py

# Or with Docker
docker-compose up -d
```

### Production Server

#### Option 1: Docker Compose (Recommended)
```bash
# 1. Clone repository
git clone <your-repo-url>
cd qfil-downloader

# 2. Configure environment
cp docker-compose.yml docker-compose.prod.yml
# Edit docker-compose.prod.yml with your settings

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2: Systemd Service
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Create systemd service
sudo tee /etc/systemd/system/qfil-downloader.service << EOF
[Unit]
Description=QFIL Downloader
After=network.target

[Service]
Type=exec
User=qfil
WorkingDirectory=/opt/qfil-downloader
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 3. Enable and start
sudo systemctl enable qfil-downloader
sudo systemctl start qfil-downloader
```

### Cloud Deployment

#### AWS ECS
1. Push Docker image to ECR
2. Create ECS task definition
3. Deploy to ECS service

#### Google Cloud Run
```bash
# Build and deploy
gcloud run deploy qfil-downloader \
  --source . \
  --platform managed \
  --region us-central1
```

#### Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name qfil-downloader \
  --image qfil-downloader:latest \
  --ports 5000
```

## 🔄 Update Process

### Development Updates
```bash
# Code changes
git pull
./update.sh quick
```

### Production Updates
```bash
# 1. Backup
cp projects.json projects.json.backup

# 2. Test in staging
git checkout staging
./update.sh clean

# 3. Deploy to production
git checkout main
git pull origin main
./update.sh rolling  # Zero downtime
```

## 📊 Monitoring

### Health Checks
- Built-in health endpoint: `GET /`
- Docker health check included
- Monitor with tools like Prometheus/Grafana

### Logs
```bash
# View logs
docker-compose logs -f

# System logs
journalctl -u qfil-downloader -f
```