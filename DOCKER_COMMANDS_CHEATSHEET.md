# Docker Commands Quick Reference for EasyPost

## 🎯 Most Common Commands

### Build Images
```bash
# Interactive builder (recommended for first time)
./build-docker.sh

# OR: Automated build all
./build-and-push.sh

# OR: Manual build backend
docker build --target production -t zeeshanaabbasi/easypost-backend:latest -f backend/Dockerfile backend/
```

### Push to Docker Hub
```bash
# Push all images
docker push zeeshanaabbasi/easypost-backend:latest
docker push zeeshanaabbasi/easypost-frontend:latest
docker push zeeshanaabbasi/easypost-nginx:latest
docker push zeeshanaabbasi/easypost-mcp-server:latest

# Or: use docker-compose to push everything at once
docker-compose push
```

### Deploy with Docker Compose
```bash
# Use local images
docker-compose up -d

# Use pre-built Docker Hub images
docker-compose -f docker-compose.hub.yml up -d

# Use production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### View & Manage Images
```bash
# List all EasyPost images
docker images | grep easypost

# Show image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep easypost

# Remove image
docker rmi zeeshanaabbasi/easypost-backend:latest

# Remove all unused images
docker image prune -a
```

---

## 🔧 Useful Commands

### Container Management
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs container_name
docker logs -f container_name          # Follow logs
docker logs --tail 100 container_name  # Last 100 lines

# Execute command in container
docker exec -it container_name bash

# Stop container
docker stop container_name

# Start container
docker start container_name

# Restart container
docker restart container_name

# Remove container
docker rm container_name
```

### Image Inspection
```bash
# View image details
docker inspect zeeshanaabbasi/easypost-backend:latest

# View image layers (build steps)
docker history zeeshanaabbasi/easypost-backend:latest

# View build history with sizes
docker history --human zeeshanaabbasi/easypost-backend:latest

# Search Docker Hub
docker search easypost
docker search zeeshanaabbasi
```

### Docker Hub Operations
```bash
# Login to Docker Hub
docker login

# Show current user
docker whoami

# Logout from Docker Hub
docker logout

# Pull image
docker pull zeeshanaabbasi/easypost-backend:latest

# Tag image
docker tag zeeshanaabbasi/easypost-backend:latest zeeshanaabbasi/easypost-backend:v1.0.0

# Push image
docker push zeeshanaabbasi/easypost-backend:latest
docker push zeeshanaabbasi/easypost-backend:v1.0.0
```

### Testing & Debugging
```bash
# Run container interactively
docker run -it zeeshanaabbasi/easypost-backend:latest /bin/bash

# Run and remove after exit
docker run --rm -it zeeshanaabbasi/easypost-backend:latest /bin/bash

# Run with environment variables
docker run -e DATABASE_URL="postgresql://..." zeeshanaabbasi/easypost-backend:latest

# Run with port mapping
docker run -p 8000:8000 zeeshanaabbasi/easypost-backend:latest

# Run in background
docker run -d zeeshanaabbasi/easypost-backend:latest

# View container stats
docker stats

# Check if container is healthy
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Docker Compose Commands
```bash
# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs
docker-compose logs -f backend          # Follow backend logs
docker-compose logs --tail 50 backend   # Last 50 lines

# Execute in running service
docker-compose exec backend bash
docker-compose exec backend python -c "print('hello')"

# Restart service
docker-compose restart backend

# Rebuild service
docker-compose build --no-cache backend

# Push images (if they're built locally)
docker-compose push

# Pull images (if using docker-compose.hub.yml)
docker-compose -f docker-compose.hub.yml pull
```

### System & Cleanup
```bash
# Check Docker system disk usage
docker system df

# Clean up unused resources
docker system prune          # Remove unused images, containers, networks
docker system prune -a       # Remove all unused (careful!)

# Remove all stopped containers
docker container prune

# Remove all dangling images
docker image prune

# Remove all unused volumes
docker volume prune

# Check Docker info
docker info

# View Docker version
docker version
```

---

## 🚀 Deployment Workflows

### Build & Deploy Flow
```bash
# 1. Verify setup
./verify-docker-setup.sh

# 2. Build images
./build-docker.sh

# 3. Test images
docker run -it zeeshanaabbasi/easypost-backend:latest /bin/bash

# 4. Push to Docker Hub
docker push zeeshanaabbasi/easypost-backend:latest
docker push zeeshanaabbasi/easypost-frontend:latest
docker push zeeshanaabbasi/easypost-nginx:latest
docker push zeeshanaabbasi/easypost-mcp-server:latest

# 5. Deploy on EC2
scp docker-compose.hub.yml ubuntu@your-ec2:/home/ubuntu/easypost/
scp .env ubuntu@your-ec2:/home/ubuntu/easypost/
ssh ubuntu@your-ec2
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d
```

### Update Deployment
```bash
# 1. Build new version
./build-docker.sh

# 2. Tag with version
docker tag zeeshanaabbasi/easypost-backend:latest zeeshanaabbasi/easypost-backend:v1.1.0

# 3. Push both tags
docker push zeeshanaabbasi/easypost-backend:latest
docker push zeeshanaabbasi/easypost-backend:v1.1.0

# 4. On EC2, pull and restart
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d
```

### Rollback Deployment
```bash
# 1. Check image history
docker images zeeshanaabbasi/easypost-backend

# 2. Update docker-compose.hub.yml to use old version
# Change: image: zeeshanaabbasi/easypost-backend:latest
# To:     image: zeeshanaabbasi/easypost-backend:v1.0.0

# 3. Pull and restart
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d

# 4. Verify
docker-compose ps
docker-compose logs backend
```

---

## 🐛 Common Issues & Solutions

### Issue: "permission denied while trying to connect to Docker daemon"
```bash
# Solution:
sudo usermod -aG docker $USER
newgrp docker
# Or restart terminal/system
```

### Issue: "Docker daemon is not running"
```bash
# Solution (Linux):
sudo systemctl start docker

# Solution (Mac):
open /Applications/Docker.app

# Solution (Windows):
Open Docker Desktop from Start menu
```

### Issue: "no space left on device"
```bash
# Solution:
docker system prune -a      # Clean up
docker volume prune         # Remove volumes
# Or: Increase disk space on EC2
```

### Issue: "image not found"
```bash
# Solution:
docker pull zeeshanaabbasi/easypost-backend:latest
# Or rebuild locally:
docker build -t zeeshanaabbasi/easypost-backend:latest -f backend/Dockerfile backend/
```

### Issue: "port already in use"
```bash
# Solution: Find process using port
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :80

# Kill process
sudo kill -9 <PID>

# Or: Use different port in docker-compose
ports:
  - "9000:8000"
```

### Issue: "container exits immediately"
```bash
# Solution: Check logs
docker logs container_name

# Run interactively to debug
docker run -it zeeshanaabbasi/easypost-backend:latest bash
```

---

## 📊 Docker Cheat Sheet

| Action | Command |
|--------|---------|
| Build image | `docker build -t name:tag .` |
| Run container | `docker run -d -p 8000:8000 name:tag` |
| View images | `docker images` |
| View containers | `docker ps -a` |
| View logs | `docker logs container_name` |
| Stop container | `docker stop container_name` |
| Remove container | `docker rm container_name` |
| Remove image | `docker rmi name:tag` |
| Push to registry | `docker push name:tag` |
| Pull from registry | `docker pull name:tag` |
| List resources | `docker system df` |
| Clean up | `docker system prune -a` |

---

## 🔗 Quick Links

- **Docker Docs**: https://docs.docker.com/
- **Docker Hub**: https://hub.docker.com/
- **Docker CLI**: https://docs.docker.com/engine/reference/commandline/cli/
- **Docker Compose**: https://docs.docker.com/compose/

---

## 💡 Pro Tips

1. **Always test locally first** before pushing
2. **Use `.dockerignore`** to exclude build files
3. **Tag images with versions** (v1.0.0, v1.1.0)
4. **Keep Dockerfiles simple** and readable
5. **Use alpine base images** for smaller sizes
6. **Multi-stage builds** reduce final image size
7. **Check image sizes** before pushing
8. **Read logs carefully** when debugging

---

**Bookmark this page for quick reference!**

Last Updated: 2026-06-16
