import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Dict, Optional
import logging
from app.models import Movie, Rating, User
from app.services.ml_recommendations import ml_engine

logger = logging.getLogger(__name__)

class WatchPartyService:
    @staticmethod
    def get_group_recommendations(user_ids: List[int], db: Session, limit: int = 15) -> List[Dict]:
        """
        Generate recommendations for a group of users by averaging their latent preference vectors.
        """
        try:
            if not ml_engine.is_trained:
                ml_engine.train_model(db)
            
            # 1. Collect user profiles
            user_profiles = []
            for uid in user_ids:
                profile = ml_engine.create_user_profile(uid, db)
                if np.any(profile):
                    user_profiles.append(profile)
            
            if not user_profiles:
                # Fallback to popular if no profiles can be created
                return WatchPartyService._get_popular_fallback(db, limit)
            
            # 2. Compute the Group Centroid (Average Vector)
            group_profile = np.mean(user_profiles, axis=0)
            
            # 3. Get all movies and exclude already seen by ANYONE in the group
            seen_movie_ids = set()
            for uid in user_ids:
                user_ratings = db.query(Rating).filter(Rating.user_id == uid).all()
                for r in user_ratings:
                    seen_movie_ids.add(r.movie_id)
            
            all_movies = db.query(Movie).all()
            
            # 4. Rank movies by similarity to the Group Centroid
            recommendations = []
            g_norm = np.linalg.norm(group_profile)
            
            for movie in all_movies:
                if movie.id in seen_movie_ids:
                    continue
                
                if movie.id not in ml_engine.movie_id_to_idx:
                    similarity = 0
                else:
                    idx = ml_engine.movie_id_to_idx[movie.id]
                    movie_vector = ml_engine.movie_vectors[idx]
                    m_norm = np.linalg.norm(movie_vector)
                    
                    similarity = np.dot(group_profile, movie_vector) / (g_norm * m_norm) if g_norm > 0 and m_norm > 0 else 0
                
                # Combined score with popularity/rating
                pop_boost = (movie.popularity or 0) / 1000
                score = similarity + pop_boost
                
                recommendations.append({
                    "movie_id": movie.id,
                    "score": float(score),
                    "movie": movie
                })
            
            # 5. Sort and finalize
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            top_rec = recommendations[:limit]
            
            # 6. Generate group-aware reasons - optimized bulk lookup
            users = db.query(User).filter(User.id.in_(user_ids)).all()
            user_map = {u.id: u.username for u in users}
            user_names = [user_map[uid] for uid in user_ids if uid in user_map]
            user_names_str = f"{', '.join(user_names[:-1])} and {user_names[-1]}" if len(user_names) > 1 else user_names[0]
            
            result = []
            for rec in top_rec:
                movie = rec["movie"]
                genre = movie.genre.split(',')[0]
                result.append({
                    "id": movie.id,
                    "movie_id": movie.id,
                    "title": movie.title,
                    "poster_path": movie.poster_path,
                    "score": rec["score"],
                    "algorithm": "watch_party",
                    "reason": f"A perfect {genre} blend that balances the tastes of {user_names_str}.",
                    "movie": movie
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error in Watch Party recommendations: {e}")
            return WatchPartyService._get_popular_fallback(db, limit)

    @staticmethod
    def _get_popular_fallback(db: Session, limit: int) -> List[Dict]:
        popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()
        return [{
            "id": m.id,
            "movie_id": m.id,
            "title": m.title,
            "poster_path": m.poster_path,
            "score": 0.5,
            "algorithm": "watch_party",
            "reason": "Couldn't find a group match, showing popular movies for everyone!",
            "movie": m
        } for m in popular]
