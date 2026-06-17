# Docker Image Build & Push Guide

## Overview

This guide explains how to build EasyPost Docker images and push them to Docker Hub.

---

## Prerequisites

### 1. Install Docker
```bash
# macOS / Windows
Download from: https://www.docker.com/products/docker-desktop/

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Create Docker Hub Account
1. Go to https://hub.docker.com
2. Sign up for free account
3. Create a repository for EasyPost images (optional - images can be in your personal namespace)

### 3. Login to Docker Hub
```bash
docker login
# Enter your Docker Hub username and password
```

---

## Quick Build & Push

### Option 1: Automated Script (Recommended)

```bash
# Make script executable
chmod +x build-and-push.sh

# Run the script
./build-and-push.sh

# The script will:
# 1. Check Docker is installed and running
# 2. Build all 4 images for production
# 3. Ask if you want to push to Docker Hub
# 4. Push all images with tags
```

### Option 2: Manual Build & Push

```bash
# Set your Docker Hub username
DOCKER_HUB_USERNAME="zeeshanaabbasi"
IMAGE_PREFIX="${DOCKER_HUB_USERNAME}/easypost"

# Build backend
docker build --target production \
  -t ${IMAGE_PREFIX}-backend:latest \
  -f backend/Dockerfile backend/

# Build frontend
docker build --target production \
  -t ${IMAGE_PREFIX}-frontend:latest \
  -f frontend/Dockerfile frontend/

# Build nginx
docker build -t ${IMAGE_PREFIX}-nginx:latest \
  -f nginx/Dockerfile nginx/

# Build MCP server
docker build -t ${IMAGE_PREFIX}-mcp-server:latest \
  -f mcp-server/Dockerfile mcp-server/

# Push all images
docker push ${IMAGE_PREFIX}-backend:latest
docker push ${IMAGE_PREFIX}-frontend:latest
docker push ${IMAGE_PREFIX}-nginx:latest
docker push ${IMAGE_PREFIX}-mcp-server:latest
```

---

## Build Targets Explained

### Production Build (Default)
Optimized for production deployment with:
- Minimal image size
- Non-root user for security
- Resource limits configured
- Health checks enabled

```bash
docker build --target production -t myimage:latest .
```

### Development Build (With Hot Reload)
For local development with live code reloading:

```bash
docker build --target development -t myimage:dev .
```

---

## Image Sizes

Expected compressed sizes after build:

| Image | Size | Notes |
|-------|------|-------|
| Backend | ~400-500 MB | Python 3.11, FastAPI, dependencies |
| Frontend | ~150-200 MB | Node 20, React build output |
| Nginx | ~30-40 MB | Alpine base, minimal footprint |
| MCP Server | ~350-400 MB | Python runtime, dependencies |

---

## Tagging Strategies

### Standard Tags
```bash
# Latest production
docker tag myimage:latest zeeshanaabbasi/easypost-backend:latest

# Version-specific
docker tag myimage:latest zeeshanaabbasi/easypost-backend:1.0.0

# Git commit hash
docker tag myimage:latest zeeshanaabbasi/easypost-backend:abc123def

# Environment
docker tag myimage:latest zeeshanaabbasi/easypost-backend:production
```

### Recommended Tagging
```bash
# Always tag with multiple tags
docker build -t zeeshanaabbasi/easypost-backend:latest \
             -t zeeshanaabbasi/easypost-backend:production \
             -t zeeshanaabbasi/easypost-backend:v1.0.0 \
             -f backend/Dockerfile backend/
```

---

## Using Pre-built Images

### Option 1: docker-compose.hub.yml (Recommended)

```bash
# Use pre-built images from Docker Hub
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d

# Set Docker Hub username in .env
DOCKER_HUB_USERNAME=zeeshanaabbasi
```

### Option 2: Inline in docker-compose

```yaml
services:
  backend:
    image: zeeshanaabbasi/easypost-backend:latest
    # ... rest of config
```

### Option 3: Pull and Run Individual Image

```bash
docker pull zeeshanaabbasi/easypost-backend:latest
docker run -it zeeshanaabbasi/easypost-backend:latest bash
```

---

## Common Commands

### View Images
```bash
# List all local images
docker images

# List EasyPost images only
docker images | grep easypost

# Show image size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Inspect Images
```bash
# View image details
docker inspect zeeshanaabbasi/easypost-backend:latest

# View image history (layers)
docker history zeeshanaabbasi/easypost-backend:latest

# View image size breakdown
docker history --human zeeshanaabbasi/easypost-backend:latest
```

### Remove Images
```bash
# Remove single image
docker rmi zeeshanaabbasi/easypost-backend:latest

# Remove all untagged images
docker image prune

# Remove all unused images (⚠️ be careful)
docker image prune -a

# Force remove image
docker rmi -f zeeshanaabbasi/easypost-backend:latest
```

### Search Images
```bash
# Search Docker Hub
docker search zeeshanaabbasi

# Search specific registry
docker search myregistry.azurecr.io/easypost
```

---

## Pushing to Different Registries

### Docker Hub (Default)
```bash
# Tag for Docker Hub
docker tag myimage:latest zeeshanaabbasi/easypost-backend:latest

# Push
docker push zeeshanaabbasi/easypost-backend:latest
```

### AWS ECR (Elastic Container Registry)
```bash
# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag for ECR
docker tag myimage:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/easypost-backend:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/easypost-backend:latest
```

### GitHub Container Registry (ghcr.io)
```bash
# Login with GitHub token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag for GitHub
docker tag myimage:latest ghcr.io/username/easypost-backend:latest

# Push
docker push ghcr.io/username/easypost-backend:latest
```

### Private Registry
```bash
# Login to private registry
docker login myregistry.com

# Tag for private registry
docker tag myimage:latest myregistry.com/easypost-backend:latest

# Push
docker push myregistry.com/easypost-backend:latest
```

---

## Optimization Tips

### Reduce Image Size

1. **Use Alpine Base Images**
   Already configured in our Dockerfiles

2. **Multi-stage Builds**
   Separates build dependencies from runtime
   Already implemented in all Dockerfiles

3. **Minimal Layers**
   Combine RUN commands where possible

4. **Remove Build Dependencies**
   Only include production dependencies

### Example Optimization
```dockerfile
# Bad: 500 MB image
FROM python:3.11
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r requirements.txt
COPY . .

# Good: 300 MB image (with multi-stage)
FROM python:3.11 as builder
RUN pip install -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /usr/local /usr/local
COPY . .
```

---

## Troubleshooting

### Build Fails with "permission denied"
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group membership (or restart terminal)
newgrp docker
```

### Push Fails with "authentication required"
```bash
# Login to Docker Hub
docker login

# Verify login
docker whoami

# If push still fails, ensure correct username in image name
docker push zeeshanaabbasi/easypost-backend:latest
```

### Out of Disk Space
```bash
# Clean up Docker system
docker system prune -a

# Remove specific image
docker rmi zeeshanaabbasi/easypost-backend:old-tag

# Show disk usage
docker system df
```

### Image Won't Run ("image not found")
```bash
# Check if image exists locally
docker images | grep easypost

# Pull from Docker Hub if not found
docker pull zeeshanaabbasi/easypost-backend:latest

# Verify image runs
docker run -it zeeshanaabbasi/easypost-backend:latest /bin/bash
```

### Slow Build Times
```bash
# Build with progress output
docker build --progress=plain -t myimage:latest .

# Use buildkit for faster builds (Docker 18.09+)
DOCKER_BUILDKIT=1 docker build -t myimage:latest .

# Parallel stage builds (Docker 20.10+)
docker build --build-context mycontext=. -t myimage:latest .
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main, production]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ secrets.DOCKER_HUB_USERNAME }}/easypost-backend:latest
```

---

## Best Practices

✅ **DO:**
- Use multi-stage builds for smaller images
- Tag images with version numbers and dates
- Keep Dockerfiles clean and readable
- Document environment variables
- Use health checks
- Test images before pushing
- Keep dependencies up to date
- Use specific base image versions (not `latest`)

❌ **DON'T:**
- Use root user in production images
- Include secrets in Dockerfiles
- Use `latest` tag in production
- Keep large build artifacts in images
- Run multiple services in one container
- Build images without tests
- Push untested images to registry

---

## Next Steps

1. **Update Docker Hub Username** in `build-and-push.sh`
2. **Run the build script**: `./build-and-push.sh`
3. **Test images**: `docker run -it zeeshanaabbasi/easypost-backend:latest`
4. **Deploy to EC2**: Use `docker-compose.hub.yml` for production
5. **Monitor images**: Check Docker Hub dashboard

---

## Resources

- Docker Documentation: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
- Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Multi-stage Builds: https://docs.docker.com/build/building/multi-stage/
- BuildKit: https://docs.docker.com/build/architecture/

---

**Last Updated**: 2026-06-16
