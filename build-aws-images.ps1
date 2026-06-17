# EasyPost AWS Docker Build Script
# This script builds the 3 separate backend services and the consolidated all-in-one image.

$DOCKER_USER = "zeeshanaabbasi" # Update this to your AWS ECR or Docker Hub username
$TAG = "latest"

Write-Host "🚀 Starting Build Process for EasyPost Backend Images..." -ForegroundColor Cyan

# 1. Build Backend API Image
Write-Host "`n📦 Building Backend API Image (FastAPI)..." -ForegroundColor Yellow
docker build --target production -t "$DOCKER_USER/easypost-api:$TAG" -f backend/Dockerfile backend/

# 2. Build Celery Worker Image
# Note: This uses the same base code but is tagged separately for AWS ECS task definition clarity.
Write-Host "`n📦 Building Celery Worker Image..." -ForegroundColor Yellow
docker build --target production -t "$DOCKER_USER/easypost-worker:$TAG" -f backend/Dockerfile backend/

# 3. Build Celery Beat (Scheduler) Image
Write-Host "`n📦 Building Celery Beat Image..." -ForegroundColor Yellow
docker build --target production -t "$DOCKER_USER/easypost-beat:$TAG" -f backend/Dockerfile backend/

# 4. Build Complete All-in-One Image
Write-Host "`n📦 Building COMPLETE All-in-One Backend Image..." -ForegroundColor Magenta
docker build -t "$DOCKER_USER/easypost-allinone:$TAG" -f Dockerfile.allinone .

Write-Host "`n✅ All 4 images built successfully!" -ForegroundColor Green
Write-Host "`nSummary of images created:"
docker images | Select-String "easypost"
