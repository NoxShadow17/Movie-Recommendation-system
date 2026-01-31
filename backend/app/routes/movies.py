from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Movie, Rating
from app.schemas import MovieResponse, MovieDetailResponse, RatingCreate, RatingResponse
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@router.get("/", response_model=List[MovieResponse])
def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    genre: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get movies with optional genre and search filters"""
    from sqlalchemy import or_
    query = db.query(Movie)
    
    if genre:
        # Handle multiple genres separated by commas
        genres = [g.strip() for g in genre.split(',')]
        # Create OR conditions for each genre
        genre_filters = [Movie.genre.ilike(f"%{g}%") for g in genres]
        query = query.filter(or_(*genre_filters))
        
    if search:
        query = query.filter(
            (Movie.title.ilike(f"%{search}%")) | 
            (Movie.overview.ilike(f"%{search}%"))
        )
    
    movies = query.offset(skip).limit(limit).all()
    return movies


@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie details"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return movie


@router.get("/{movie_id}/explanation")
def get_movie_explanation(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated explanation for why this movie matches the user's taste"""
    from app.services.explainability_service import AIExplainabilityService
    
    explanation = AIExplainabilityService.generate_movie_explanation(
        current_user.id, movie_id, db
    )
    return explanation


@router.post("/{movie_id}/rate", response_model=RatingResponse)
def rate_movie(
    movie_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a movie"""
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Use mood value as-is (now expects uppercase enum values)
    mood_value = rating_data.mood
    
    # Check if user already rated this movie
    existing_rating = db.query(Rating).filter(
        (Rating.user_id == current_user.id) & (Rating.movie_id == movie_id)
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_data.rating
        existing_rating.review = rating_data.review
        existing_rating.mood = mood_value
        db.commit()
        db.refresh(existing_rating)
        rating = existing_rating
    else:
        # Create new rating
        rating = Rating(
            user_id=current_user.id,
            movie_id=movie_id,
            rating=rating_data.rating,
            review=rating_data.review,
            mood=mood_value
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
    
    # Update movie average rating
    all_ratings = db.query(Rating).filter(Rating.movie_id == movie_id).all()
    movie.avg_rating = sum([r.rating for r in all_ratings]) / len(all_ratings) if all_ratings else 0
    movie.rating_count = len(all_ratings)
    db.commit()
    
    return rating


@router.get("/{movie_id}/ratings", response_model=List[RatingResponse])
def get_movie_ratings(
    movie_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get ratings for a movie"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    ratings = db.query(Rating).filter(
        Rating.movie_id == movie_id
    ).offset(skip).limit(limit).all()
    
    return ratings


@router.post("/search", response_model=List[MovieResponse])
def search_movies(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search movies by title or overview"""
    movies = db.query(Movie).filter(
        (Movie.title.ilike(f"%{query}%")) | (Movie.overview.ilike(f"%{query}%"))
    ).limit(20).all()
    
    return movies
