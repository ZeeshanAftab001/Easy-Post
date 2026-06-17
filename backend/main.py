# main.py or at the end of your main app file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes.auth_router import auth_router
from app.user.routes.user_router import user_router
from app.oauth.routes.oauth_router import oauth_router
from app.chat.routes.whatsapp_router import whatsapp_router
from app.chat.routes.post_router import post_router
from app.chat.routes.ai_router import ai_router
from app.chat.routes.knowledge_router import knowledge_router
from app.chat.routes.media_router import media_router
from app.chat.routes.dashboard_router import dashboard_router
from app.chat.services.agent_service import lifespan

app = FastAPI(
    lifespan=lifespan,
    title="EasyPost API",
    description="EasyPost API for user management, authentication, OAuth integration, and WhatsApp chat services for mananging social media accounts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized API Routes
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(oauth_router, prefix="/api/oauth", tags=["Social"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Core"])
app.include_router(knowledge_router, prefix="/api/ai/knowledge", tags=["RAG Knowledge"])
app.include_router(media_router, prefix="/api/media", tags=["Media Storage"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    return {"message": "EasyPost API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__": 
    import uvicorn 
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)