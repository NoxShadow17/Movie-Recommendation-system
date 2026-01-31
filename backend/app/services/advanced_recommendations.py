from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Movie, Rating, TrendingMovie, UserPreference
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TrendingAnalyzer:
    """Analyze and track trending movies with advanced algorithms"""
    
    @staticmethod
    def update_trending_scores(db: Session):
        """
        Legacy internal trending update. 
        Now primarily handled by TMDBService for discovery, 
        but we keep this to track internal popularity.
        """
        # ... logic remains for internal analytics ...
        pass
    
    @staticmethod
    def get_trending_movies(db: Session, period: str = 'weekly', limit: int = 20, skip: int = 0) -> List[Movie]:
        """
        Get trending movies using TMDB for discovery, mapped to local DB.
        Falls back to internal analytics if TMDB fails or returns no matches.
        """
        from app.services.tmdb_service import TMDBService
        
        try:
            # 1. Try fetching from TMDB
            tmdb_service = TMDBService()
            tmdb_trending = tmdb_service.get_trending_movies(time_window='week' if period == 'weekly' else 'day')
            
            movies = []
            if tmdb_trending:
                # 2. Map TMDB results to local DB movies
                tmdb_ids = [m['id'] for m in tmdb_trending]
                
                # Fetch all matching movies in one query
                local_movies = db.query(Movie).filter(Movie.tmdb_id.in_(tmdb_ids)).all()
                local_movie_map = {m.tmdb_id: m for m in local_movies}
                
                # Maintain TMDB order (popularity)
                for i, tmdb_movie in enumerate(tmdb_trending):
                    if tmdb_movie['id'] in local_movie_map:
                        movie = local_movie_map[tmdb_movie['id']]
                        # Inject trending metadata for UI
                        movie.trending_rank = i + 1
                        movie.trending_score = tmdb_movie.get('popularity', 0)
                        movie.is_trending = True
                        movies.append(movie)
            
            # 3. Fallback to internal logic if we have too few results
            if len(movies) < 5:
                # Use legacy internal trending
                internal_trending = db.query(TrendingMovie).filter(
                    TrendingMovie.period == period
                ).order_by(TrendingMovie.trend_score.desc()).offset(skip).limit(limit).all()
                
                for record in internal_trending:
                    movie = db.query(Movie).filter(Movie.id == record.movie_id).first()
                    if movie and movie not in movies:
                         movie.trending_rank = record.rank
                         movie.trending_score = record.trend_score
                         movies.append(movie)
            
            return movies[skip : skip + limit]
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            return []


class SocialRecommendationEngine:
    """Generate recommendations based on social connections with advanced algorithms"""
    
    @staticmethod
    def get_friend_recommendations(user_id: int, db: Session, limit: int = 10, skip: int = 0) -> List[Dict]:
        """Get recommendations based on what friends are watching with advanced scoring - optimized with bulk queries"""
        try:
            from app.models import User
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.friends:
                return []
            
            # Get user's preferences for better matching
            user_preferences = SocialRecommendationEngine._get_user_preferences(user_id, db)
            
            # Get movies rated by friends - optimized bulk query
            friend_ids = [f.id for f in user.friends]
            user_rated_movies = set([r.movie_id for r in db.query(Rating).filter(Rating.user_id == user_id).all()])
            
            # Advanced friend recommendation query with movie data
            friend_ratings = db.query(
                Rating.movie_id,
                func.avg(Rating.rating).label('avg_rating'),
                func.count(Rating.id).label('friend_count'),
                Movie  # Include movie data in the query
            ).join(Movie, Rating.movie_id == Movie.id)\
            .filter(
                Rating.user_id.in_(friend_ids),
                Rating.movie_id.notin_(user_rated_movies)
            ).group_by(Rating.movie_id, Movie.id).all()
            
            # Get all top friends in one bulk query
            # First, get all friend ratings for the movies we're considering
            movie_ids = [rating_data.movie_id for rating_data in friend_ratings]
            if not movie_ids:
                return []
            
            # Get top 3 friends per movie in a single query
            top_friends_subquery = db.query(
                Rating.movie_id,
                User.id,
                User.username,
                User.profile_picture,
                Rating.rating,
                Rating.created_at,
                func.row_number().over(
                    partition_by=Rating.movie_id,
                    order_by=[Rating.rating.desc(), Rating.created_at.desc()]
                ).label('rn')
            ).join(User, Rating.user_id == User.id)\
            .filter(
                Rating.user_id.in_(friend_ids),
                Rating.movie_id.in_(movie_ids)
            ).subquery()
            
            top_friends_query = db.query(top_friends_subquery).filter(
                top_friends_subquery.c.rn <= 3
            ).all()
            
            # Group top friends by movie_id
            friends_by_movie = {}
            for row in top_friends_query:
                movie_id = row.movie_id
                if movie_id not in friends_by_movie:
                    friends_by_movie[movie_id] = []
                friends_by_movie[movie_id].append({
                    "id": row.id,
                    "username": row.username,
                    "profile_picture": row.profile_picture
                })
            
            result = []
            for rating_data in friend_ratings:
                movie_id = rating_data.movie_id
                avg_rating = rating_data.avg_rating or 0
                friend_count = rating_data.friend_count or 0
                rating_variance = 0 # stddev not supported in SQLite
                movie = rating_data.Movie
                
                if movie:
                    # Calculate social score with multiple factors
                    social_score = SocialRecommendationEngine._calculate_social_score(
                        movie, avg_rating, friend_count, rating_variance, user_preferences
                    )
                    
                    # Get top friends for this movie
                    top_friends = friends_by_movie.get(movie_id, [])

                    result.append({
                        "movie_id": movie_id,
                        "score": float(social_score),
                        "reason": SocialRecommendationEngine._generate_social_reason(
                            friend_count, avg_rating, movie, user_preferences
                        ),
                        "algorithm": "social",
                        "friend_count": friend_count,
                        "avg_friend_rating": avg_rating,
                        "top_friends": top_friends
                    })
            
            # Sort by score and limit
            result.sort(key=lambda x: x["score"], reverse=True)
            return result[skip : skip + limit]
            
        except Exception as e:
            logger.error(f"Error getting friend recommendations: {e}")
            return []
    
    @staticmethod
    def _get_user_preferences(user_id: int, db: Session) -> Dict:
        """Get user's genre and director preferences for social matching"""
        try:
            user_ratings = db.query(Rating).filter(Rating.user_id == user_id).order_by(Rating.rating.desc()).limit(20).all()
            
            if not user_ratings:
                return {"genres": [], "directors": []}
            
            genres = {}
            directors = {}
            
            for rating in user_ratings:
                movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                if movie:
                    # Count genres with rating weight
                    for genre in movie.genre.split(','):
                        genre = genre.strip()
                        genres[genre] = genres.get(genre, 0) + rating.rating
            
                    # Count directors with rating weight
                    if movie.director:
                        for director in movie.director.split(','):
                            director = director.strip()
                            directors[director] = directors.get(director, 0) + rating.rating
            
            return {
                "genres": sorted(genres.items(), key=lambda x: x[1], reverse=True),
                "directors": sorted(directors.items(), key=lambda x: x[1], reverse=True)
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {"genres": [], "directors": []}
    
    @staticmethod
    def _calculate_social_score(movie: Movie, avg_rating: float, friend_count: int, 
                              rating_variance: float, user_preferences: Dict) -> float:
        """Calculate advanced social recommendation score"""
        try:
            # Base score from friend ratings using Saturation Curve
            # Formula: 1 - 0.65^count -> 1=35%, 2=57.7%, 3=72.5%, 4=82%, 5=88%
            # This makes 100% significantly harder to hit without consensus.
            volume_score = 1.0 - (0.65 ** friend_count)
            base_score = (avg_rating / 5.0) * volume_score
            
            # Penalize high variance in friend ratings
            variance_penalty = max(0, 1 - (rating_variance / 2.0))
            base_score *= variance_penalty
            
            # Boost score if movie matches user's preferences
            preference_boost = 0.0
            movie_genres = [g.strip().lower() for g in movie.genre.split(',')]
            movie_directors = [d.strip().lower() for d in (movie.director or "").split(',')]
            
            # Genre preference boost
            if user_preferences.get("genres"):
                for preferred_genre, weight in user_preferences["genres"][:5]:  # Top 5 genres
                    if any(preferred_genre.lower() in mg for mg in movie_genres):
                        preference_boost += 0.1 # Reduced from 0.2
            
            # Director preference boost
            if user_preferences.get("directors") and movie.director:
                for preferred_director, weight in user_preferences["directors"][:3]:  # Top 3 directors
                    if any(preferred_director.lower() in md for md in movie_directors):
                        preference_boost += 0.1 # Reduced from 0.3
            
            # Overall movie quality boost
            if movie.avg_rating and movie.rating_count:
                quality_boost = (movie.avg_rating / 5.0) * min(movie.rating_count / 100, 1.0) * 0.1 # Reduced from 0.2
                base_score += quality_boost
            
            return min(base_score * (1 + preference_boost), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating social score: {e}")
            return 0.0
    
    @staticmethod
    def _generate_social_reason(friend_count: int, avg_rating: float, movie: Movie, 
                              user_preferences: Dict) -> str:
        """Generate intuitive, diverse social recommendation reasons"""
        try:
            import random
            genres = [g.strip() for g in movie.genre.split(',')]
            
            if friend_count >= 3:
                templates = [
                    f"Your inner circle has excellent taste—{friend_count} friends are raving about this!",
                    f"A total consensus: {friend_count} of your friends highy recommend this {genres[0]} hit.",
                    f"Major buzz in your network! {friend_count} friends gave this {avg_rating} stars.",
                    f"Don't be the last to know—{friend_count} friends already love this {genres[0]} film."
                ]
            elif friend_count == 2:
                templates = [
                    f"A solid recommendation from 2 friends who share your cinematic vibes.",
                    f"Double the proof: 2 friends rated this {avg_rating} stars.",
                    f"Two of your friends think this {genres[0]} story is a must-watch.",
                    f"2 friends are recommending this—it might just be your next favorite."
                ]
            else:
                templates = [
                    f"A trusted friend recommends this {genres[0]} gem.",
                    f"Word is spreading: one of your friends gave this a stellar {avg_rating} rating.",
                    f"Follow a friend's lead with locally-loved {genres[0]} cinema.",
                    f"Matches a friend's high rating—could be exactly what you're looking for."
                ]
            
            base_reason = random.choice(templates)
            
            # Add preference matching if available
            if user_preferences.get("genres"):
                user_fav = user_preferences["genres"][0][0]
                if any(user_fav.lower() in g.lower() for g in genres):
                    boosts = [
                        f" (Matches your {user_fav} preference perfectly)",
                        f" (Ideal for a {user_fav} fan like you)",
                        f" (Right in your {user_fav} sweet spot)"
                    ]
                    base_reason += random.choice(boosts)
            
            return base_reason
            
        except Exception as e:
            logger.error(f"Error generating social reason: {e}")
            return f"Highly recommended by {friend_count} friends in your network."
            
    @staticmethod
    def get_social_preview(user_id: int, movie_ids: List[int], db: Session) -> Dict[int, Dict]:
        """Get friend ratings for a specific set of movies (for previewing social proof)"""
        try:
            from app.models import Friendship
            # Get friends
            friendships = db.query(Friendship).filter(
                or_(Friendship.user_id == user_id, Friendship.friend_id == user_id)
            ).all()
            friend_ids = [f.friend_id if f.user_id == user_id else f.user_id for f in friendships]
            
            if not friend_ids:
                return {}
            
            # Get ratings for these movies from friends
            friend_ratings = db.query(
                Rating.movie_id,
                func.avg(Rating.rating).label('avg_rating'),
                func.count(Rating.id).label('friend_count')
            ).filter(
                Rating.user_id.in_(friend_ids),
                Rating.movie_id.in_(movie_ids)
            ).group_by(Rating.movie_id).all()
            
            return {r.movie_id: {"friend_count": r.friend_count, "avg_friend_rating": r.avg_rating} for r in friend_ratings}
        except Exception as e:
            logger.error(f"Error getting social preview: {e}")
            return {}


class MoodBasedRecommendation:
    """Generate recommendations based on user mood with advanced algorithms"""
    
    MOOD_TO_GENRES = {
        "happy": ["Comedy", "Animation", "Family", "Musical"],
        "sad": ["Drama", "Romance", "Tragedy"],
        "excited": ["Action", "Adventure", "Thriller", "Sci-Fi"],
        "relaxed": ["Comedy", "Drama", "Animation", "Slice of Life"],
        "thoughtful": ["Drama", "Documentary", "Sci-Fi", "Mystery", "Philosophical"],
        "scared": ["Horror", "Thriller", "Suspense", "Supernatural"]
    }
    
    # Mood-based director preferences
    MOOD_TO_DIRECTORS = {
        "happy": ["Wes Anderson", "Richard Linklater", "Greta Gerwig"],
        "sad": ["Denis Villeneuve", "Darren Aronofsky", "Lars von Trier"],
        "excited": ["Christopher Nolan", "James Cameron", "George Miller"],
        "relaxed": ["Hayao Miyazaki", "Wes Anderson", "Richard Linklater"],
        "thoughtful": ["Christopher Nolan", "Denis Villeneuve", "Stanley Kubrick"],
        "scared": ["James Wan", "Jordan Peele", "Ari Aster"]
    }
    
    @staticmethod
    def get_mood_recommendations(user_id: int, mood: str, db: Session, limit: int = 10, skip: int = 0) -> List[Dict]:
        """Get recommendations based on user's current mood with advanced scoring"""
        try:
            genres = MoodBasedRecommendation.MOOD_TO_GENRES.get(mood, ["Drama"])
            preferred_directors = MoodBasedRecommendation.MOOD_TO_DIRECTORS.get(mood, [])
            
            user_rated_movies = set([r.movie_id for r in db.query(Rating).filter(Rating.user_id == user_id).all()])
            
            # Get user's historical mood patterns
            user_mood_history = MoodBasedRecommendation._get_user_mood_history(user_id, db)
            
            # Get highly-rated movies in mood-appropriate genres
            # Use OR filters for genres to ensure we find matches at the database level
            genre_filters = [Movie.genre.ilike(f"%{g}%") for g in genres]
            
            recommendations = db.query(Movie).filter(
                Movie.id.notin_(user_rated_movies),
                Movie.avg_rating >= 3.0,  # Scale is 1-5
                or_(*genre_filters)
            ).order_by(Movie.avg_rating.desc(), Movie.rating_count.desc()).limit(limit * 3).all()
            
            result = []
            for movie in recommendations:
                if any(genre.lower() in movie.genre.lower() for genre in genres):
                    mood_score = MoodBasedRecommendation._calculate_mood_score(
                        movie, mood, preferred_directors, user_mood_history
                    )
                    
                    if mood_score > 0:
                        result.append({
                            "movie_id": movie.id,
                            "score": float(mood_score),
                            "reason": MoodBasedRecommendation._generate_mood_reason(movie, mood, preferred_directors),
                            "algorithm": "mood_based",
                            "mood_compatibility": mood_score
                        })
            
            # Sort by mood score and limit
            result.sort(key=lambda x: x["score"], reverse=True)
            return result[skip : skip + limit]
            
        except Exception as e:
            logger.error(f"Error getting mood recommendations: {e}")
            return []
    
    @staticmethod
    def _get_user_mood_history(user_id: int, db: Session) -> Dict:
        """Get user's historical mood patterns from ratings"""
        try:
            ratings = db.query(Rating).filter(
                Rating.user_id == user_id,
                Rating.mood.isnot(None)
            ).all()
            
            if not ratings:
                return {}
            
            mood_counts = Counter([rating.mood.value for rating in ratings])
            total_ratings = len(ratings)
            
            return {
                mood: count / total_ratings 
                for mood, count in mood_counts.items()
            }
            
        except Exception as e:
            logger.error(f"Error getting user mood history: {e}")
            return {}
    
    @staticmethod
    def _calculate_mood_score(movie: Movie, mood: str, preferred_directors: List[str], 
                            user_mood_history: Dict) -> float:
        """Calculate advanced mood-based recommendation score"""
        try:
            # Dynamic Weighting
            # If user has no director preferences, redistribute that 30% weight to Genre (20%) and Quality (10%)
            has_director_pref = len(preferred_directors) > 0
            
            w_genre = 0.4 if has_director_pref else 0.6
            w_director = 0.3 if has_director_pref else 0.0
            w_history = 0.2
            w_quality = 0.1 if has_director_pref else 0.2
            
            score = 0.0
            
            # Genre compatibility (Lenient: Any match gives full score)
            movie_genres = [g.strip().lower() for g in movie.genre.split(',')]
            mood_genres = [g.lower() for g in MoodBasedRecommendation.MOOD_TO_GENRES.get(mood, [])]
            
            if any(mg in mg2 for mg2 in mood_genres for mg in movie_genres):
                score += 1.0 * w_genre
            
            # Director compatibility
            if has_director_pref and movie.director:
                movie_directors = [d.strip().lower() for d in movie.director.split(',')]
                director_match = sum(1 for pd in preferred_directors if any(pd.lower() in md for md in movie_directors))
                # Even one match is great
                if director_match > 0:
                     score += 1.0 * w_director
            
            # User's historical mood preference
            if user_mood_history.get(mood, 0) > 0.3:  # User frequently rates in this mood
                score += user_mood_history[mood] * w_history
            
            # Movie quality factor
            if movie.avg_rating and movie.rating_count:
                quality_score = (movie.avg_rating / 5.0) * min(movie.rating_count / 50, 1.0)
                score += quality_score * w_quality
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating mood score: {e}")
            return 0.0
    
    @staticmethod
    def _generate_mood_reason(movie: Movie, mood: str, preferred_directors: List[str]) -> str:
        """Generate intuitive, diverse mood-based reasons"""
        try:
            import random
            genres = [g.strip() for g in movie.genre.split(',')]
            
            # Mood specific templates
            mood_templates = {
                "happy": [
                    f"Feeling happy? This {genres[0]} joyride is the perfect mood-booster.",
                    f"Keep the good vibes rolling with this uplifting {genres[0]} story.",
                    f"A visual celebration of happiness—exactly what you need right now."
                ],
                "sad": [
                    f"The ultimate companion for a thoughtful, quiet {mood} evening.",
                    f"Embrace the emotion with this powerful {genres[0]} drama.",
                    f"A beautiful, melancholy journey for your current mood."
                ],
                "excited": [
                    f"Fuel your adrenaline with this high-octane {genres[0]} thrill.",
                    f"Matches your energy! Get ready for a pulse-pounding experience.",
                    f"The perfect choice for a bold, exciting movie night."
                ],
                "relaxed": [
                    f"Unwind with this soothing, aesthetic {genres[0]} gem.",
                    f"Stress-free cinema: perfect for a relaxed, easy-going vibe.",
                    f"Kick back and enjoy this smooth-paced {genres[0]} masterpiece."
                ],
                "thoughtful": [
                    f"A visual brain-teaser that's perfect for your thoughtful mood.",
                    f"Deep, cinematic storytelling for the philosophical viewer.",
                    f"Get ready to reflect on this complex and rewarding {genres[0]} story."
                ],
                "scared": [
                    f"Ready for a fright? This is the ultimate spooky companion.",
                    f"A masterclass in suspense for when you want to feel the chill.",
                    f"Pure nightmare fuel—perfect for a scary movie marathon."
                ]
            }
            
            base_templates = mood_templates.get(mood, [f"Hand-picked for your {mood} vibe."])
            reason = random.choice(base_templates)
            
            # Add director info for extra punch
            if movie.director:
                movie_directors = [d.strip().lower() for d in movie.director.split(',')]
                for pd in preferred_directors:
                    if any(pd.lower() in md for md in movie_directors):
                        reasons_with_dir = [
                            f"{reason} Directed by the legendary {pd}.",
                            f"{reason} Features the visionary direction of {pd}.",
                            f"{reason} A classic piece of {pd} cinema."
                        ]
                        return random.choice(reasons_with_dir)
            
            return reason
            
        except Exception as e:
            logger.error(f"Error generating mood reason: {e}")
            return f"Perfect for when you're feeling {mood}"


class AdvancedUserProfiling:
    """Advanced user profiling and preference learning"""
    
    @staticmethod
    def update_user_profile(user_id: int, db: Session) -> bool:
        """Update user profile based on their rating patterns"""
        try:
            # Get user's ratings
            ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
            
            if not ratings:
                return False
            
            # Analyze genre preferences
            genre_scores = {}
            director_scores = {}
            mood_scores = {}
            
            for rating in ratings:
                movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                if movie:
                    # Genre scoring
                    for genre in movie.genre.split(','):
                        genre = genre.strip()
                        genre_scores[genre] = genre_scores.get(genre, 0) + rating.rating
                    
                    # Director scoring
                    if movie.director:
                        for director in movie.director.split(','):
                            director = director.strip()
                            director_scores[director] = director_scores.get(director, 0) + rating.rating
                
                # Mood scoring
                if rating.mood:
                    mood_scores[rating.mood.value] = mood_scores.get(rating.mood.value, 0) + rating.rating
            
            # Get or create user preference record
            user_pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            
            if not user_pref:
                user_pref = UserPreference(user_id=user_id)
                db.add(user_pref)
            
            # Update preferences
            if genre_scores:
                top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                user_pref.preferred_genres = ','.join([g for g, _ in top_genres])
            
            if director_scores:
                top_directors = sorted(director_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                user_pref.preferred_directors = ','.join([d for d, _ in top_directors])
            
            if mood_scores:
                top_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
                user_pref.favorite_mood = top_mood
            
            # Set language preference based on most watched
            language_counts = Counter()
            for rating in ratings:
                movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                if movie and movie.language:
                    language_counts[movie.language] += 1
            
            if language_counts:
                user_pref.preferred_language = language_counts.most_common(1)[0][0]
            
            user_pref.updated_at = datetime.utcnow()
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            db.rollback()
            return False
