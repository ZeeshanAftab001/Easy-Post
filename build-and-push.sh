#!/bin/bash
# Master Build & Push Script for EasyPost Multi-Image Stack
# Usage: ./build-and-push.sh

set -e

# Configuration
DOCKER_USER="zeeshanaftababbasi"
VERSION="latest"

echo "------------------------------------------------"
echo "🚀 Starting Master Build for EasyPost Stack"
echo "------------------------------------------------"

# 1. Build Backend (Used for API, Worker, and Beat)
echo "📦 Building Backend..."
docker build -t $DOCKER_USER/easypost-backend:$VERSION ./backend --target production

# 2. Build Frontend
echo "🎨 Building Frontend..."
docker build -t $DOCKER_USER/easypost-frontend:$VERSION ./frontend --target production

# 3. Build MCP Server
echo "⚙️ Building MCP Server..."
docker build -t $DOCKER_USER/easypost-mcp:$VERSION ./mcp-server

# 4. Build Nginx Proxy
echo "🐘 Building Nginx Proxy..."
docker build -t $DOCKER_USER/easypost-nginx:$VERSION ./nginx

echo "------------------------------------------------"
echo "✅ Build Complete. Starting Push to Docker Hub..."
echo "------------------------------------------------"

docker push $DOCKER_USER/easypost-backend:$VERSION
docker push $DOCKER_USER/easypost-frontend:$VERSION
docker push $DOCKER_USER/easypost-mcp:$VERSION
docker push $DOCKER_USER/easypost-nginx:$VERSION

echo "------------------------------------------------"
echo "🎉 All images successfully pushed!"
echo "User: $DOCKER_USER"
echo "Images: backend, frontend, mcp, nginx"
echo "------------------------------------------------"
