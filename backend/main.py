from app.auth.routes.auth_router import auth_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.user.routes.user_router import user_router
from app.oauth.routes.oauth_router import oauth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

# ========== CRITICAL: IMPORT ALL MODELS ==========
# This ensures SQLAlchemy knows about all model classes

# Import User model
from app.user.models.user import User
print(f"✅ Imported: {User.__name__}")

# Import SocialAccount model - adjust path based on where it actually is
try:
    from app.oauth.models.social import SocialAccount
    print(f"✅ Imported: {SocialAccount.__name__}")
except ImportError:
    print("⚠️  Could not import SocialAccount - check if file exists")

# Import ChatSession model - adjust path based on where it actually is
try:
    from app.chat.models.whatsapp import ChatSession
    print(f"✅ Imported: {ChatSession.__name__}")
except ImportError:
    try:
        from app.chat.models.whatsapp import ChatSession
        print(f"✅ Imported: {ChatSession.__name__} from whatsapp")
    except ImportError:
        print("⚠️  Could not import ChatSession - will cause relationship errors!")

# Import ChatMemory model
try:
    from app.chat.models.whatsapp import ChatMemory
    print(f"✅ Imported: {ChatMemory.__name__}")
except ImportError:
    try:
        from app.chat.models.whatsapp import ChatMemory
        print(f"✅ Imported: {ChatMemory.__name__} from whatsapp")
    except ImportError:
        print("⚠️  Could not import ChatMemory")

# ========== CONTINUE WITH REST OF IMPORTS ==========
from app.auth.routes.auth_router import auth_router
from app.user.routes.user_router import user_router
from app.oauth.routes.oauth_router import oauth_router
from app.chat.routes.whatsapp_router import whatsapp_router
import logging
from app.chat.routes.whatsapp_router import whatsapp_router
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
app.include_router(whatsapp_router, prefix="/api/whatsapp")


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