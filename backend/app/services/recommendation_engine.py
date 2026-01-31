import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Movie, Rating, User, Recommendation, UserPreference
from app.core.config import COLLABORATIVE_WEIGHT, CONTENT_BASED_WEIGHT, MIN_COMMON_RATINGS, RECOMMENDATION_COUNT
from app.services.cache_service import RecommendationCache, CacheInvalidator


class CollaborativeFiltering:
    """User-based collaborative filtering recommendation"""
    
    @staticmethod
    def get_similar_users(user_id: int, db: Session, min_common_ratings: int = MIN_COMMON_RATINGS) -> List[Tuple[int, float]]:
        """Find similar users based on rating patterns - optimized with bulk queries"""
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        
        if not user_ratings:
            return []
        
        user_movie_ids = set([r.movie_id for r in user_ratings])
        user_rating_dict = {r.movie_id: r.rating for r in user_ratings}
        
        # Find all other users who rated the same movies - optimized bulk query
        # Get all ratings from other users for movies that our target user has rated
        other_user_ratings = db.query(Rating).filter(
            Rating.user_id != user_id,
            Rating.movie_id.in_(user_movie_ids)
        ).all()
        
        # Group ratings by user
        user_ratings_map = {}
        for rating in other_user_ratings:
            if rating.user_id not in user_ratings_map:
                user_ratings_map[rating.user_id] = {}
            user_ratings_map[rating.user_id][rating.movie_id] = rating.rating
        
        similar_users = []
        
        for other_user_id, other_rating_dict in user_ratings_map.items():
            common_movies = user_movie_ids.intersection(set(other_rating_dict.keys()))
            
            if len(common_movies) >= min_common_ratings:
                # Calculate cosine similarity
                similarity = CollaborativeFiltering._cosine_similarity(
                    user_rating_dict,
                    other_rating_dict,
                    common_movies
                )
                
                if similarity > 0:
                    similar_users.append((other_user_id, similarity))
        
        return sorted(similar_users, key=lambda x: x[1], reverse=True)
    
    @staticmethod
    def _cosine_similarity(dict1: Dict, dict2: Dict, common_keys: set) -> float:
        """Calculate cosine similarity between two rating dictionaries"""
        if not common_keys:
            return 0.0
        
        ratings1 = np.array([dict1[k] for k in common_keys])
        ratings2 = np.array([dict2[k] for k in common_keys])
        
        dot_product = np.dot(ratings1, ratings2)
        norm1 = np.linalg.norm(ratings1)
        norm2 = np.linalg.norm(ratings2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def recommend(user_id: int, db: Session, limit: int = RECOMMENDATION_COUNT) -> List[Tuple[int, float]]:
        """Get collaborative recommendations"""
        similar_users = CollaborativeFiltering.get_similar_users(user_id, db)
        
        if not similar_users:
            return []
        
        user_rated_movies = set([r.movie_id for r in db.query(Rating).filter(Rating.user_id == user_id).all()])
        
        recommendations = {}
        
        for similar_user_id, similarity in similar_users:
            similar_user_ratings = db.query(Rating).filter(Rating.user_id == similar_user_id).all()
            
            for rating in similar_user_ratings:
                if rating.movie_id not in user_rated_movies:
                    if rating.movie_id not in recommendations:
                        recommendations[rating.movie_id] = []
                    recommendations[rating.movie_id].append(rating.rating * similarity)
        
        # Calculate weighted average scores
        movie_scores = {
            movie_id: np.mean(scores) 
            for movie_id, scores in recommendations.items()
        }
        
        return sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:limit]


class ContentBasedFiltering:
    """Content-based recommendation based on movie attributes"""
    
    @staticmethod
    def get_user_preferences(user_id: int, db: Session) -> Dict:
        """Get user's genre and director preferences - optimized with bulk query"""
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).order_by(Rating.rating.desc()).limit(20).all()
        
        if not user_ratings:
            return {"genres": [], "directors": []}
        
        # Get all movies in one query instead of N queries
        movie_ids = [r.movie_id for r in user_ratings]
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        movie_map = {m.id: m for m in movies}
        
        genres = {}
        directors = {}
        
        for rating in user_ratings:
            movie = movie_map.get(rating.movie_id)
            if movie:
                # Count genres
                for genre in movie.genre.split(','):
                    genre = genre.strip()
                    genres[genre] = genres.get(genre, 0) + rating.rating
                
                # Count directors
                if movie.director:
                    for director in movie.director.split(','):
                        director = director.strip()
                        directors[director] = directors.get(director, 0) + rating.rating
        
        return {
            "genres": sorted(genres.items(), key=lambda x: x[1], reverse=True),
            "directors": sorted(directors.items(), key=lambda x: x[1], reverse=True)
        }
    
    @staticmethod
    def movie_similarity(movie1: Movie, movie2: Movie) -> float:
        """Calculate similarity between two movies"""
        if not movie1 or not movie2:
            return 0.0
        
        movie1_genres = set([g.strip() for g in movie1.genre.split(',')])
        movie2_genres = set([g.strip() for g in movie2.genre.split(',')])
        
        # Genre similarity
        if movie1_genres and movie2_genres:
            genre_similarity = len(movie1_genres.intersection(movie2_genres)) / len(movie1_genres.union(movie2_genres))
        else:
            genre_similarity = 0.0
        
        # Director similarity
        director_similarity = 0.0
        if movie1.director and movie2.director:
            movie1_directors = set([d.strip() for d in movie1.director.split(',')])
            movie2_directors = set([d.strip() for d in movie2.director.split(',')])
            if movie1_directors and movie2_directors:
                director_similarity = len(movie1_directors.intersection(movie2_directors)) / len(movie1_directors.union(movie2_directors)) * 0.5
        
        # Language similarity
        language_similarity = 0.3 if movie1.language == movie2.language else 0.0
        
        return genre_similarity * 0.5 + director_similarity + language_similarity
    
    @staticmethod
    def recommend(user_id: int, db: Session, limit: int = RECOMMENDATION_COUNT) -> List[Tuple[int, float]]:
        """Get content-based recommendations"""
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        
        if not user_ratings:
            return []
        
        user_rated_movies = set([r.movie_id for r in user_ratings])
        rated_movies = [db.query(Movie).filter(Movie.id == r.movie_id).first() for r in user_ratings]
        
        all_movies = db.query(Movie).filter(Movie.id.notin_(user_rated_movies)).all()
        
        movie_scores = {}
        
        for movie in all_movies:
            similarity_scores = []
            
            for rated_movie in rated_movies:
                if rated_movie:
                    similarity = ContentBasedFiltering.movie_similarity(rated_movie, movie)
                    similarity_scores.append(similarity)
            
            if similarity_scores:
                movie_scores[movie.id] = np.mean(similarity_scores)
        
        return sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:limit]


class HybridRecommendationEngine:
    """Hybrid recommendation system combining collaborative and content-based filtering"""
    
    @staticmethod
    def get_recommendations(user_id: int, db: Session, limit: int = RECOMMENDATION_COUNT) -> List[Dict]:
        """Get hybrid recommendations with proper weighting and personalization"""
        try:
            # Get user preferences for personalization
            user_preferences = HybridRecommendationEngine._get_user_preferences(user_id, db)
            
            # Get collaborative recommendations
            collab_recommendations = CollaborativeFiltering.recommend(user_id, db, limit * 3)
            collab_dict = dict(collab_recommendations)
            
            # Get content-based recommendations
            content_recommendations = ContentBasedFiltering.recommend(user_id, db, limit * 3)
            content_dict = dict(content_recommendations)
            
            # Get user's genre/director preferences for enhanced content filtering
            enhanced_content_scores = HybridRecommendationEngine._get_enhanced_content_scores(user_id, db, user_preferences)
            
            # Merge scores with proper normalization and personalization
            all_movie_ids = set(collab_dict.keys()).union(set(content_dict.keys())).union(set(enhanced_content_scores.keys()))
            
            hybrid_scores = {}
            for movie_id in all_movie_ids:
                # Get base scores
                collab_score = collab_dict.get(movie_id, 0.0)
                content_score = content_dict.get(movie_id, 0.0)
                enhanced_content_score = enhanced_content_scores.get(movie_id, 0.0)
                
                # Normalize scores to 0-1 range for fair comparison
                normalized_collab = collab_score / 5.0 if collab_score > 0 else 0.0
                normalized_content = content_score if content_score > 0 else 0.0
                normalized_enhanced = enhanced_content_score if enhanced_content_score > 0 else 0.0
                
                # Apply hybrid weighting with enhanced content-based filtering
                # 60% collaborative + 20% enhanced content + 20% basic content
                # Increased collaborative weight for more diversity
                hybrid_score = (
                    COLLABORATIVE_WEIGHT * 0.9 * normalized_collab +
                    CONTENT_BASED_WEIGHT * 0.3 * normalized_enhanced +
                    CONTENT_BASED_WEIGHT * 0.3 * normalized_content
                )
                
                # Apply personalization boost for preferred genres/directors
                movie = db.query(Movie).filter(Movie.id == movie_id).first()
                if movie and user_preferences:
                    personalization_boost = HybridRecommendationEngine._calculate_personalization_boost(movie, user_preferences)
                    hybrid_score *= (1 + personalization_boost)
                
                hybrid_scores[movie_id] = hybrid_score
            
            # Sort and get top recommendations with forced genre diversity
            sorted_recommendations = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Force genre diversity by ensuring we get movies from different genres
            diverse_recommendations = []
            selected_genres = set()
            genre_counts = {}
            
            # First pass: try to get diverse genres
            for movie_id, score in sorted_recommendations:
                if len(diverse_recommendations) >= limit:
                    break
                    
                movie = db.query(Movie).filter(Movie.id == movie_id).first()
                if not movie:
                    continue
                
                # Get movie genres
                movie_genres = [g.strip().lower() for g in movie.genre.split(',')]
                
                # Check if this movie introduces new genres
                new_genres = [g for g in movie_genres if g not in selected_genres]
                
                if new_genres or len(selected_genres) == 0:
                    # This movie has new genres, add it
                    diverse_recommendations.append((movie_id, score))
                    
                    # Update genre tracking
                    for genre in movie_genres:
                        selected_genres.add(genre)
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
                else:
                    # This movie only has genres we already have, apply heavy penalty
                    genre_penalty = 0.4  # 40% penalty for non-diverse movies
                    adjusted_score = score * (1 - genre_penalty)
                    
                    # Only add if still competitive after penalty
                    if len(diverse_recommendations) < limit:
                        diverse_recommendations.append((movie_id, adjusted_score))
                        
                        # Update genre tracking
                        for genre in movie_genres:
                            genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Sort the diverse recommendations by score again
            diverse_recommendations = sorted(diverse_recommendations, key=lambda x: x[1], reverse=True)
            
            # If we still don't have enough recommendations, fill with remaining high-scoring ones
            if len(diverse_recommendations) < limit:
                remaining = [item for item in sorted_recommendations if item[0] not in [r[0] for r in diverse_recommendations]]
                diverse_recommendations.extend(remaining[:limit - len(diverse_recommendations)])
            
            top_recommendations = diverse_recommendations[:limit]
            
            result = []
            for movie_id, score in top_recommendations:
                movie = db.query(Movie).filter(Movie.id == movie_id).first()
                if movie:
                    reason = HybridRecommendationEngine._generate_reason(user_id, movie, db)
                    recommendation_data = {
                        "movie_id": movie_id,
                        "score": float(score),
                        "reason": reason,
                        "algorithm": "hybrid"
                    }
                    
                    # Save recommendation to database for tracking
                    try:
                        HybridRecommendationEngine._save_recommendation(user_id, movie_id, score, reason, db)
                    except Exception as e:
                        print(f"Warning: Could not save recommendation: {e}")
                    
                    result.append(recommendation_data)
            
            return result
        except Exception as e:
            print(f"Error in hybrid recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def _get_user_preferences(user_id: int, db: Session) -> Dict:
        """Get user's stored preferences"""
        from app.models import UserPreference
        
        user_pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if user_pref:
            return {
                "preferred_genres": [g.strip() for g in user_pref.preferred_genres.split(',')] if user_pref.preferred_genres else [],
                "preferred_directors": [d.strip() for d in user_pref.preferred_directors.split(',')] if user_pref.preferred_directors else [],
                "preferred_language": user_pref.preferred_language,
                "favorite_mood": user_pref.favorite_mood
            }
        return {}
    
    @staticmethod
    def _get_enhanced_content_scores(user_id: int, db: Session, user_preferences: Dict) -> Dict:
        """Get enhanced content-based scores using user preferences"""
        from app.models import Rating, Movie
        
        # Get user's high-rated movies
        high_rated = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 4.0
        ).all()
        
        if not high_rated:
            return {}
        
        # Get user's preferred attributes from stored preferences
        preferred_genres = user_preferences.get("preferred_genres", [])
        preferred_directors = user_preferences.get("preferred_directors", [])
        
        # Find all unrated movies
        rated_movie_ids = set(r.movie_id for r in high_rated)
        unrated_movies = db.query(Movie).filter(Movie.id.notin_(rated_movie_ids)).all()
        
        enhanced_scores = {}
        
        for movie in unrated_movies:
            score = 0.0
            
            # Genre preference boost (more diverse approach)
            movie_genres = [g.strip().lower() for g in movie.genre.split(',')]
            if preferred_genres:
                # Check for matches with top 3 genres instead of just the favorite
                top_3_genres = preferred_genres[:3]
                genre_match = sum(1 for pg in top_3_genres if any(pg.lower() in mg for mg in movie_genres))
                # Significantly reduce the weight to allow more variety
                score += (genre_match / len(top_3_genres)) * 0.1
            
            # Director preference boost
            if movie.director and preferred_directors:
                movie_directors = [d.strip().lower() for d in movie.director.split(',')]
                director_match = sum(1 for pd in preferred_directors if any(pd.lower() in md for md in movie_directors))
                score += (director_match / len(preferred_directors)) * 0.15
            
            # Language preference
            if user_preferences.get("preferred_language") and movie.language:
                if user_preferences["preferred_language"].lower() == movie.language.lower():
                    score += 0.08
            
            # Overall movie quality (popularity + rating) - increased weight for diversity
            if movie.avg_rating and movie.rating_count:
                quality_score = (movie.avg_rating / 5.0) * (min(movie.rating_count, 100) / 100.0)
                score += quality_score * 0.5
            
            # Add diversity boost for movies with different genres than user's top genre
            if preferred_genres and movie_genres:
                top_genre = preferred_genres[0].lower()
                has_top_genre = any(top_genre in mg for mg in movie_genres)
                if not has_top_genre:
                    # Small boost for genre diversity
                    score += 0.05
            
            # Add boost for movies with high ratings from similar users (collaborative signal)
            similar_user_ratings = db.query(Rating).filter(
                Rating.movie_id == movie.id,
                Rating.rating >= 4.0
            ).count()
            if similar_user_ratings > 3:
                score += 0.1
            
            if score > 0:
                enhanced_scores[movie.id] = score
        
        return enhanced_scores
    
    @staticmethod
    def _calculate_personalization_boost(movie: Movie, user_preferences: Dict) -> float:
        """Calculate personalization boost based on user preferences"""
        boost = 0.0
        
        # Genre boost
        if user_preferences.get("preferred_genres"):
            movie_genres = [g.strip().lower() for g in movie.genre.split(',')]
            for preferred_genre in user_preferences["preferred_genres"]:
                if any(preferred_genre.lower() in mg for mg in movie_genres):
                    boost += 0.1
        
        # Director boost
        if user_preferences.get("preferred_directors") and movie.director:
            movie_directors = [d.strip().lower() for d in movie.director.split(',')]
            for preferred_director in user_preferences["preferred_directors"]:
                if any(preferred_director.lower() in md for md in movie_directors):
                    boost += 0.15
        
        # Language boost
        if (user_preferences.get("preferred_language") and movie.language and 
            user_preferences["preferred_language"].lower() == movie.language.lower()):
            boost += 0.05
        
        return min(boost, 0.5)  # Cap boost at 50%
    
    @staticmethod
    def _save_recommendation(user_id: int, movie_id: int, score: float, reason: str, db: Session):
        """Save recommendation to database for tracking and analytics"""
        from app.models import Recommendation
        
        # Check if recommendation already exists
        existing = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.movie_id == movie_id
        ).first()
        
        if existing:
            # Update existing recommendation
            existing.score = score
            existing.reason = reason
            existing.created_at = datetime.utcnow()
        else:
            # Create new recommendation
            recommendation = Recommendation(
                user_id=user_id,
                movie_id=movie_id,
                score=score,
                reason=reason,
                algorithm="hybrid"
            )
            db.add(recommendation)
        
        db.commit()
    
    @staticmethod
    def _generate_reason(user_id: int, movie: Movie, db: Session) -> str:
        """Generate human-readable recommendation reason - optimized with bulk queries"""
        user_prefs = ContentBasedFiltering.get_user_preferences(user_id, db)
        
        # Check for genre match (but don't be too restrictive)
        if user_prefs["genres"]:
            genres = movie.genre.split(',')
            user_favorite_genre = user_prefs["genres"][0][0] if user_prefs["genres"] else None
            
            # Check if movie matches user's favorite genre
            if user_favorite_genre and any(user_favorite_genre.lower() in g.lower() for g in genres):
                return f"Based on your interest in {user_favorite_genre} films"
            
            # Check if movie matches any of user's top 3 genres
            top_genres = [g[0] for g in user_prefs["genres"][:3]]
            for genre in genres:
                genre_clean = genre.strip().lower()
                for user_genre in top_genres:
                    if user_genre.lower() in genre_clean:
                        return f"Similar to {user_genre} films you enjoyed"
        
        # Check for director match
        if user_prefs["directors"]:
            user_favorite_director = user_prefs["directors"][0][0] if user_prefs["directors"] else None
            if user_favorite_director and movie.director and user_favorite_director.lower() in movie.director.lower():
                return f"Featuring director {user_favorite_director} you love"
        
        # Check for language preference - optimized bulk query
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        if user_ratings:
            # Get all movies in one query instead of N queries
            movie_ids = [r.movie_id for r in user_ratings]
            movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
            movie_map = {m.id: m for m in movies}
            
            # Get user's preferred language from their ratings
            from collections import Counter
            languages = [movie_map[r.movie_id].language 
                        for r in user_ratings if r.movie_id in movie_map and movie_map[r.movie_id].language]
            if languages:
                preferred_lang = Counter(languages).most_common(1)[0][0]
                if movie.language and movie.language.lower() == preferred_lang.lower():
                    return f"In your preferred language ({preferred_lang})"
        
        # Check for overall quality/popularity
        if movie.avg_rating and movie.avg_rating >= 7.0:
            return "Highly rated by other users"
        
        # Check for recent popularity
        from datetime import datetime, timedelta
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_ratings = db.query(Rating).filter(
            Rating.movie_id == movie.id,
            Rating.created_at >= recent_date
        ).count()
        
        if recent_ratings > 5:
            return "Recently popular with users like you"
        
        return "Recommended based on your overall preferences"
