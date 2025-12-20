from app.auth.routes.auth_router import auth_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.user.routes.user_router import user_router
from app.oauth.routes.oauth_router import oauth_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EasyPost API",
    description="Career Advisor API",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # React default
    "http://127.0.0.1:5173",  # Alternative
    "http://127.0.0.1:3000",  # Alternative
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# Include routers
app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/api/auth")  # This makes /auth/token
app.include_router(oauth_router, prefix="/api/oauth")  # This makes /auth/token


@app.get("/")
async def root():
    return {"message": "EasyPost API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Create tables on startup (for development)
@app.on_event("startup")
async def startup():
    logger.info("Starting up...")
    async with engine.begin() as conn:
        # For development only - comment in production
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not exist)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)