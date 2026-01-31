from sqlalchemy.orm import Session
from app.models import Movie, Rating, User
from typing import Dict, Optional
import random

class AIExplainabilityService:
    """Generate human-readable explanations for why a movie was recommended"""
    
    @staticmethod
    def generate_movie_explanation(user_id: int, movie_id: int, db: Session) -> Dict:
        """
        Generate a personalized explanation for why this movie matches the user's taste
        """
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return AIExplainabilityService._get_fallback_explanation()
        
        # Get user's rating history
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).order_by(Rating.rating.desc()).limit(20).all()
        
        if not user_ratings or len(user_ratings) < 2:
            return AIExplainabilityService._get_new_user_explanation(movie)
        
        # Analyze user preferences
        genre_scores = {}
        director_scores = {}
        highly_rated_movies = []
        
        for rating in user_ratings:
            rated_movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie and rating.rating >= 4:
                highly_rated_movies.append(rated_movie)
                
                # Count genres
                for genre in rated_movie.genre.split(','):
                    genre = genre.strip()
                    genre_scores[genre] = genre_scores.get(genre, 0) + rating.rating
                
                # Count directors
                if rated_movie.director:
                    for director in rated_movie.director.split(','):
                        director = director.strip()
                        director_scores[director] = director_scores.get(director, 0) + rating.rating
        
        # Find matching patterns
        movie_genres = [g.strip() for g in movie.genre.split(',')]
        movie_directors = [d.strip() for d in (movie.director or "").split(',')] if movie.director else []
        
        # Calculate match reasons
        genre_matches = [g for g in movie_genres if g in genre_scores]
        director_match = next((d for d in movie_directors if d in director_scores), None)
        similar_movie = AIExplainabilityService._find_similar_movie(movie, highly_rated_movies)
        
        # Generate explanation
        return AIExplainabilityService._build_explanation(
            movie, genre_matches, director_match, similar_movie, genre_scores, director_scores
        )
    
    @staticmethod
    def _find_similar_movie(target_movie: Movie, user_favorites: list) -> Optional[Movie]:
        """Find a movie from user's favorites that's similar to the target"""
        target_genres = set(g.strip().lower() for g in target_movie.genre.split(','))
        
        best_match = None
        best_score = 0
        
        for fav in user_favorites:
            fav_genres = set(g.strip().lower() for g in fav.genre.split(','))
            overlap = len(target_genres & fav_genres)
            
            if overlap > best_score:
                best_score = overlap
                best_match = fav
        
        return best_match if best_score >= 1 else None
    
    @staticmethod
    def _build_explanation(movie: Movie, genre_matches: list, director_match: Optional[str], 
                          similar_movie: Optional[Movie], genre_scores: dict, director_scores: dict) -> Dict:
        """Build the explanation text and metrics"""
        
        # Calculate similarity score (0.0 to 1.0)
        similarity_score = 0.0
        
        if genre_matches:
            # More genre matches = higher score
            similarity_score += min(len(genre_matches) * 0.25, 0.6)
        
        if director_match:
            similarity_score += 0.2
        
        if similar_movie:
            similarity_score += 0.2
        
        similarity_score = min(similarity_score, 0.98)  # Cap at 0.98
        
        # Build reason text
        reasons = []
        
        if similar_movie:
            reasons.append(f"you enjoyed <span class='text-indigo-400'>{similar_movie.title}</span>")
        
        if genre_matches:
            if len(genre_matches) == 1:
                reasons.append(f"you frequently watch <span class='text-white'>{genre_matches[0]}</span> films")
            else:
                genre_list = " and ".join(genre_matches[:2])
                reasons.append(f"you love <span class='text-white'>{genre_list}</span> cinema")
        
        if director_match:
            reasons.append(f"<span class='text-indigo-400'>{director_match}</span> is one of your preferred directors")
        
        if not reasons:
            # Fallback based on movie quality
            if movie.vote_average and movie.vote_average >= 7.5:
                reason_text = f"This critically acclaimed {movie.genre.split(',')[0]} masterpiece aligns with high-quality cinema preferences detected in your neural profile."
            else:
                reason_text = f"This {movie.genre.split(',')[0]} film matches emerging patterns in your viewing behavior."
        else:
            connector = "Because " if len(reasons) == 1 else "Since "
            reason_text = connector + ", ".join(reasons) + f", CineAI identifies this as a {int(similarity_score * 100)}% match for your neural taste profile."
        
        # Determine latent zone (V1-V8 based on genre diversity)
        unique_genres = len(set(g.strip() for g in movie.genre.split(',')))
        latent_zone = f"V{min(unique_genres + 2, 8)}"
        
        # Add user-friendly description
        zone_descriptions = {
            "V1": "Single-genre classic",
            "V2": "Focused storytelling",
            "V3": "Dual-genre blend",
            "V4": "Multi-dimensional narrative",
            "V5": "Genre-crossing experience",
            "V6": "Complex hybrid film",
            "V7": "Highly diverse cinema",
            "V8": "Genre-defying masterpiece"
        }
        
        return {
            "reason": reason_text,
            "similarity": round(similarity_score, 2),
            "latent_zone": latent_zone,
            "zone_description": zone_descriptions.get(latent_zone, "Unique film"),
            "confidence": "high" if similarity_score >= 0.7 else "medium" if similarity_score >= 0.4 else "exploratory"
        }
    
    @staticmethod
    def _get_new_user_explanation(movie: Movie) -> Dict:
        """Explanation for users with little to no rating history"""
        genres = movie.genre.split(',')[0].strip()
        
        return {
            "reason": f"As you build your neural profile, CineAI recommends this {genres} film based on its exceptional ratings ({movie.vote_average:.1f}/10) and cultural impact. Your future ratings will refine these suggestions.",
            "similarity": 0.65,
            "latent_zone": "V3",
            "zone_description": "Dual-genre blend",
            "confidence": "exploratory"
        }
    
    @staticmethod
    def _get_fallback_explanation() -> Dict:
        """Fallback when movie not found"""
        return {
            "reason": "CineAI is analyzing this title against your neural profile. Check back soon for personalized insights.",
            "similarity": 0.50,
            "latent_zone": "V2",
            "zone_description": "Focused storytelling",
            "confidence": "low"
        }
