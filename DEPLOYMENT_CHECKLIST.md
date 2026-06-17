# AWS EC2 Deployment Quick Start Checklist

## Pre-Deployment

- [ ] AWS Account created and active
- [ ] IAM user with appropriate permissions created
- [ ] EC2 keypair downloaded and saved securely
- [ ] Security Group created with inbound rules (22, 80, 443, 5432, 6379)
- [ ] Elastic IP allocated
- [ ] Domain name registered and ready
- [ ] All production credentials and API keys collected

## EC2 Instance Setup

- [ ] Launch EC2 instance (t3.xlarge or larger)
- [ ] Select Ubuntu 22.04 LTS or Amazon Linux 2
- [ ] Assign 100GB root volume + 500GB data volume
- [ ] Attach Security Group
- [ ] Attach Elastic IP
- [ ] Connect via SSH successfully
- [ ] Run system updates: `sudo apt update && sudo apt upgrade -y`

## Docker Setup

- [ ] Install Docker using provided script
- [ ] Install Docker Compose
- [ ] Add current user to docker group
- [ ] Verify Docker installation: `docker --version`
- [ ] Verify Docker Compose installation: `docker-compose --version`

## Application Deployment

- [ ] Clone repository or upload code
- [ ] Copy `.env.production.example` to `.env`
- [ ] Update `.env` with production values:
  - [ ] Database credentials (PostgreSQL)
  - [ ] Redis password
  - [ ] WAHA API key
  - [ ] OpenAI API key
  - [ ] AWS credentials and S3 bucket
  - [ ] Clerk authentication keys
  - [ ] JWT secret and encryption keys
  - [ ] Domain names in CORS origins
- [ ] Update Nginx configuration with your domain
- [ ] Create Docker volumes
- [ ] Build and start containers: `docker-compose up -d`
- [ ] Run database migrations: `docker-compose exec backend python -m alembic upgrade head`

## SSL/TLS Setup

- [ ] Install Certbot: `sudo apt install certbot python3-certbot-nginx`
- [ ] Request SSL certificate: `sudo certbot certonly --standalone -d yourdomain.com`
- [ ] Copy certificates to nginx/ssl directory
- [ ] Update nginx configuration with certificate paths
- [ ] Test SSL configuration: `sudo certbot renew --dry-run`
- [ ] Verify HTTPS access
- [ ] Set up auto-renewal with cron or systemd timer

## DNS Configuration

- [ ] Point domain to Elastic IP in DNS provider
- [ ] Wait for DNS propagation (can take up to 48 hours)
- [ ] Test domain resolution: `nslookup yourdomain.com`
- [ ] Verify API endpoint: `curl https://api.yourdomain.com/health`

## Monitoring & Logging

- [ ] Set up CloudWatch Agent
- [ ] Configure Docker logging driver
- [ ] Create CloudWatch alarms for:
  - [ ] High CPU usage
  - [ ] High memory usage
  - [ ] Disk space
  - [ ] Container crashes
- [ ] Set up log rotation
- [ ] Enable CloudWatch Logs

## Backup & Recovery

- [ ] Create database backup script
- [ ] Test backup creation: `./backup-database.sh`
- [ ] Create full system backup script: `./full-backup.sh`
- [ ] Set up cron jobs for automated backups:
  - [ ] Daily database backup at 2 AM
  - [ ] Weekly full backup
- [ ] Create S3 bucket for backup storage
- [ ] Test recovery procedure
- [ ] Document recovery steps

## Security Hardening

- [ ] Restrict SSH access to specific IPs
- [ ] Disable root login
- [ ] Set up firewall rules properly
- [ ] Enable AWS VPC Flow Logs
- [ ] Enable EC2 detailed monitoring
- [ ] Set up AWS CloudTrail for audit logging
- [ ] Review security group rules
- [ ] Rotate AWS access keys regularly
- [ ] Use IAM roles instead of embedded credentials
- [ ] Enable MFA for AWS console

## Application Verification

- [ ] All containers running: `docker-compose ps`
- [ ] No container restart loops
- [ ] Health check endpoints responding:
  - [ ] Backend: `https://api.yourdomain.com/health`
  - [ ] Frontend: `https://yourdomain.com`
  - [ ] MCP Server: `https://mcp.yourdomain.com/health`
- [ ] Database connected and migrations complete
- [ ] Redis cache working
- [ ] WAHA WhatsApp service active
- [ ] Frontend loads correctly
- [ ] API requests working
- [ ] WebSocket connections working
- [ ] File uploads working
- [ ] Notifications sending

## Performance Testing

- [ ] Load test the application
- [ ] Monitor resource usage during load
- [ ] Test with expected peak traffic
- [ ] Verify autoscaling (if configured)
- [ ] Document performance baseline

## Maintenance Setup

- [ ] Create systemd service for auto-start
- [ ] Enable systemd service: `sudo systemctl enable easypost`
- [ ] Create convenience scripts (start.sh, stop.sh, logs.sh)
- [ ] Set up log rotation
- [ ] Create health check monitoring script
- [ ] Document all scripts and their usage

## Documentation & Knowledge Transfer

- [ ] Create deployment runbook
- [ ] Document all credentials and secrets (securely)
- [ ] Create incident response procedures
- [ ] Document common troubleshooting steps
- [ ] Create upgrade procedures
- [ ] Set up team access (IAM users, SSH keys)
- [ ] Create on-call rotation documentation
- [ ] Document SLAs and monitoring thresholds

## Post-Deployment Monitoring (First 24 Hours)

- [ ] Monitor container restarts
- [ ] Monitor error logs
- [ ] Monitor resource usage patterns
- [ ] Verify backup jobs ran successfully
- [ ] Monitor database query performance
- [ ] Test user registration and login
- [ ] Test social media posting functionality
- [ ] Monitor WhatsApp webhook connectivity

## Optimization & Scaling

- [ ] Optimize Docker images (remove unused layers)
- [ ] Consider RDS for managed PostgreSQL
- [ ] Consider ElastiCache for Redis
- [ ] Set up CloudFront for CDN
- [ ] Consider Application Load Balancer
- [ ] Set up auto-scaling groups (if needed)
- [ ] Optimize database queries
- [ ] Implement caching strategies

## Ongoing Maintenance

- [ ] Weekly security updates
- [ ] Monthly dependency updates
- [ ] Quarterly disaster recovery drills
- [ ] Regular backup integrity checks
- [ ] Monthly cost review
- [ ] Performance baseline monitoring
- [ ] Security scanning and penetration testing
- [ ] Documentation updates

---

## Support Resources

- EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Docker Documentation: https://docs.docker.com/
- Let's Encrypt: https://letsencrypt.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation
- Nginx: https://nginx.org/en/docs/

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Notes**: 

