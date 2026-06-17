# Docker Build Quick Start Script
# This script guides you through building and pushing Docker images

#!/bin/bash

echo "============================================"
echo "🐳 EasyPost Docker Build & Push"
echo "============================================"
echo ""

# ============================================
# Step 1: Check Prerequisites
# ============================================
echo "📋 Step 1: Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "   Install from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if daemon is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running!"
    echo "   Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is ready"
echo ""

# ============================================
# Step 2: Get Docker Hub Credentials
# ============================================
echo "📋 Step 2: Docker Hub Configuration"
echo ""

# Try to get current Docker Hub user
CURRENT_USER=$(docker info 2>/dev/null | grep "Username" | awk '{print $2}' | tr -d ' ')

if [ -n "$CURRENT_USER" ]; then
    echo "Currently logged in as: $CURRENT_USER"
    read -p "Use this account? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DOCKER_HUB_USERNAME=$CURRENT_USER
    else
        read -p "Enter your Docker Hub username: " DOCKER_HUB_USERNAME
    fi
else
    echo "You're not logged in to Docker Hub."
    read -p "Enter your Docker Hub username: " DOCKER_HUB_USERNAME
    
    read -p "Login now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login
    fi
fi

echo ""
echo "Using Docker Hub username: $DOCKER_HUB_USERNAME"
echo ""

# ============================================
# Step 3: Choose What to Build
# ============================================
echo "📋 Step 3: Select Images to Build"
echo ""
echo "Available images:"
echo "  1) All images (backend, frontend, nginx, mcp-server)"
echo "  2) Backend API only"
echo "  3) Frontend only"
echo "  4) Nginx proxy only"
echo "  5) MCP Server only"
echo ""

read -p "Select option (1-5): " BUILD_CHOICE

case $BUILD_CHOICE in
    1) BUILD_ALL=true ;;
    2) BUILD_BACKEND=true ;;
    3) BUILD_FRONTEND=true ;;
    4) BUILD_NGINX=true ;;
    5) BUILD_MCP=true ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

echo ""

# ============================================
# Step 4: Choose Build Target
# ============================================
echo "📋 Step 4: Select Build Target"
echo ""
echo "Options:"
echo "  1) Production (optimized, smaller, recommended)"
echo "  2) Development (with debug tools)"
echo ""

read -p "Select option (1-2): " TARGET_CHOICE

case $TARGET_CHOICE in
    1) BUILD_TARGET="production" ;;
    2) BUILD_TARGET="development" ;;
    *) BUILD_TARGET="production" ;;
esac

echo "Build target: $BUILD_TARGET"
echo ""

# ============================================
# Step 5: Build Functions
# ============================================

build_backend() {
    echo "🔨 Building Backend API image..."
    docker build \
        --target $BUILD_TARGET \
        -t "${DOCKER_HUB_USERNAME}/easypost-backend:latest" \
        -t "${DOCKER_HUB_USERNAME}/easypost-backend:${BUILD_TARGET}" \
        -f backend/Dockerfile \
        backend/
    
    if [ $? -eq 0 ]; then
        echo "✅ Backend image built successfully"
        return 0
    else
        echo "❌ Failed to build backend image"
        return 1
    fi
}

build_frontend() {
    echo "🔨 Building Frontend image..."
    docker build \
        --target $BUILD_TARGET \
        -t "${DOCKER_HUB_USERNAME}/easypost-frontend:latest" \
        -t "${DOCKER_HUB_USERNAME}/easypost-frontend:${BUILD_TARGET}" \
        -f frontend/Dockerfile \
        frontend/
    
    if [ $? -eq 0 ]; then
        echo "✅ Frontend image built successfully"
        return 0
    else
        echo "❌ Failed to build frontend image"
        return 1
    fi
}

build_nginx() {
    echo "🔨 Building Nginx image..."
    docker build \
        -t "${DOCKER_HUB_USERNAME}/easypost-nginx:latest" \
        -t "${DOCKER_HUB_USERNAME}/easypost-nginx:${BUILD_TARGET}" \
        -f nginx/Dockerfile \
        nginx/
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx image built successfully"
        return 0
    else
        echo "❌ Failed to build nginx image"
        return 1
    fi
}

build_mcp() {
    echo "🔨 Building MCP Server image..."
    docker build \
        -t "${DOCKER_HUB_USERNAME}/easypost-mcp-server:latest" \
        -t "${DOCKER_HUB_USERNAME}/easypost-mcp-server:${BUILD_TARGET}" \
        -f mcp-server/Dockerfile \
        mcp-server/
    
    if [ $? -eq 0 ]; then
        echo "✅ MCP Server image built successfully"
        return 0
    else
        echo "❌ Failed to build MCP Server image"
        return 1
    fi
}

# ============================================
# Step 6: Execute Builds
# ============================================
echo "📋 Step 5: Building Images..."
echo ""

if [ "$BUILD_ALL" = true ]; then
    build_backend && build_frontend && build_nginx && build_mcp
elif [ "$BUILD_BACKEND" = true ]; then
    build_backend
elif [ "$BUILD_FRONTEND" = true ]; then
    build_frontend
elif [ "$BUILD_NGINX" = true ]; then
    build_nginx
elif [ "$BUILD_MCP" = true ]; then
    build_mcp
fi

BUILD_STATUS=$?

echo ""

if [ $BUILD_STATUS -eq 0 ]; then
    echo "✅ All images built successfully!"
else
    echo "⚠️  Some builds may have failed"
fi

# ============================================
# Step 7: Show Built Images
# ============================================
echo ""
echo "📦 Built Images:"
docker images | grep "$DOCKER_HUB_USERNAME/easypost" || echo "No images found"

# ============================================
# Step 8: Push Option
# ============================================
echo ""
read -p "Push images to Docker Hub? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Pushing images to Docker Hub..."
    echo ""
    
    docker images | grep "$DOCKER_HUB_USERNAME/easypost" | awk '{print $1":"$2}' | while read IMAGE; do
        echo "Pushing: $IMAGE"
        docker push "$IMAGE"
        if [ $? -eq 0 ]; then
            echo "✅ Pushed: $IMAGE"
        else
            echo "❌ Failed to push: $IMAGE"
        fi
        echo ""
    done
    
    echo "✅ All images pushed to Docker Hub!"
else
    echo "⏭️  Images are ready locally."
    echo ""
    echo "To push later, run:"
    docker images | grep "$DOCKER_HUB_USERNAME/easypost" | awk '{print "  docker push " $1":"$2}' || echo "  docker push [image-name]"
fi

echo ""
echo "============================================"
echo "✅ Build Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Test images locally:"
echo "   docker run -it ${DOCKER_HUB_USERNAME}/easypost-backend:latest"
echo ""
echo "2. Deploy to production:"
echo "   docker-compose -f docker-compose.hub.yml up -d"
echo ""
echo "3. View images:"
echo "   docker images | grep easypost"
echo ""
