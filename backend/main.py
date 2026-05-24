import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.database import Base, engine
from app.core.config import API_V1_STR
from app.routes import auth, movies, recommendations, users, friends, chat

logging.basicConfig(level=logging.INFO)

# Create tables
Base.metadata.create_all(bind=engine)

# Auto-seed database if empty (loads local data on first deploy)
from seeder import run_seed
run_seed()

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Movie Recommendation System",
    description="A sophisticated movie recommendation platform with hybrid algorithms",
    version="1.0.0"
)

# Configure CORS dynamically
cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS", "")
if cors_origins_env:
    # Strip trailing slashes — browsers send origins without trailing slash
    origins = [origin.strip().rstrip("/") for origin in cors_origins_env.split(",") if origin.strip()]
else:
    # Note: "*" wildcard cannot be used with allow_credentials=True
    # Always set BACKEND_CORS_ORIGINS in production to your frontend URL
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add response compression for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(recommendations.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(chat.router)


@app.api_route("/", methods=["GET", "HEAD"])
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Advanced Movie Recommendation System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_version": API_V1_STR
    }


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
