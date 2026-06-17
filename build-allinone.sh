#!/bin/bash

# EasyPost All-in-One Docker Build Script
# This script builds the "Complete Backend" image containing:
# FastAPI + MCP Server + Nginx + Celery Worker/Beat

echo "============================================"
echo "🐳 EasyPost: Building Complete Backend"
echo "============================================"

# Default Docker Hub username if not provided
DEFAULT_USERNAME="zeeshanaabbasi"
read -p "Enter Docker Hub username [$DEFAULT_USERNAME]: " DOCKER_HUB_USERNAME
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-$DEFAULT_USERNAME}

IMAGE_NAME="${DOCKER_HUB_USERNAME}/easypost-allinone:latest"

echo "🚀 Building image: $IMAGE_NAME"
echo "📂 Using Dockerfile.allinone"

# Build the all-in-one image
docker build -t "$IMAGE_NAME" -f Dockerfile.allinone .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build Successful!"
    echo "📦 Image: $IMAGE_NAME"
    echo ""
    read -p "Do you want to push this image to Docker Hub? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to Docker Hub..."
        docker push "$IMAGE_NAME"
        if [ $? -eq 0 ]; then
            echo "✅ Push Successful!"
        else
            echo "❌ Push Failed. Make sure you are logged in (docker login)."
        fi
    fi
else
    echo "❌ Build Failed. Please check the logs above."
    exit 1
fi

echo ""
echo "============================================"
echo "Next Steps:"
echo "1. Run locally to test: docker run -p 80:80 $IMAGE_NAME"
echo "2. Follow the AWS Deployment Guide for production setup."
echo "============================================"
