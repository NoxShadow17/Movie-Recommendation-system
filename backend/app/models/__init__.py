from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table, Enum, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

# Import friend models
from .friend import FriendRequest, Friendship, FriendRequestStatus


class MoodEnum(str, enum.Enum):
    HAPPY = "HAPPY"
    SAD = "SAD"
    EXCITED = "EXCITED"
    RELAXED = "RELAXED"
    THOUGHTFUL = "THOUGHTFUL"
    SCARED = "SCARED"
    
    def __str__(self):
        return self.value


# Association table for user watchlist
user_watchlist = Table(
    'user_watchlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    
    # Self-referential relationship for friendships
    friends = relationship(
        "User",
        secondary="friendships",
        primaryjoin="and_(User.id == Friendship.user1_id, Friendship.is_active == True)",
        secondaryjoin="and_(User.id == Friendship.user2_id, Friendship.is_active == True)",
        backref="befriended_by",
        viewonly=True
    )
    
    # Watchlist
    watchlist = relationship(
        "Movie",
        secondary=user_watchlist,
        backref="added_to_watchlist_by"
    )
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )


class Movie(Base):
    __tablename__ = "movies"
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=True, index=True)
    
    # Basic information
    title = Column(String(500), index=True)
    original_title = Column(String(500), nullable=True)
    tagline = Column(String(500), nullable=True)
    overview = Column(Text)
    release_date = Column(String(50), nullable=True)
    release_year = Column(Integer, nullable=True, index=True)
    status = Column(String(50), nullable=True)  # Released, Post Production, etc.
    
    # Media
    poster_path = Column(String(500), nullable=True)
    backdrop_path = Column(String(500), nullable=True)
    
    # Genre and classification
    genre = Column(String(500))  # Comma-separated genres
    keywords = Column(Text, nullable=True)  # Comma-separated keywords for ML
    adult = Column(Boolean, default=False)
    
    # Cast and crew (basic - kept for backward compatibility)
    director = Column(String(255), nullable=True)
    cast = Column(Text, nullable=True)  # Comma-separated cast
    
    # Cast and crew (enhanced - JSON format for ML)
    cast_details = Column(Text, nullable=True)  # JSON: [{"name": "Actor", "character": "Role", "order": 0}]
    crew_details = Column(Text, nullable=True)  # JSON: [{"name": "Person", "job": "Director", "department": "Directing"}]
    top_actors = Column(String(500), nullable=True)  # Top 5 actors comma-separated
    writers = Column(String(500), nullable=True)  # Screenplay writers
    producers = Column(String(500), nullable=True)  # Producers
    
    # Technical details
    runtime = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True)  # Primary language
    original_language = Column(String(10), nullable=True)  # Original language
    spoken_languages = Column(Text, nullable=True)  # JSON array of all languages
    country = Column(String(255), nullable=True)  # Primary country
    production_countries = Column(Text, nullable=True)  # JSON array of countries
    production_companies = Column(Text, nullable=True)  # JSON array of production companies
    
    # Financial data (for ML features)
    budget = Column(Integer, nullable=True)  # Production budget in USD
    revenue = Column(Integer, nullable=True)  # Box office revenue in USD
    
    # Ratings and popularity
    avg_rating = Column(Float, default=0.0)  # Our internal rating
    rating_count = Column(Integer, default=0)  # Our internal rating count
    vote_average = Column(Float, nullable=True)  # TMDB average rating (0-10)
    vote_count = Column(Integer, nullable=True)  # TMDB vote count
    popularity = Column(Float, default=0.0)  # Our popularity score
    tmdb_popularity = Column(Float, nullable=True)  # TMDB popularity score
    is_trending = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_movie_tmdb_id', 'tmdb_id'),
        Index('idx_movie_genres', 'genre'),
        Index('idx_movie_language', 'language'),
        Index('idx_movie_release_year', 'release_year'),
    )


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), index=True)
    rating = Column(Float)  # 1-5 scale
    review = Column(Text, nullable=True)
    mood = Column(Enum(MoodEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_rating_user_id', 'user_id'),
        Index('idx_rating_movie_id', 'movie_id'),
        Index('idx_rating_user_movie', 'user_id', 'movie_id'),  # Composite index
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    preferred_genres = Column(String(500))  # Comma-separated
    preferred_directors = Column(String(500), nullable=True)
    min_rating_threshold = Column(Float, default=6.0)
    preferred_language = Column(String(50), nullable=True)
    favorite_mood = Column(Enum(MoodEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), index=True)
    score = Column(Float)  # Recommendation confidence score
    reason = Column(String(500))  # Why this movie was recommended
    algorithm = Column(String(50))  # Which algorithm generated this
    is_clicked = Column(Boolean, default=False)
    is_rated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    movie = relationship("Movie")


class TrendingMovie(Base):
    __tablename__ = "trending_movies"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), index=True)
    trend_score = Column(Float)
    views_count = Column(Integer, default=0)
    period = Column(String(50))  # daily, weekly, monthly
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    movie = relationship("Movie")
