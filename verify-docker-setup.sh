#!/bin/bash

# Docker Setup Verification Script
# Checks if your system is ready to build and push Docker images

echo "============================================"
echo "🐳 Docker Setup Verification"
echo "============================================"
echo ""

# Counter for checks
PASSED=0
FAILED=0

# ============================================
# Check 1: Docker Installed
# ============================================
echo "✓ Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "  ✅ Docker installed: $DOCKER_VERSION"
    ((PASSED++))
else
    echo "  ❌ Docker not installed"
    echo "     Install from: https://www.docker.com/products/docker-desktop/"
    ((FAILED++))
fi

# ============================================
# Check 2: Docker Daemon Running
# ============================================
echo "✓ Checking Docker daemon..."
if docker ps > /dev/null 2>&1; then
    echo "  ✅ Docker daemon is running"
    ((PASSED++))
else
    echo "  ❌ Docker daemon is not running"
    echo "     Start Docker and try again"
    ((FAILED++))
fi

# ============================================
# Check 3: Docker Compose
# ============================================
echo "✓ Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    DC_VERSION=$(docker-compose --version)
    echo "  ✅ Docker Compose installed: $DC_VERSION"
    ((PASSED++))
else
    echo "  ⚠️  Docker Compose not installed"
    echo "     Install with: pip install docker-compose"
    ((FAILED++))
fi

# ============================================
# Check 4: Disk Space
# ============================================
echo "✓ Checking disk space..."
if command -v df &> /dev/null; then
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    FREE_SPACE=$(df / | awk 'NR==2 {print $4}' | awk '{printf "%.0f GB", $1/1024/1024}')
    
    echo "  📊 Disk usage: $DISK_USAGE%"
    echo "  📊 Free space: $FREE_SPACE"
    
    if [ "$DISK_USAGE" -gt 80 ]; then
        echo "  ⚠️  Low disk space (>80% used)"
        ((FAILED++))
    else
        echo "  ✅ Sufficient disk space"
        ((PASSED++))
    fi
fi

# ============================================
# Check 5: Docker Hub Login
# ============================================
echo "✓ Checking Docker Hub login..."
if docker info | grep -q "Username"; then
    HUB_USER=$(docker info 2>/dev/null | grep "Username" | awk '{print $2}' || echo "unknown")
    echo "  ✅ Logged in to Docker Hub: $HUB_USER"
    ((PASSED++))
else
    echo "  ⚠️  Not logged in to Docker Hub"
    echo "     Run: docker login"
    echo "     Then enter your credentials"
    ((FAILED++))
fi

# ============================================
# Check 6: Required Dockerfiles
# ============================================
echo "✓ Checking Dockerfiles..."
DOCKERFILES=("backend/Dockerfile" "frontend/Dockerfile" "nginx/Dockerfile" "mcp-server/Dockerfile")
ALL_FOUND=true

for df in "${DOCKERFILES[@]}"; do
    if [ -f "$df" ]; then
        echo "  ✅ Found: $df"
    else
        echo "  ❌ Missing: $df"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = true ]; then
    ((PASSED++))
else
    ((FAILED++))
fi

# ============================================
# Check 7: Build Script
# ============================================
echo "✓ Checking build script..."
if [ -f "build-and-push.sh" ]; then
    echo "  ✅ Found: build-and-push.sh"
    if [ -x "build-and-push.sh" ]; then
        echo "  ✅ Script is executable"
    else
        echo "  ⚠️  Script is not executable"
        echo "     Run: chmod +x build-and-push.sh"
    fi
    ((PASSED++))
else
    echo "  ❌ Missing: build-and-push.sh"
    ((FAILED++))
fi

# ============================================
# Check 8: Environment File
# ============================================
echo "✓ Checking .env file..."
if [ -f ".env" ]; then
    echo "  ✅ Found: .env"
    ((PASSED++))
else
    echo "  ⚠️  Missing: .env"
    echo "     Create from: .env.production.example"
    ((FAILED++))
fi

# ============================================
# Summary
# ============================================
echo ""
echo "============================================"
echo "📊 Summary"
echo "============================================"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All checks passed! Ready to build Docker images"
    echo ""
    echo "Next steps:"
    echo "1. Update DOCKER_HUB_USERNAME in build-and-push.sh"
    echo "2. Run: ./build-and-push.sh"
    echo ""
    exit 0
else
    echo "⚠️  Some checks failed. Please fix the issues above."
    echo ""
    echo "Help:"
    echo "  • Docker: https://docs.docker.com/get-docker/"
    echo "  • Docker Hub: https://hub.docker.com/"
    echo "  • Troubleshooting: See DOCKER_BUILD_GUIDE.md"
    echo ""
    exit 1
fi
