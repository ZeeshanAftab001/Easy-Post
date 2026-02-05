# main.py or at the end of your main app file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.auth.routes.auth_router import auth_router
from app.user.routes.user_router import user_router
from app.oauth.routes.oauth_router import oauth_router
from app.chat.routes.whatsapp_router import whatsapp_router
from app.chat.services.agent_service import lifespan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    lifespan=lifespan,
    title="EasyPost API",
    description="Career Advisor API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(oauth_router, prefix="/api/oauth")
app.include_router(whatsapp_router, prefix="/api/whatsapp")


@app.get("/")
async def root():
    return {"message": "EasyPost API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__": 
    import uvicorn 
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)