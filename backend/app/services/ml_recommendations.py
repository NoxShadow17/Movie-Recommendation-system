import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Movie, Rating, User
from app.core.config import RECOMMENDATION_COUNT
from app.utils.scoring import normalize_scores


class MLRecommendationEngine:
    """Machine Learning-based recommendation system using content and user behavior"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        self.scaler = StandardScaler()
        self.movie_features_matrix = None
        self.movie_vectors = None  # Latent space vectors for movies
        self.movie_id_to_idx = {}  # Mapping of movie_id to index in matrix
        self.user_profiles = {}
        self.movie_similarity_matrix = None
        self.is_trained = False
        # Dynamic path — works on local and Render
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'ml_models_cache.pkl'
        )
        
        # Try loading existing model on init
        self.load_model()
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'tfidf': self.tfidf_vectorizer,
                    'svd': self.svd_model,
                    'scaler': self.scaler,
                    'features': self.movie_features_matrix,
                    'vectors': self.movie_vectors,
                    'mapping': self.movie_id_to_idx,
                    'similarity': self.movie_similarity_matrix,
                    'timestamp': datetime.now()
                }, f)
            print("ML model saved to cache")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                print(f"Loading model from {self.model_path}...")
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.tfidf_vectorizer = data.get('tfidf')
                    self.svd_model = data.get('svd')
                    self.scaler = data.get('scaler')
                    self.movie_features_matrix = data.get('features')
                    self.movie_vectors = data.get('vectors')
                    self.movie_id_to_idx = data.get('mapping', {})
                    self.movie_similarity_matrix = data.get('similarity')
                    self.is_trained = True
                print("ML model loaded from cache")
            else:
                print(f"No model cache found at {self.model_path}")
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False

    def train_model(self, db: Session, force: bool = False):
        """Train the ML recommendation model"""
        if self.is_trained and not force:
            return True

        try:
            print("Training ML recommendation model...")
            
            # Get all movies
            movies = db.query(Movie).all()
            if not movies:
                print("No movies found for training")
                return False
            
            # Prepare movie features
            movie_features = self.prepare_movie_features(movies)
            self.movie_id_to_idx = {m.id: i for i, m in enumerate(movies)}
            
            # Fit TF-IDF vectorizer on content features
            content_matrix = self.tfidf_vectorizer.fit_transform(movie_features['content_features'])
            
            # Scale numerical features
            cols = ['runtime', 'budget', 'revenue', 'popularity', 'vote_average', 'vote_count']
            for col in cols:
                if col not in movie_features.columns:
                    movie_features[col] = 0
                    
            numerical_features = movie_features[cols].fillna(0).values
            numerical_features_scaled = self.scaler.fit_transform(numerical_features)
            
            # Combine all features
            self.movie_features_matrix = np.hstack([content_matrix.toarray(), numerical_features_scaled])
            
            # Transform movie features
            self.movie_vectors = self.svd_model.fit_transform(self.movie_features_matrix)
            
            # Calculate movie similarity matrix
            self.movie_similarity_matrix = cosine_similarity(self.movie_vectors)
            
            self.is_trained = True
            
            # Save the trained model
            self.save_model()
            
            return True
            
        except Exception as e:
            print(f"Error training ML model: {e}")
            return False
    
    def get_ml_recommendations(self, user_id: int, db: Session, limit: int = RECOMMENDATION_COUNT, skip: int = 0) -> List[Dict]:
        """Get ML-based recommendations for a user"""
        if not self.is_trained:
            # Fallback to content-based if not trained
            return self._get_content_based_fallback(user_id, db, limit)
        
        try:
            # Create user profile
            user_profile = self.create_user_profile(user_id, db)
            
            if np.all(user_profile == 0):
                # New user - return popular movies
                return self._get_popular_movies(db, limit)
            
            # Get all movie IDs
            all_movies = db.query(Movie).all()
            movie_ids = [m.id for m in all_movies]
            
            # Get user's rated movies to exclude them
            user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
            rated_movie_ids = set(r.movie_id for r in user_ratings)
            
            import math
            import random
            
            # Calculate recommendations
            recommendations = []
            u_norm = np.linalg.norm(user_profile)
            
            for i, movie in enumerate(all_movies):
                if movie.id in rated_movie_ids:
                    continue
                
                # 1. Personalization Score (Cosine Similarity)
                if movie.id not in self.movie_id_to_idx:
                    movie_similarity = 0
                else:
                    idx = self.movie_id_to_idx[movie.id]
                    movie_vector = self.movie_vectors[idx]
                    m_norm = np.linalg.norm(movie_vector)
                    movie_similarity = np.dot(user_profile, movie_vector) / (u_norm * m_norm) if u_norm > 0 and m_norm > 0 else 0
                
                # 2. Non-Linear Popularity Score (Logarithmic scaling)
                # This prevents a movie with 10k popularity from drowning out niche gems
                pop_value = float(movie.popularity or 0)
                log_popularity = math.log10(pop_value + 1) / 4.0  # Normalize (assuming max pop ~10k)
                log_popularity = min(log_popularity, 1.0)
                
                # 3. Quality Score (Normalized Rating)
                rating_score = (float(movie.avg_rating or 0)) / 10.0 # TMDB is 0-10
                
                # 4. Weighted Fusion
                # Weights: 70% Personalization, 15% Popularity, 15% Rating
                personalization_weight = 0.70
                popularity_weight = 0.15
                rating_weight = 0.15
                
                # Base score
                base_score = (movie_similarity * personalization_weight) + \
                             (log_popularity * popularity_weight) + \
                             (rating_score * rating_weight)
                
                # 5. Diversity Injection (Minor controlled noise)
                # Ensures similar users get slightly different top picks
                diversity_noise = random.uniform(0, 0.05)
                final_score = base_score + diversity_noise
                
                recommendations.append({
                    "movie_id": movie.id,
                    "score": float(final_score),
                    "movie": movie,
                    "debug_info": {
                        "sim": movie_similarity,
                        "pop": log_popularity,
                        "rating": rating_score
                    }
                })
            
            # Sort by score and take top candidates with pagination
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            # Apply pagination
            paginated_recs = recommendations[skip : skip + limit]
            
            # Add reasons only for the top results (to save DB queries)
            for rec in paginated_recs:
                rec["reason"] = self._generate_ml_reason(user_id, rec["movie"], db)
                del rec["movie"] # Clean up
                
            # Normalize scores to [0.6, 0.98] range for UI
            normalized_recs = normalize_scores(paginated_recs, min_val=0.75, max_val=0.98)
            
            return normalized_recs
            
        except Exception as e:
            print(f"Error in ML recommendations: {e}")
            return self._get_content_based_fallback(user_id, db, limit)
    
    def _get_content_based_fallback(self, user_id: int, db: Session, limit: int) -> List[Dict]:
        """Fallback content-based recommendations using TF-IDF"""
        try:
            movies = db.query(Movie).all()
            if not movies:
                return []
            
            # Check if vectorizer is fitted
            from sklearn.utils.validation import check_is_fitted
            try:
                check_is_fitted(self.tfidf_vectorizer)
            except:
                # If not fitted, return popular movies
                print("TF-IDF vectorizer not fitted. Falling back to popular movies.")
                return self._get_popular_movies(db, limit)
            
            # Get user's high-rated movies
            high_rated = db.query(Rating).filter(
                Rating.user_id == user_id,
                Rating.rating >= 4.0
            ).all()
            
            if not high_rated:
                return self._get_popular_movies(db, limit)
            
            # Get content features for all movies
            movie_features = self.prepare_movie_features(movies)
            
            # Calculate TF-IDF similarity
            content_matrix = self.tfidf_vectorizer.transform(movie_features['content_features'])
            similarity_matrix = cosine_similarity(content_matrix)
            
            # Find similar movies to user's high-rated ones
            recommendations = {}
            rated_movie_indices = [i for i, m in enumerate(movies) if m.id in [r.movie_id for r in high_rated]]
            
            for idx in rated_movie_indices:
                similar_scores = similarity_matrix[idx]
                
                for i, score in enumerate(similar_scores):
                    if i != idx and movies[i].id not in [r.movie_id for r in high_rated]:
                        if movies[i].id not in recommendations:
                            recommendations[movies[i].id] = 0
                        recommendations[movies[i].id] += score
            
            # Sort and return recommendations
            sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
            
            result = []
            for movie_id, score in sorted_recs[:limit]:
                movie = db.query(Movie).filter(Movie.id == movie_id).first()
                if movie:
                    result.append({
                        "movie_id": movie_id,
                        "score": float(score),
                        "reason": "Based on movies you liked"
                    })
            
            if result:
                return normalize_scores(result, min_val=0.7, max_val=0.95)
            
            return self._get_popular_movies(db, limit)
            
        except Exception as e:
            print(f"Error in content-based fallback: {e}")
            return self._get_popular_movies(db, limit)
    
    def _get_popular_movies(self, db: Session, limit: int) -> List[Dict]:
        """Get popular movies for new users"""
        try:
            popular_movies = db.query(Movie).filter(
                Movie.popularity > 0,
                Movie.rating_count > 10
            ).order_by(Movie.popularity.desc()).limit(limit).all()
            
            results = [{
                "movie_id": movie.id,
                "score": float(movie.popularity or 0),
                "reason": "Popular with other users"
            } for movie in popular_movies]
            
            return normalize_scores(results, min_val=0.6, max_val=0.92)
            
        except Exception as e:
            print(f"Error getting popular movies: {e}")
            return []
    
    def prepare_movie_features(self, movies: List[Movie]) -> pd.DataFrame:
        """Extract and clean features from movie objects for ML"""
        data = []
        for m in movies:
            # Combine text features for content-based filtering
            content = f"{m.title} {m.genre} {m.director} {m.cast} {m.keywords or ''} {m.overview or ''}"
            
            data.append({
                'id': m.id,
                'content_features': content.lower(),
                'popularity': m.popularity or 0,
                'vote_average': m.vote_average or 0,
                'release_year': m.release_year or 2000,
                'budget': m.budget or 0,
                'revenue': m.revenue or 0
            })
            
        return pd.DataFrame(data)
        
    def create_user_profile(self, user_id: int, db: Session) -> np.ndarray:
        """Create a user profile vector in the latent space based on ratings"""
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        
        if not user_ratings or not self.is_trained:
            return np.zeros(self.svd_model.n_components)
            
        # Weighted average of movie vectors based on user ratings
        user_profile = np.zeros(self.svd_model.n_components)
        total_weight = 0
        
        for rating in user_ratings:
            if rating.movie_id in self.movie_id_to_idx:
                idx = self.movie_id_to_idx[rating.movie_id]
                movie_vector = self.movie_vectors[idx]
                
                # Weight by rating (centered around 3)
                weight = rating.rating - 2.5
                user_profile += movie_vector * weight
                total_weight += abs(weight)
                
        if total_weight > 0:
            user_profile /= total_weight
            
        return user_profile

    def _generate_ml_reason(self, user_id: int, movie: Movie, db: Session) -> str:
        """Generate AI-powered, intuitive recommendation reason"""
        try:
            import random
            
            # Analyze user's top genres from highly rated movies
            user_ratings = db.query(Rating).filter(Rating.user_id == user_id, Rating.rating >= 4.0).all()
            if not user_ratings:
                # New user/discovery templates
                templates = [
                    f"A trending {movie.genre.split(',')[0]} masterpiece you shouldn't miss.",
                    f"Everyone's talking about this—perfect for starting your movie journey.",
                    f"A high-rated {movie.genre.split(',')[0]} gem ready for discovery.",
                    f"Jump into the action with this popular {movie.genre.split(',')[0]} pick."
                ]
                return random.choice(templates)
            
            # Analyze top genres and recent favorites
            genres_count = {}
            favorite_movies = []
            for rating in sorted(user_ratings, key=lambda x: x.created_at, reverse=True)[:5]:
                rated_movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                if rated_movie:
                    favorite_movies.append(rated_movie.title)
                    for g in rated_movie.genre.split(','):
                        g = g.strip()
                        genres_count[g] = genres_count.get(g, 0) + 1
            
            movie_genres = [g.strip() for g in movie.genre.split(',')]
            top_genre = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)[0][0] if genres_count else None
            
            # 1. Similarity to specific favorite movies
            if favorite_movies:
                target_movie = random.choice(favorite_movies)
                templates = [
                    f"Since you enjoyed {target_movie}, this similar {movie_genres[0]} journey is a perfect follow-up.",
                    f"Fans of {target_movie} often find their next favorite in this {movie_genres[0]} hit.",
                    f"Matches the atmosphere of {target_movie}—ideal for your next watch session.",
                    f"Love {target_movie}? Get ready for another deep-dive into {movie_genres[0]} cinematic excellence."
                ]
                # Only use movie-match if they actually share a genre or we hit a random chance
                if any(g in genres_count for g in movie_genres) or random.random() > 0.5:
                    return random.choice(templates)
            
            # 2. Strong Genre Match
            if top_genre and top_genre in movie_genres:
                templates = [
                    f"Your love for {top_genre} films makes this a must-watch choice.",
                    f"Diving deep into {top_genre}? This is one of the best the genre has to offer.",
                    f"Another {top_genre} classic—tailored specifically for your cinema palette.",
                    f"We noticed your interest in {top_genre}—here's a fresh take you'll love."
                ]
                return random.choice(templates)
            
            # 3. Quality/Popularity based
            if movie.avg_rating and movie.avg_rating >= 8.0:
                return f"A critically acclaimed {movie_genres[0]} experience that lives up to the hype."
            
            if movie.popularity and movie.popularity > 100:
                return f"Global hit alert: This {movie_genres[0]} movie is taking the world by storm."
            
            return f"A hand-picked {movie_genres[0]} recommendation tailored just for your vibe."
            
        except Exception as e:
            print(f"Error generating ML reason: {e}")
            return f"Strategic {movie.genre.split(',')[0]} pick based on your taste profile."


# Global ML recommendation engine instance
ml_engine = MLRecommendationEngine()
