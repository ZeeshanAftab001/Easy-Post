# Master Build & Push Script for EASYPOST (Backend Only)
$ErrorActionPreference = "Stop"

$DOCKER_USER = "zeeshanaftababbasi"
$VERSION = "latest"

Write-Host "--- Starting Backend Infrastructure Build ---"

Write-Host "1/3 Building Backend..."
docker build -t "$DOCKER_USER/easypost-backend:$VERSION" ./backend --target production

Write-Host "2/3 Building MCP Server..."
docker build -t "$DOCKER_USER/easypost-mcp:$VERSION" ./mcp-server

Write-Host "3/3 Building Nginx Gateway..."
docker build -t "$DOCKER_USER/easypost-nginx:$VERSION" ./nginx

Write-Host "--- Pushing to Docker Hub ---"

docker push "$DOCKER_USER/easypost-backend:$VERSION"
docker push "$DOCKER_USER/easypost-mcp:$VERSION"
docker push "$DOCKER_USER/easypost-nginx:$VERSION"

Write-Host "--- Cloud Infrastructure pushed successfully! ---"
Write-Host "Frontend excluded (for Hostinger deployment)."
