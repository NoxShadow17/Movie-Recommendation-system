import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./movie_recommendation.db"  # Local SQLite for development
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API
API_V1_STR = "/api/v1"

# Recommendation Engine
COLLABORATIVE_WEIGHT = 0.6
CONTENT_BASED_WEIGHT = 0.4
MIN_COMMON_RATINGS = 3
RECOMMENDATION_COUNT = 10

# Features
ENABLE_SOCIAL_FEATURES = True
ENABLE_MOOD_BASED = True
ENABLE_TRENDING = True
