from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Import friend schemas
from .friend import (
    FriendRequestBase, FriendRequestCreate, FriendRequestResponse,
    FriendResponse, FriendSearchResult, FriendStats, FriendActivity,
    SocialRecommendation
)


# User Schemas
class SimpleUser(BaseModel):
    id: int
    username: str
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None


class UserBase(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    pass


# Movie Schemas
class MovieCreate(BaseModel):
    tmdb_id: Optional[int] = None
    title: str
    overview: str
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    genre: str
    director: Optional[str] = None
    cast: Optional[str] = None
    runtime: Optional[int] = None
    language: Optional[str] = None
    country: Optional[str] = None
    popularity: Optional[float] = None


class MovieBase(MovieCreate):
    id: int
    avg_rating: float
    rating_count: int
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    is_trending: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MovieResponse(MovieBase):
    pass


class MovieDetailResponse(MovieResponse):
    rating_count: int
    avg_rating: float
    is_trending: bool


# Rating Schemas
class RatingCreate(BaseModel):
    movie_id: int
    rating: float  # 1-5 scale
    review: Optional[str] = None
    mood: Optional[str] = None


class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    review: Optional[str] = None
    mood: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRatingResponse(RatingResponse):
    movie_title: Optional[str] = None
    movie_genre: Optional[str] = None


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    movie_id: int
    score: float
    reason: str
    algorithm: str
    title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    movie: MovieResponse
    # Social metadata
    friend_count: Optional[int] = 0
    avg_friend_rating: Optional[float] = 0.0
    top_friends: Optional[List[SimpleUser]] = None
    
    class Config:
        from_attributes = True
        extra = 'allow'


# User Preference Schemas
class UserPreferenceCreate(BaseModel):
    preferred_genres: str
    preferred_directors: Optional[str] = None
    min_rating_threshold: float = 6.0
    preferred_language: Optional[str] = None
    favorite_mood: Optional[str] = None


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    preferred_genres: str
    preferred_directors: Optional[str] = None
    min_rating_threshold: float
    preferred_language: Optional[str] = None
    favorite_mood: Optional[str] = None
    
    class Config:
        from_attributes = True


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Watchlist Schemas
class WatchlistItem(BaseModel):
    movie: MovieResponse
    added_at: datetime
    
    class Config:
        from_attributes = True


class WatchPartyRequest(BaseModel):
    user_ids: List[int]
    limit: Optional[int] = 15
