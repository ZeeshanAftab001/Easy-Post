#!/bin/bash

# EasyPost AWS EC2 Deployment Script
# This script automates the setup of an EC2 instance for EasyPost production deployment
# Usage: curl https://raw.githubusercontent.com/yourusername/Easy-Post/main/deploy.sh | bash

set -e

echo "🚀 Starting EasyPost Deployment Setup..."

# ============================================
# 1. System Updates
# ============================================
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y \
    curl \
    wget \
    git \
    htop \
    net-tools \
    build-essential \
    libssl-dev \
    libffi-dev \
    jq \
    certbot \
    python3-certbot-nginx

# ============================================
# 2. Docker Installation
# ============================================
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

echo "Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# ============================================
# 3. AWS CLI Installation
# ============================================
echo "☁️ Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
aws --version

# ============================================
# 4. Directory Setup
# ============================================
echo "📁 Setting up directories..."
cd /home/ubuntu
mkdir -p easypost
cd easypost

# Create data directories
sudo mkdir -p /data/{postgres,redis,waha,uploads,backups}
sudo chown -R ubuntu:ubuntu /data
chmod -R 755 /data

# ============================================
# 5. Clone Repository
# ============================================
echo "📥 Cloning repository..."
if [ -d ".git" ]; then
    echo "Repository already cloned"
else
    git clone https://github.com/yourusername/Easy-Post.git /tmp/easypost-repo
    cp -r /tmp/easypost-repo/* /tmp/easypost-repo/.* . 2>/dev/null || true
    rm -rf /tmp/easypost-repo
fi

# ============================================
# 6. Environment Setup
# ============================================
echo "⚙️ Setting up environment..."

# Check if .env exists
if [ -f ".env" ]; then
    echo "ℹ️ .env file already exists"
else
    cp .env.production.example .env
    echo "🔒 Created .env file - PLEASE EDIT WITH YOUR PRODUCTION VALUES"
    echo "💡 Run: nano /home/ubuntu/easypost/.env"
    
    # Generate secure values
    echo ""
    echo "🔐 Generated secure values for .env:"
    echo "PostgreSQL Password: $(openssl rand -base64 32)"
    echo "Redis Password: $(openssl rand -base64 32)"
    echo "JWT Secret: $(openssl rand -base64 32)"
fi

chmod 600 .env

# ============================================
# 7. Docker Volume Setup
# ============================================
echo "💾 Creating Docker volumes..."
docker volume create postgres_data 2>/dev/null || true
docker volume create redis_data 2>/dev/null || true
docker volume create waha_data 2>/dev/null || true
docker volume create media_uploads 2>/dev/null || true
docker volume create static_files 2>/dev/null || true
docker volume create mcp_data 2>/dev/null || true

# ============================================
# 8. SSL Certificate Setup (Optional)
# ============================================
echo "🔐 SSL Certificate Setup"
echo "For production, you'll need a domain name and SSL certificate."
echo "Instructions:"
echo "1. Point your domain to this EC2 instance's Elastic IP"
echo "2. Run: sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com"
echo "3. Copy certificates to: nginx/ssl/"

# ============================================
# 9. CloudWatch Agent Setup
# ============================================
echo "📊 Setting up CloudWatch monitoring..."

# Download CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

echo "CloudWatch agent installed. Configure with your AWS account credentials."

# ============================================
# 10. Nginx Configuration
# ============================================
echo "🌐 Preparing Nginx configuration..."

mkdir -p nginx/ssl
mkdir -p nginx/conf.d

echo "⚠️ IMPORTANT: Update nginx/conf.d/default.conf with your domain names"
echo "Search for 'yourdomain.com' and replace with your actual domain"

# ============================================
# 11. Final Configuration
# ============================================
echo ""
echo "✅ System setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit .env with your production secrets:"
echo "   nano /home/ubuntu/easypost/.env"
echo ""
echo "2. Set up SSL certificate:"
echo "   sudo certbot certonly --standalone -d yourdomain.com"
echo ""
echo "3. Update Nginx configuration:"
echo "   nano /home/ubuntu/easypost/nginx/conf.d/default.conf"
echo ""
echo "4. Start the application:"
echo "   cd /home/ubuntu/easypost"
echo "   docker-compose up -d"
echo ""
echo "5. Verify health status:"
echo "   docker-compose ps"
echo "   ./health-check.sh"
echo ""
echo "📚 For more details, see EC2_DEPLOYMENT_GUIDE.md"
echo ""

# ============================================
# 12. Create Convenience Scripts
# ============================================
cat > start.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/easypost
docker-compose up -d
echo "✅ EasyPost started"
EOF

cat > stop.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/easypost
docker-compose down
echo "⛔ EasyPost stopped"
EOF

cat > logs.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/easypost
docker-compose logs -f "$@"
EOF

cat > restart.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/easypost
docker-compose restart "$@"
echo "🔄 Restarted"
EOF

chmod +x start.sh stop.sh logs.sh restart.sh

echo ""
echo "🎉 Deployment script complete!"
