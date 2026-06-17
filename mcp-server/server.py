# MCP Server Application Stub

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="EasyPost MCP Server",
    description="Model Context Protocol Server for EasyPost",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy"})

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EasyPost MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

# Add your MCP tool definitions and routes here
