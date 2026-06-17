# EasyPost AWS EC2 Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Environment Configuration](#environment-configuration)
4. [Docker & Docker Compose Setup](#docker--docker-compose-setup)
5. [Database Initialization](#database-initialization)
6. [SSL/TLS Certificate Setup](#ssltls-certificate-setup)
7. [Application Deployment](#application-deployment)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### AWS Requirements
- AWS Account with appropriate IAM permissions
- EC2 instance (recommended: `t3.xlarge` or larger for production)
- Security Groups configured
- Elastic IP (static IP address)
- RDS or self-hosted PostgreSQL option
- S3 bucket for media storage
- CloudFront for CDN (optional)

### Required AWS Services
- **EC2**: Compute instance
- **S3**: Media storage & backups
- **RDS** (optional): Managed PostgreSQL
- **CloudWatch**: Monitoring & logs
- **VPC & Security Groups**: Networking
- **Route53**: DNS management

---

## EC2 Instance Setup

### 1. Launch EC2 Instance

```bash
# AWS CLI command to launch an instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.xlarge \
  --key-name your-key-pair \
  --security-groups easypost-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=EasyPost-Production}]'
```

### 2. Instance Specifications (Recommended)

```
Instance Type:      t3.xlarge (4 vCPU, 16 GB RAM)
Root Volume:        100 GB gp3 (General Purpose SSD)
Additional Volume:  500 GB gp3 (for media & backups)
OS:                 Ubuntu 22.04 LTS or Amazon Linux 2
Region:             Choose based on your target audience
```

### 3. Security Group Configuration

```
Inbound Rules:
  - Port 22 (SSH): From your IP only
  - Port 80 (HTTP): From 0.0.0.0/0 (will redirect to HTTPS)
  - Port 443 (HTTPS): From 0.0.0.0/0
  - Port 5432 (PostgreSQL): From same VPC only (if internal)
  - Port 6379 (Redis): From same VPC only

Outbound Rules:
  - All traffic to 0.0.0.0/0 (for package downloads, API calls)
```

### 4. Connect to Instance

```bash
chmod 400 your-key-pair.pem
ssh -i your-key-pair.pem ubuntu@your-elastic-ip
```

### 5. Update System

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
  curl \
  wget \
  git \
  htop \
  net-tools \
  build-essential \
  libssl-dev \
  libffi-dev
```

---

## Environment Configuration

### 1. Create `.env` File

```bash
# SSH into your instance and create the .env file
cd /home/ubuntu
mkdir -p easypost
cd easypost

# Create .env file with all required variables
cat > .env << 'EOF'
# ===== Database Configuration =====
POSTGRES_DB=easypost
POSTGRES_USER=easypost_admin
POSTGRES_PASSWORD=$(openssl rand -base64 32)  # Generate secure password
POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=C --lc-ctype=C"

# ===== Redis Configuration =====
REDIS_PASSWORD=$(openssl rand -base64 32)  # Generate secure password

# ===== WAHA (WhatsApp) Configuration =====
WAHA_API_KEY=$(openssl rand -base64 32)
WAHA_SESSION=easypost_session
WAHA_ENGINE=WEBJS
WAHA_START_SESSION=true
WAHA_RESTART_SESSION_ON_TEARDOWN=true
WAHA_DEBUG=false
WAHA_HOST=0.0.0.0
WAHA_PORT=8080

# ===== OpenAI Configuration =====
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7

# ===== AWS Configuration =====
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=easypost-production-bucket

# ===== Clerk Authentication =====
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# ===== Security Keys (GENERATE NEW FOR PRODUCTION) =====
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 32)

# ===== Application Configuration =====
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===== Frontend Configuration =====
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
VITE_CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud
VITE_ENVIRONMENT=production
VITE_APP_NAME=EasyPost AI
VITE_DEBUG=false

# ===== Monitoring & Logging =====
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_KEY=your-new-relic-key

# ===== MCP Server =====
MCP_SERVER_URL=http://mcp-server:9000
MCP_PORT=9000

# ===== Build Targets =====
BUILD_TARGET=production
EOF
```

### 2. Secure the `.env` File

```bash
# Restrict file permissions
chmod 600 .env

# Only allow current user to read
sudo chown ubuntu:ubuntu .env
```

### 3. Generate Secure Passwords

```bash
# Generate strong random passwords
echo "Database Password: $(openssl rand -base64 32)"
echo "Redis Password: $(openssl rand -base64 32)"
echo "WAHA API Key: $(openssl rand -base64 32)"
echo "JWT Secret: $(openssl rand -base64 32)"
echo "Encryption Key: $(openssl rand -base64 32)"
```

---

## Docker & Docker Compose Setup

### 1. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose (latest version)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Repository

```bash
# Clone your EasyPost repository
cd ~/easypost
git clone https://github.com/yourusername/Easy-Post.git .

# Or if you want to push code using rsync
# On your local machine:
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  /path/to/Easy-Post/ ubuntu@your-ec2-ip:/home/ubuntu/easypost/
```

### 3. Prepare Docker Volumes

```bash
# Create volumes for persistent data
sudo mkdir -p /data/postgres
sudo mkdir -p /data/redis
sudo mkdir -p /data/waha
sudo mkdir -p /data/uploads
sudo mkdir -p /data/backups

# Set proper permissions
sudo chown -R ubuntu:ubuntu /data
chmod -R 755 /data
```

### 4. Configure Docker Daemon (Optional but Recommended)

```bash
# Create docker daemon config for better resource management
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "labels": "easypost"
  },
  "metrics-addr": "0.0.0.0:9323",
  "experimental": true
}
EOF

# Restart Docker daemon
sudo systemctl restart docker
```

---

## Database Initialization

### 1. Initialize PostgreSQL with Docker

```bash
# Create a temporary postgres container to initialize
docker-compose -f docker-compose.yml up postgres -d

# Wait for postgres to be ready
sleep 20

# Run alembic migrations
docker-compose exec backend python -m alembic upgrade head
```

### 2. Create Database Backups Strategy

```bash
# Create a backup script
cat > ~/easypost/backup-database.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/data/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/easypost_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Run backup
docker-compose exec -T postgres pg_dump \
  -U easypost_admin \
  easypost | gzip > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "easypost_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x ~/easypost/backup-database.sh
```

### 3. Set Up Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add this line to backup daily at 2 AM
0 2 * * * /home/ubuntu/easypost/backup-database.sh >> /var/log/easypost-backup.log 2>&1
```

---

## SSL/TLS Certificate Setup

### 1. Install Certbot for Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx

# Or use Docker-based certbot
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d www.yourdomain.com \
  -d api.yourdomain.com
```

### 2. Generate SSL Certificate

```bash
# Using Certbot (interactive)
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -d api.yourdomain.com

# Certificates will be at:
# /etc/letsencrypt/live/yourdomain.com/
```

### 3. Copy Certificates to Application Directory

```bash
# Create ssl directory
mkdir -p ~/easypost/nginx/ssl

# Copy certificates (adjust paths as needed)
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ~/easypost/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ~/easypost/nginx/ssl/
sudo chown ubuntu:ubuntu ~/easypost/nginx/ssl/*
```

### 4. Set Up Auto-Renewal

```bash
# Enable Certbot auto-renewal timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Or add to crontab for renewal before expiry (80 days)
0 0 */60 * * certbot renew --quiet --post-hook "docker-compose -f /home/ubuntu/easypost/docker-compose.yml exec -T nginx nginx -s reload"
```

### 5. Configure Nginx for SSL

Create `~/easypost/nginx/conf.d/ssl.conf`:

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com api.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS upstream
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

upstream mcp {
    server mcp-server:9000;
}

# API server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# App server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Application Deployment

### 1. Start All Services

```bash
cd ~/easypost

# Start services in detached mode
docker-compose -f docker-compose.yml up -d

# Verify all services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 2. Initialize Application Data

```bash
# Run database migrations
docker-compose exec backend python -m alembic upgrade head

# Create initial users/roles (if needed)
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"

# Build frontend for production
docker-compose exec frontend npm run build
```

### 3. Create Systemd Service for Auto-Start

```bash
# Create systemd service file
sudo tee /etc/systemd/system/easypost.service > /dev/null <<EOF
[Unit]
Description=EasyPost Docker Compose Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/easypost
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable easypost.service
sudo systemctl start easypost.service

# Check status
sudo systemctl status easypost.service
```

### 4. Health Check Script

```bash
# Create health check script
cat > ~/easypost/health-check.sh << 'EOF'
#!/bin/bash

echo "=== EasyPost Health Check ==="
echo ""

# Check Docker containers
echo "📦 Docker Containers Status:"
docker-compose ps

echo ""
echo "🏥 Service Health Checks:"

# Backend health
if curl -s http://localhost:8000/health > /dev/null; then
  echo "✅ Backend API: OK"
else
  echo "❌ Backend API: FAILED"
fi

# Frontend health
if curl -s http://localhost:3000 > /dev/null; then
  echo "✅ Frontend: OK"
else
  echo "❌ Frontend: FAILED"
fi

# PostgreSQL health
if docker-compose exec -T postgres pg_isready -U easypost_admin > /dev/null 2>&1; then
  echo "✅ PostgreSQL: OK"
else
  echo "❌ PostgreSQL: FAILED"
fi

# Redis health
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
  echo "✅ Redis: OK"
else
  echo "❌ Redis: FAILED"
fi

# WAHA health
if curl -s http://localhost:8080/api/health > /dev/null; then
  echo "✅ WAHA: OK"
else
  echo "❌ WAHA: FAILED"
fi

echo ""
echo "📊 Disk Usage:"
df -h /data

echo ""
echo "💾 Memory Usage:"
free -h
EOF

chmod +x ~/easypost/health-check.sh
```

---

## Monitoring & Logging

### 1. Configure CloudWatch Agent

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create CloudWatch config
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/lib/docker/containers/*/*-json.log",
            "log_group_name": "/easypost/docker",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/easypost-backup.log",
            "log_group_name": "/easypost/backup",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "metrics_collected": {
      "cpu": {
        "measurement": [{"name": "cpu_usage_idle"}],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": [{"name": "mem_used_percent"}],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [{"name": "used_percent"}],
        "metrics_collection_interval": 60,
        "resources": ["/"]
      }
    }
  }
}
EOF

# Start the CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 2. Enable Docker Logging

Docker logging is configured in `docker-compose.yml` with JSON file driver:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

View logs:

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### 3. Setup Log Rotation

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/easypost > /dev/null <<EOF
/var/log/easypost-*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload easypost > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## Backup & Recovery

### 1. Full System Backup Strategy

```bash
# Create comprehensive backup script
cat > ~/easypost/full-backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="easypost_full_$DATE"

echo "Starting full system backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# 1. Database backup
echo "Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump \
  -U easypost_admin \
  easypost | gzip > "$BACKUP_DIR/$BACKUP_NAME/database.sql.gz"

# 2. Redis backup
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli --rdb /data/redis-dump.rdb
cp /data/redis-dump.rdb "$BACKUP_DIR/$BACKUP_NAME/"

# 3. Media files backup
echo "Backing up media files..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME/media.tar.gz" /data/uploads

# 4. Configuration backup
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME/config.tar.gz" \
  ~/easypost/.env \
  ~/easypost/nginx/conf.d \
  ~/easypost/docker-compose.yml

# 5. Upload to S3
echo "Uploading backup to S3..."
aws s3 cp "$BACKUP_DIR/$BACKUP_NAME" \
  "s3://easypost-backups/$BACKUP_NAME/" \
  --recursive

# Cleanup old local backups (keep 7 days)
find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_NAME"
EOF

chmod +x ~/easypost/full-backup.sh
```

### 2. Add to Cron for Daily Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 1 AM UTC
0 1 * * * /home/ubuntu/easypost/full-backup.sh >> /var/log/easypost-backup.log 2>&1
```

### 3. Recovery Procedure

```bash
# Download backup from S3
aws s3 cp s3://easypost-backups/easypost_full_<DATE>/ ./recovery/ --recursive

# Stop services
docker-compose down

# Restore database
cat recovery/database.sql.gz | gunzip | \
  docker-compose run --rm postgres psql \
  -U easypost_admin \
  -d easypost

# Restore media
tar -xzf recovery/media.tar.gz -C /

# Restore config
tar -xzf recovery/config.tar.gz -C ~/easypost/

# Restart services
docker-compose up -d
```

---

## Troubleshooting

### 1. Container Issues

```bash
# Check if containers are running
docker ps

# View container logs
docker logs container_name

# Restart a specific service
docker-compose restart service_name

# Rebuild a service
docker-compose build --no-cache service_name

# Full restart
docker-compose down
docker-compose up -d
```

### 2. Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec postgres psql -U easypost_admin -d easypost -c "\dt"

# Check if migrations ran
docker-compose exec backend python -m alembic current

# Run migrations manually
docker-compose exec backend python -m alembic upgrade head
```

### 3. Memory Issues

```bash
# Check memory usage
free -h
docker stats

# Limit Docker memory in /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file"
}

# Restart Docker daemon
sudo systemctl restart docker
```

### 4. SSL Certificate Issues

```bash
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -noout -dates

# Test SSL configuration
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

### 5. Port Conflicts

```bash
# Find process using a port
sudo lsof -i :8000
sudo netstat -tlpn | grep 8000

# Kill process
sudo kill -9 <PID>
```

### 6. Network Issues

```bash
# Test connectivity
docker-compose exec backend curl http://postgres:5432

# Check network
docker network ls
docker network inspect easypost-network

# DNS resolution
docker-compose exec backend nslookup postgres
```

---

## Post-Deployment Checklist

- [ ] All containers running and healthy
- [ ] SSL certificate installed and valid
- [ ] Database migrations completed
- [ ] Environment variables properly set
- [ ] S3 bucket access verified
- [ ] Email/notification services configured
- [ ] Database backups configured
- [ ] Monitoring and logging active
- [ ] CloudWatch alarms set up
- [ ] Domain DNS records pointing to EC2 Elastic IP
- [ ] Security groups configured correctly
- [ ] IAM roles and policies attached to EC2
- [ ] Application deployed and tested
- [ ] Performance baseline established

---

## Production Best Practices

### Security
- Use Secrets Manager for sensitive data
- Enable VPC flow logs
- Use Security Groups restrictively
- Enable AWS WAF on CloudFront
- Regularly update Docker images

### Performance
- Use t3.xlarge+ for production
- Consider RDS for PostgreSQL (managed service)
- Use ElastiCache for Redis
- Enable CloudFront CDN
- Use Application Load Balancer

### Cost Optimization
- Right-size instances
- Use Reserved Instances
- Enable CloudWatch cost alarms
- Regular review of unused resources
- Use spot instances for non-critical workloads

### Disaster Recovery
- Test backup restoration regularly
- Maintain off-site backups
- Document recovery procedures
- Setup automated failover
- Regular DR drills

---

## Support & Documentation

- Docker Documentation: https://docs.docker.com/
- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
- FastAPI: https://fastapi.tiangolo.com/
- PostgreSQL: https://www.postgresql.org/docs/

---

## Quick Reference Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Run health checks
./health-check.sh

# Create backup
./full-backup.sh

# Enter container
docker-compose exec service_name bash

# View running processes
docker stats

# Prune unused resources
docker system prune -a

# Check service status
sudo systemctl status easypost

# View recent logs
sudo journalctl -u easypost -n 100
```

---

**Last Updated**: 2026-06-16
**Version**: 1.0.0
