#!/usr/bin/env python3
"""
Advanced Collaborative Filtering Models
Implements sophisticated collaborative filtering algorithms for movie recommendations.
"""

import numpy as np
import pandas as pd
import sqlite3
import json
from sklearn.decomposition import TruncatedSVD, NMF
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedCollaborativeFiltering:
    def __init__(self, db_path: str = "movie_recommendation.db"):
        self.db_path = db_path
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_features = None
        self.item_features = None
        self.model = None
        self.scaler = StandardScaler()
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load user, movie, and rating data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load ratings
            ratings_query = """
                SELECT user_id, movie_id, rating 
                FROM ratings 
                WHERE rating IS NOT NULL
            """
            ratings_df = pd.read_sql_query(ratings_query, conn)
            
            # Load users
            users_query = """
                SELECT id, username, email 
                FROM users 
                WHERE is_active = 1
            """
            users_df = pd.read_sql_query(users_query, conn)
            
            # Load movies with existing schema
            movies_query = """
                SELECT id, title, genre, director, cast,
                       runtime, popularity, avg_rating, release_date
                FROM movies
            """
            movies_df = pd.read_sql_query(movies_query, conn)
            
            conn.close()
            
            # Parse string fields into lists
            for col in ['genre', 'director', 'cast']:
                if col in movies_df.columns:
                    movies_df[col] = movies_df[col].apply(lambda x: [g.strip() for g in (x or '').split(',')] if x else [])
            
            # Rename columns to match expected format
            movies_df = movies_df.rename(columns={
                'genre': 'genres',
                'director': 'directors',
                'cast': 'writers'  # Using cast as writers for simplicity
            })
            
            # Add placeholder columns for missing features
            for col in ['budget_tier', 'revenue_tier', 'runtime_category', 
                       'release_decade', 'popularity_category', 'rating_category']:
                if col not in movies_df.columns:
                    movies_df[col] = 'unknown'
            
            logger.info(f"Loaded {len(ratings_df)} ratings, {len(users_df)} users, {len(movies_df)} movies")
            return ratings_df, users_df, movies_df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    def create_user_item_matrix(self, ratings_df: pd.DataFrame) -> csr_matrix:
        """Create sparse user-item matrix for collaborative filtering"""
        # Create user and movie mappings
        unique_users = sorted(ratings_df['user_id'].unique())
        unique_movies = sorted(ratings_df['movie_id'].unique())
        
        user_to_idx = {user: idx for idx, user in enumerate(unique_users)}
        movie_to_idx = {movie: idx for idx, movie in enumerate(unique_movies)}
        
        # Create sparse matrix
        rows = [user_to_idx[user] for user in ratings_df['user_id']]
        cols = [movie_to_idx[movie] for movie in ratings_df['movie_id']]
        data = ratings_df['rating'].values
        
        matrix = csr_matrix((data, (rows, cols)), 
                          shape=(len(unique_users), len(unique_movies)))
        
        logger.info(f"Created user-item matrix: {matrix.shape}")
        return matrix
    
    def compute_user_similarity(self, matrix: csr_matrix) -> np.ndarray:
        """Compute user-user similarity matrix"""
        # Compute cosine similarity between users
        similarity = cosine_similarity(matrix)
        logger.info(f"Computed user similarity matrix: {similarity.shape}")
        return similarity
    
    def compute_item_similarity(self, matrix: csr_matrix) -> np.ndarray:
        """Compute item-item similarity matrix"""
        # Compute cosine similarity between items (transpose matrix)
        similarity = cosine_similarity(matrix.T)
        logger.info(f"Computed item similarity matrix: {similarity.shape}")
        return similarity
    
    def matrix_factorization_svd(self, matrix: csr_matrix, n_components: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Apply SVD for matrix factorization"""
        # Convert to dense for SVD (may need to handle memory for large matrices)
        dense_matrix = matrix.toarray()
        
        # Fill NaN values with mean rating
        user_means = np.nanmean(dense_matrix, axis=1, keepdims=True)
        dense_matrix = np.where(dense_matrix == 0, user_means, dense_matrix)
        
        # Apply SVD
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        user_features = svd.fit_transform(dense_matrix)
        item_features = svd.components_.T
        
        logger.info(f"SVD completed: user_features {user_features.shape}, item_features {item_features.shape}")
        return user_features, item_features
    
    def matrix_factorization_nmf(self, matrix: csr_matrix, n_components: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Apply NMF for matrix factorization"""
        # Convert to dense and ensure non-negative
        dense_matrix = matrix.toarray()
        dense_matrix = np.where(dense_matrix == 0, 1e-6, dense_matrix)  # Replace zeros with small positive values
        
        # Apply NMF
        nmf = NMF(n_components=n_components, random_state=42, max_iter=500)
        user_features = nmf.fit_transform(dense_matrix)
        item_features = nmf.components_.T
        
        logger.info(f"NMF completed: user_features {user_features.shape}, item_features {item_features.shape}")
        return user_features, item_features
    
    def train_models(self, n_components: int = 50):
        """Train all collaborative filtering models"""
        logger.info("Training collaborative filtering models...")
        
        # Load data
        ratings_df, users_df, movies_df = self.load_data()
        
        if ratings_df.empty:
            logger.error("No data loaded, cannot train models")
            return
        
        # Create user-item matrix
        self.user_item_matrix = self.create_user_item_matrix(ratings_df)
        
        # Compute similarity matrices
        self.user_similarity_matrix = self.compute_user_similarity(self.user_item_matrix)
        self.item_similarity_matrix = self.compute_item_similarity(self.user_item_matrix)
        
        # Train matrix factorization models
        self.user_features_svd, self.item_features_svd = self.matrix_factorization_svd(
            self.user_item_matrix, n_components
        )
        self.user_features_nmf, self.item_features_nmf = self.matrix_factorization_nmf(
            self.user_item_matrix, n_components
        )
        
        logger.info("Collaborative filtering models training completed!")
    
    def get_user_based_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using user-based collaborative filtering"""
        if self.user_similarity_matrix is None:
            logger.error("User similarity matrix not computed")
            return []
        
        # Find user index
        ratings_df = pd.read_sql_query("SELECT DISTINCT user_id FROM ratings", 
                                     sqlite3.connect(self.db_path))
        unique_users = sorted(ratings_df['user_id'].unique())
        user_to_idx = {user: idx for idx, user in enumerate(unique_users)}
        
        if user_id not in user_to_idx:
            logger.warning(f"User {user_id} not found")
            return []
        
        user_idx = user_to_idx[user_id]
        
        # Get user's ratings
        user_ratings = self.user_item_matrix[user_idx].toarray().flatten()
        unrated_items = np.where(user_ratings == 0)[0]
        
        if len(unrated_items) == 0:
            return []
        
        # Compute weighted average ratings from similar users
        similarities = self.user_similarity_matrix[user_idx]
        user_ratings_matrix = self.user_item_matrix.toarray()
        
        # Calculate predictions
        predictions = []
        for item_idx in unrated_items:
            # Get ratings for this item from all users
            item_ratings = user_ratings_matrix[:, item_idx]
            rated_users = np.where(item_ratings > 0)[0]
            
            if len(rated_users) == 0:
                continue
            
            # Compute weighted average
            weights = similarities[rated_users]
            ratings = item_ratings[rated_users]
            
            # Normalize weights
            if np.sum(weights) > 0:
                prediction = np.dot(weights, ratings) / np.sum(weights)
                predictions.append((item_idx, prediction))
        
        # Sort by prediction score
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Convert back to movie IDs
        movies_df = pd.read_sql_query("SELECT DISTINCT movie_id FROM ratings", 
                                    sqlite3.connect(self.db_path))
        unique_movies = sorted(movies_df['movie_id'].unique())
        
        recommendations = [(unique_movies[item_idx], score) 
                          for item_idx, score in predictions[:n_recommendations]]
        
        return recommendations
    
    def get_item_based_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using item-based collaborative filtering"""
        if self.item_similarity_matrix is None:
            logger.error("Item similarity matrix not computed")
            return []
        
        # Get user's ratings
        conn = sqlite3.connect(self.db_path)
        user_ratings_query = """
            SELECT movie_id, rating FROM ratings 
            WHERE user_id = ? AND rating IS NOT NULL
        """
        user_ratings_df = pd.read_sql_query(user_ratings_query, conn, params=(user_id,))
        conn.close()
        
        if user_ratings_df.empty:
            return []
        
        # Create movie to index mapping
        movies_df = pd.read_sql_query("SELECT DISTINCT movie_id FROM ratings", 
                                    sqlite3.connect(self.db_path))
        unique_movies = sorted(movies_df['movie_id'].unique())
        movie_to_idx = {movie: idx for idx, movie in enumerate(unique_movies)}
        
        # Get user's rated movies and ratings
        rated_movies = user_ratings_df['movie_id'].tolist()
        rated_ratings = user_ratings_df['rating'].tolist()
        
        # Find unrated movies
        unrated_movies = [m for m in unique_movies if m not in rated_movies]
        
        if not unrated_movies:
            return []
        
        # Calculate predictions
        predictions = []
        for movie_id in unrated_movies:
            movie_idx = movie_to_idx[movie_id]
            prediction = 0
            weight_sum = 0
            
            for rated_movie, rating in zip(rated_movies, rated_ratings):
                rated_movie_idx = movie_to_idx[rated_movie]
                similarity = self.item_similarity_matrix[movie_idx, rated_movie_idx]
                
                prediction += similarity * rating
                weight_sum += abs(similarity)
            
            if weight_sum > 0:
                prediction /= weight_sum
                predictions.append((movie_id, prediction))
        
        # Sort by prediction score
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n_recommendations]
    
    def get_matrix_factorization_recommendations(self, user_id: int, n_recommendations: int = 10, method: str = 'svd') -> List[Tuple[int, float]]:
        """Get recommendations using matrix factorization"""
        if method == 'svd':
            user_features = self.user_features_svd
            item_features = self.item_features_svd
        elif method == 'nmf':
            user_features = self.user_features_nmf
            item_features = self.item_features_nmf
        else:
            logger.error(f"Unknown method: {method}")
            return []
        
        if user_features is None or item_features is None:
            logger.error("Matrix factorization features not computed")
            return []
        
        # Get user index
        ratings_df = pd.read_sql_query("SELECT DISTINCT user_id FROM ratings", 
                                     sqlite3.connect(self.db_path))
        unique_users = sorted(ratings_df['user_id'].unique())
        user_to_idx = {user: idx for idx, user in enumerate(unique_users)}
        
        if user_id not in user_to_idx:
            logger.warning(f"User {user_id} not found")
            return []
        
        user_idx = user_to_idx[user_id]
        
        # Get user's feature vector
        user_vector = user_features[user_idx]
        
        # Calculate dot product with all item vectors
        scores = np.dot(item_features, user_vector)
        
        # Get unrated movies
        conn = sqlite3.connect(self.db_path)
        user_ratings_query = """
            SELECT movie_id FROM ratings 
            WHERE user_id = ? AND rating IS NOT NULL
        """
        user_rated_movies = pd.read_sql_query(user_ratings_query, conn, params=(user_id,))
        conn.close()
        
        rated_movie_ids = set(user_rated_movies['movie_id'].tolist())
        
        # Get all movie IDs
        movies_df = pd.read_sql_query("SELECT DISTINCT movie_id FROM ratings", 
                                    sqlite3.connect(self.db_path))
        all_movie_ids = sorted(movies_df['movie_id'].unique())
        
        # Filter out rated movies and create recommendations
        recommendations = []
        for i, movie_id in enumerate(all_movie_ids):
            if movie_id not in rated_movie_ids:
                recommendations.append((movie_id, scores[i]))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:n_recommendations]
    
    def get_hybrid_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get hybrid recommendations combining multiple methods"""
        # Get recommendations from different methods
        user_based = self.get_user_based_recommendations(user_id, n_recommendations * 2)
        item_based = self.get_item_based_recommendations(user_id, n_recommendations * 2)
        svd_based = self.get_matrix_factorization_recommendations(user_id, n_recommendations * 2, 'svd')
        nmf_based = self.get_matrix_factorization_recommendations(user_id, n_recommendations * 2, 'nmf')
        
        # Combine recommendations with weights
        weights = {
            'user_based': 0.2,
            'item_based': 0.2,
            'svd': 0.3,
            'nmf': 0.3
        }
        
        # Create score dictionary
        scores = {}
        
        for method_name, recs in [
            ('user_based', user_based),
            ('item_based', item_based), 
            ('svd', svd_based),
            ('nmf', nmf_based)
        ]:
            weight = weights[method_name]
            for movie_id, score in recs:
                if movie_id not in scores:
                    scores[movie_id] = 0
                scores[movie_id] += score * weight
        
        # Sort by combined score
        recommendations = [(movie_id, score) for movie_id, score in scores.items()]
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:n_recommendations]

def main():
    """Main function to demonstrate collaborative filtering"""
    cf = AdvancedCollaborativeFiltering()
    
    print("🤖 Training Advanced Collaborative Filtering Models...")
    cf.train_models(n_components=30)
    
    # Test with a sample user
    conn = sqlite3.connect(cf.db_path)
    user_query = "SELECT id FROM users WHERE is_active = 1 LIMIT 1"
    user_result = conn.execute(user_query).fetchone()
    conn.close()
    
    if user_result:
        user_id = user_result[0]
        print(f"🎯 Generating recommendations for user {user_id}...")
        
        # Get hybrid recommendations
        recommendations = cf.get_hybrid_recommendations(user_id, 10)
        
        print("📋 Top 10 Recommendations:")
        for i, (movie_id, score) in enumerate(recommendations, 1):
            print(f"  {i}. Movie ID: {movie_id}, Score: {score:.3f}")
    else:
        print("❌ No active users found for testing")

if __name__ == "__main__":
    main()
