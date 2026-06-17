# EasyPost AWS EC2 Deployment - Quick Reference

## 📋 Quick Start (5 Steps)

### Step 1: Launch EC2 Instance
```bash
# Through AWS Console:
1. Go to EC2 Dashboard → Launch Instance
2. Select: Ubuntu 22.04 LTS (or Amazon Linux 2)
3. Instance Type: t3.xlarge (4 vCPU, 16 GB RAM)
4. Storage: 100 GB root + 500 GB data volume
5. Security Group: Allow ports 22, 80, 443, 5432, 6379
6. Key Pair: Download and save securely
7. Assign Elastic IP
```

### Step 2: Connect & Run Deployment Script
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-elastic-ip

# Run automated setup
curl -fsSL https://raw.githubusercontent.com/yourusername/Easy-Post/main/deploy.sh | bash
```

### Step 3: Configure Environment
```bash
# Edit production configuration
nano /home/ubuntu/easypost/.env

# Update with your values:
# - POSTGRES_PASSWORD, REDIS_PASSWORD (generate new)
# - OPENAI_API_KEY (from OpenAI)
# - AWS credentials and S3 bucket
# - CLERK authentication keys
# - Domain names
```

### Step 4: Set Up SSL Certificate
```bash
# Point your domain to Elastic IP first, then:
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -d api.yourdomain.com

# Copy certificates
mkdir -p /home/ubuntu/easypost/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
  /home/ubuntu/easypost/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem \
  /home/ubuntu/easypost/nginx/ssl/
sudo chown ubuntu:ubuntu /home/ubuntu/easypost/nginx/ssl/*
```

### Step 5: Start Application
```bash
# Navigate to project
cd /home/ubuntu/easypost

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify health
docker-compose ps
./health-check.sh

# Test endpoints
curl https://api.yourdomain.com/health
curl https://yourdomain.com
```

---

## 📁 Key Files for Deployment

| File | Purpose |
|------|---------|
| `EC2_DEPLOYMENT_GUIDE.md` | Comprehensive deployment guide (100+ pages) |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist for deployment |
| `.env.production.example` | Template for production environment variables |
| `docker-compose.yml` | Main Docker Compose configuration |
| `docker-compose.prod.yml` | Production overrides |
| `deploy.sh` | Automated setup script |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend container image |
| `nginx/Dockerfile` | Nginx container image |
| `nginx/nginx.conf` | Nginx main configuration |
| `nginx/conf.d/default.conf` | Nginx routing configuration |
| `mcp-server/Dockerfile` | MCP server container image |

---

## 🚀 Common Commands

### Application Management
```bash
cd /home/ubuntu/easypost

# Start application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Stop application
docker-compose down

# Restart services
docker-compose restart backend
docker-compose restart frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Health check
./health-check.sh

# Database migrations
docker-compose exec backend python -m alembic upgrade head
```

### Backup & Restore
```bash
# Create database backup
./backup-database.sh

# Create full system backup
./full-backup.sh

# Restore from backup
# See EC2_DEPLOYMENT_GUIDE.md for detailed restore procedure
```

### SSL Certificate Management
```bash
# Renew certificate
sudo certbot renew

# Test auto-renewal
sudo certbot renew --dry-run

# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -noout -dates
```

### Monitoring
```bash
# Container stats
docker stats

# Memory usage
free -h

# Disk usage
df -h /data

# View container logs
docker logs container_name
docker logs -f container_name  # Follow logs

# Systemd status
sudo systemctl status easypost
sudo systemctl restart easypost
```

---

## 🔐 Security Essentials

### AWS Security
- [ ] Enable MFA on AWS root account
- [ ] Use IAM user for deployments (not root)
- [ ] Enable CloudTrail for audit logging
- [ ] Regular security group reviews
- [ ] Rotate AWS access keys every 90 days

### Application Security
- [ ] Generate strong `.env` secrets: `openssl rand -base64 32`
- [ ] Enable HTTPS/SSL everywhere
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade -y`
- [ ] Monitor for unauthorized access
- [ ] Keep backups encrypted

### Data Protection
- [ ] Enable database encryption
- [ ] Encrypt S3 bucket
- [ ] Enable versioning on S3
- [ ] Regular backup testing
- [ ] Off-site backup storage

---

## 📊 Monitoring & Alarms

### CloudWatch Metrics to Monitor
```
- CPU Utilization (Alert: >80%)
- Memory Usage (Alert: >85%)
- Disk Space (Alert: >90%)
- Network In/Out (Baseline trending)
- Container Restart Count (Alert: >0 in 5 min)
- HTTP 5xx Errors (Alert: >1% of requests)
- Database Connection Pool (Alert: >80% utilized)
- Redis Memory (Alert: >85% utilized)
```

### Setting Up Alarms
```bash
# Use AWS Console or AWS CLI
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## 🐛 Troubleshooting Quick Guide

### Container won't start
```bash
# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend

# Rebuild container
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Database connection issues
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U easypost_admin -c "\l"

# Check connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.url)"

# Run migrations
docker-compose exec backend python -m alembic upgrade head
```

### SSL certificate issues
```bash
# Check certificate
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# Test Nginx config
docker-compose exec nginx nginx -t

# Reload Nginx
docker-compose exec nginx nginx -s reload
```

### Memory issues
```bash
# Check usage
docker stats
free -h

# View memory by container
docker ps --format="table {{.Names}}\t{{.Size}}"

# Increase Docker memory limit in /etc/docker/daemon.json
```

### Port conflicts
```bash
# Find process using port
sudo lsof -i :8000
sudo netstat -tlpn | grep 8000

# Kill process
sudo kill -9 <PID>
```

---

## 📈 Performance Optimization

### Database
```sql
-- Add indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM posts WHERE user_id = 1;
```

### Redis Caching
```python
# Implement cache for frequently accessed data
from redis import Redis
redis_client = Redis(host='redis', port=6379, db=1)
redis_client.setex('user:123', 3600, json.dumps(user_data))
```

### Frontend Optimization
- Use CDN (CloudFront)
- Enable gzip compression
- Minify CSS/JS
- Implement lazy loading
- Optimize images

---

## 🔄 Upgrade Procedure

### Update Docker Images
```bash
cd /home/ubuntu/easypost

# Pull latest images
docker-compose pull

# Rebuild with new images
docker-compose build --no-cache

# Start with zero downtime (rolling update)
docker-compose up -d backend frontend
```

### Database Migrations
```bash
# Create backup before migration
./backup-database.sh

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Verify migration
docker-compose exec backend python -m alembic current
```

---

## 📞 Support & Resources

- **AWS Support**: https://aws.amazon.com/support/
- **Docker Documentation**: https://docs.docker.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/documentation
- **Let's Encrypt**: https://letsencrypt.org/

---

## 🆘 Emergency Procedures

### System Down
1. Check EC2 instance status
2. SSH and check container status: `docker-compose ps`
3. Check logs: `docker-compose logs`
4. Restart services: `docker-compose restart`
5. If still down, restore from backup

### Data Loss
1. Stop all containers: `docker-compose down`
2. Find latest backup: `ls -la /data/backups/`
3. Follow restore procedure in EC2_DEPLOYMENT_GUIDE.md
4. Verify data integrity
5. Restart services

### Compromised Security
1. Rotate all credentials immediately
2. Review CloudTrail logs
3. Disable compromised IAM users
4. Update all `.env` secrets
5. Restart all containers with new credentials
6. Backup for forensics before rebuilding

---

## 💡 Pro Tips

1. **Always test on staging first** - Don't deploy directly to production
2. **Keep backups** - Test restore procedures regularly
3. **Monitor CloudWatch** - Set up alarms for critical metrics
4. **Use logs** - Always check logs before asking for help
5. **Automate backups** - Use cron for scheduled backups
6. **Document changes** - Keep changelog for all modifications
7. **Security updates** - Update system regularly
8. **Database maintenance** - Run VACUUM and ANALYZE periodically

---

**Last Updated**: 2026-06-16
**Version**: 1.0.0
