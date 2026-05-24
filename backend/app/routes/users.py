from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import func, desc
from collections import Counter
from app.core.database import get_db
from app.models import User, Movie, Rating, UserPreference
from app.schemas import UserResponse, UserUpdate, UserRatingResponse, UserPreferenceResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/{user_id}")
def get_user(
    user_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile with privacy checks and enriched data for friends"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if friends
    from app.models import Friendship
    is_friend = False
    
    if current_user.id == user_id:
        is_friend = True
    else:
        friendship = db.query(Friendship).filter(
            ((Friendship.user1_id == current_user.id) & (Friendship.user2_id == user.id)) |
            ((Friendship.user1_id == user.id) & (Friendship.user2_id == current_user.id)),
            Friendship.is_active == True
        ).first()
        is_friend = friendship is not None
        
    if is_friend:
        # Fetch recent ratings (last 4)
        recent_ratings = db.query(
            Rating.id, Rating.rating, Rating.created_at, Movie.id.label("movie_id"), Movie.title, Movie.poster_path
        ).join(Movie, Rating.movie_id == Movie.id)\
         .filter(Rating.user_id == user.id)\
         .order_by(desc(Rating.created_at))\
         .limit(4).all()
         
        formatted_ratings = [
            {
                "id": r.id, 
                "rating": r.rating, 
                "movie_id": r.movie_id, 
                "title": r.title, 
                "poster_path": r.poster_path,
                "created_at": r.created_at
            } 
            for r in recent_ratings
        ]

        # Fetch recent watchlist (last 4)
        # Note: watchlist is a relationship, so we can access it directly but need to sort/limit
        # SQLAlchemy relationships load all by default, so query directly for efficiency
        # Assuming we have an association table or configured relationship
        # For simplicity with current setup, let's query the association table logic valid for many-to-many
        # Actually user.watchlist is a list of Movie objects. 
        # To get "recent", we need the association table timestamp.
        # Let's try a simpler approach: just take the last 4 from the list if not huge, 
        # or better: query via the association if possible.
        # Given potential complexity, let's just reverse the watchlist list (assuming appended) or use what we have.
        # Safest quick way:
        
        recent_watchlist = []
        if user.watchlist:
            # This relies on order, which might not be guaranteed without explicit sort on association
            # But let's take the last 4 items added
             recent_watchlist = [
                {
                    "id": m.id,
                    "title": m.title,
                    "poster_path": m.poster_path,
                    "vote_average": m.vote_average
                }
                for m in user.watchlist[-4:][::-1]
            ]
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "bio": user.bio,
            "created_at": user.created_at,
            "is_friend": True,
            "recent_ratings": formatted_ratings,
            "recent_watchlist": recent_watchlist,
            # Add stats for the UI
            "stats": {
                "total_ratings": len(user.ratings),
                "total_watchlist": len(user.watchlist)
            }
        }
    
    # Restricted Access
    return {
        "id": user.id,
        "username": user.username,
        "email": None, # Hide email for non-friends
        "full_name": user.full_name,
        "profile_picture": None, # HIDDEN
        "bio": None, # HIDDEN
        "created_at": user.created_at,
        "is_friend": False
    }


@router.put("/me", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.profile_picture:
        current_user.profile_picture = user_update.profile_picture
    if user_update.bio:
        current_user.bio = user_update.bio
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}/friends", response_model=List[UserResponse])
def get_user_friends(user_id: int, db: Session = Depends(get_db)):
    """Get user's friends"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user.friends


@router.post("/{friend_id}/add-friend")
def add_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a friend"""
    if friend_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as friend"
        )
    
    friend = db.query(User).filter(User.id == friend_id).first()
    
    if not friend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend not found"
        )
    
    if friend not in current_user.friends:
        current_user.friends.append(friend)
        db.commit()
    
    return {"message": "Friend added successfully"}


@router.post("/{movie_id}/add-to-watchlist")
def add_to_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add movie to watchlist"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    if movie not in current_user.watchlist:
        current_user.watchlist.append(movie)
        db.commit()
    
    return {"message": "Added to watchlist"}


@router.delete("/{movie_id}/remove-from-watchlist")
def remove_from_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove movie from watchlist"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    if movie in current_user.watchlist:
        current_user.watchlist.remove(movie)
        db.commit()
    
    return {"message": "Removed from watchlist"}


@router.get("/me/watchlist")
def get_watchlist(current_user: User = Depends(get_current_user)):
    """Get current user's watchlist"""
    return {"watchlist": current_user.watchlist}


@router.get("/me/ratings", response_model=List[UserRatingResponse])
def get_user_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's ratings with movie details"""
    ratings = db.query(
        Rating.id,
        Rating.user_id,
        Rating.movie_id,
        Rating.rating,
        Rating.review,
        Rating.mood,
        Rating.created_at,
        Movie.title.label("movie_title"),
        Movie.genre.label("movie_genre")
    ).join(Movie, Rating.movie_id == Movie.id)\
     .filter(Rating.user_id == current_user.id)\
     .all()
    
    return ratings


@router.get("/me/preferences", response_model=Dict[str, Any])
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's calculated preferences based on their ratings and behavior"""
    try:
        # Get user's ratings
        user_ratings = db.query(Rating).filter(Rating.user_id == current_user.id).all()
        
        if not user_ratings:
            return {
                "message": "No ratings found. Rate some movies to see your preferences!",
                "genres": [],
                "directors": [],
                "moods": [],
                "stats": {
                    "total_ratings": 0,
                    "average_rating": 0,
                    "favorite_genre": None,
                    "favorite_mood": None
                }
            }
        
        # Calculate genre preferences
        genre_counts = Counter()
        director_counts = Counter()
        mood_counts = Counter()
        total_rating = 0
        rating_count = 0
        
        for rating in user_ratings:
            movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie:
                # Count genres with rating weight
                for genre in movie.genre.split(','):
                    genre = genre.strip()
                    if genre:
                        genre_counts[genre] += rating.rating
                
                # Count directors with rating weight
                if movie.director:
                    for director in movie.director.split(','):
                        director = director.strip()
                        if director:
                            director_counts[director] += rating.rating
            
            # Count moods
            if rating.mood:
                mood_counts[rating.mood.value] += 1
            
            total_rating += rating.rating
            rating_count += 1
        
        # Calculate averages and rankings
        avg_rating = total_rating / rating_count if rating_count > 0 else 0
        
        # Get top preferences
        top_genres = [{"genre": genre, "score": score} for genre, score in genre_counts.most_common(5)]
        top_directors = [{"director": director, "score": score} for director, score in director_counts.most_common(3)]
        top_moods = [{"mood": mood, "count": count} for mood, count in mood_counts.most_common(3)]
        
        # Get favorite genre and mood
        favorite_genre = top_genres[0]["genre"] if top_genres else None
        favorite_mood = top_moods[0]["mood"] if top_moods else None
        
        return {
            "genres": top_genres,
            "directors": top_directors,
            "moods": top_moods,
            "stats": {
                "total_ratings": rating_count,
                "average_rating": round(avg_rating, 1),
                "favorite_genre": favorite_genre,
                "favorite_mood": favorite_mood,
                "rating_distribution": _get_rating_distribution(user_ratings),
                "last_activity": max([_parse_date(r.created_at) for r in user_ratings]).isoformat() if user_ratings else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating preferences: {str(e)}"
        )


from datetime import datetime

def _parse_date(date_val):
    if isinstance(date_val, str):
        try:
            return datetime.fromisoformat(date_val.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Handle space-separated SQLite dates
                return datetime.strptime(date_val.split('.')[0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return datetime.now()
    if date_val is None:
        return datetime.now()
    return date_val

@router.get("/me/preferences/detailed", response_model=Dict[str, Any])
def get_detailed_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user preferences with additional insights"""
    try:
        # Get basic preferences
        basic_prefs = get_user_preferences(current_user, db)
        
        # Add detailed insights
        user_ratings = db.query(Rating).filter(Rating.user_id == current_user.id).all()
        
        if not user_ratings:
            return basic_prefs
        
        # Calculate additional insights
        insights = {
            "diversity_score": _calculate_diversity_score(user_ratings, db),
            "rating_patterns": _analyze_rating_patterns(user_ratings),
            "genre_evolution": _analyze_genre_evolution(user_ratings, db),
            "recommendation_confidence": _calculate_recommendation_confidence(user_ratings)
        }
        
        return {**basic_prefs, "insights": insights}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating detailed preferences: {str(e)}"
        )


def _get_rating_distribution(user_ratings: List[Rating]) -> Dict[str, int]:
    """Get distribution of user ratings"""
    distribution = {str(i): 0 for i in range(1, 11)}
    for rating in user_ratings:
        distribution[str(int(rating.rating))] += 1
    return distribution


def _calculate_diversity_score(user_ratings: List[Rating], db: Session) -> float:
    """Calculate how diverse the user's movie tastes are (0-100)"""
    if not user_ratings:
        return 0
    
    genres = set()
    for rating in user_ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if movie and movie.genre:
            for genre in movie.genre.split(','):
                genre = genre.strip()
                if genre:
                    genres.add(genre)
    
    # Diversity score based on number of unique genres
    max_genres = 20  # Maximum reasonable number of genres
    diversity_score = min(len(genres) / max_genres * 100, 100)
    return round(diversity_score, 1)


def _analyze_rating_patterns(user_ratings: List[Rating]) -> Dict[str, Any]:
    """Analyze user's rating patterns"""
    if not user_ratings:
        return {
            "average_rating": 0,
            "rating_style": "Not enough data",
            "consistency": 0,
            "total_movies": 0,
            "high_rated_count": 0,
            "low_rated_count": 0
        }
    
    ratings = [r.rating for r in user_ratings]
    avg_rating = sum(ratings) / len(ratings)
    
    # Determine rating style - require at least 2 ratings for meaningful analysis
    if len(user_ratings) >= 2:
        if avg_rating >= 4.0:  # 4.0+ out of 5 = generous
            style = "generous"
        elif avg_rating <= 3.0:  # 3.0- out of 5 = harsh
            style = "harsh"
        else:
            style = "moderate"
    else:
        style = "Not enough data"
    
    # Calculate rating consistency (normalized to 0-1 scale for better interpretation)
    import statistics
    if len(ratings) > 1:
        std_dev = statistics.stdev(ratings)
        # Normalize to 0-1 scale where 1 = very consistent, 0 = very inconsistent
        # Max possible std dev for 1-5 scale is ~2.0, so we use 2.0 as the divisor
        consistency = max(0, 1 - (std_dev / 2.0))
    else:
        consistency = 0
    
    return {
        "average_rating": round(avg_rating, 1),
        "rating_style": style,
        "consistency": round(consistency, 2),
        "total_movies": len(user_ratings),
        "high_rated_count": len([r for r in ratings if r >= 4.0]),  # 4.0+ out of 5 = high rated
        "low_rated_count": len([r for r in ratings if r <= 2.0])    # 2.0- out of 5 = low rated
    }


def _analyze_genre_evolution(user_ratings: List[Rating], db: Session) -> Dict[str, Any]:
    """Analyze how user's genre preferences have evolved over time"""
    if len(user_ratings) < 5:
        return {"message": "Need more ratings to analyze evolution"}
    
    # Sort by date safely
    sorted_ratings = sorted(user_ratings, key=lambda x: _parse_date(x.created_at))
    
    # Split into early and recent ratings
    mid_point = len(sorted_ratings) // 2
    early_ratings = sorted_ratings[:mid_point]
    recent_ratings = sorted_ratings[mid_point:]
    
    def get_genre_scores(ratings_list):
        genre_scores = Counter()
        for rating in ratings_list:
            movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie and movie.genre:
                for genre in movie.genre.split(','):
                    genre = genre.strip()
                    if genre:
                        genre_scores[genre] += rating.rating
        return dict(genre_scores)
    
    early_genres = get_genre_scores(early_ratings)
    recent_genres = get_genre_scores(recent_ratings)
    
    return {
        "early_preferences": early_genres,
        "recent_preferences": recent_genres,
        "evolution_detected": early_genres != recent_genres
    }


def _calculate_recommendation_confidence(user_ratings: List[Rating]) -> float:
    """Calculate confidence in recommendations (0-100) based on data quality"""
    if not user_ratings:
        return 0
    
    # Factors affecting confidence:
    # 1. Number of ratings (more = higher confidence)
    rating_count = len(user_ratings)
    rating_score = min(rating_count / 50 * 100, 50)  # Max 50 points for rating count
    
    # 2. Rating distribution (balanced = higher confidence)
    ratings = [r.rating for r in user_ratings]
    import statistics
    diversity_score = min(100 - (statistics.stdev(ratings) * 10), 30) if len(ratings) > 1 else 10
    
    # 3. Time span (longer history = higher confidence)
    if len(user_ratings) > 1:
        time_span = max([_parse_date(r.created_at) for r in user_ratings]) - min([_parse_date(r.created_at) for r in user_ratings])
        time_days = time_span.days
        time_score = min(time_days / 90 * 20, 20)  # Max 20 points for time span
    else:
        time_score = 5
    
    total_confidence = rating_score + diversity_score + time_score
    return round(min(total_confidence, 100), 1)
