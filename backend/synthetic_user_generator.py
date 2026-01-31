#!/usr/bin/env python3
"""
Synthetic User Data Generator
Creates diverse user profiles and movie ratings for training collaborative filtering models.
"""

import random
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyntheticUserGenerator:
    def __init__(self, db_path: str = "movie_recommendation.db"):
        self.db_path = db_path
        self.users = []
        self.user_profiles = {}
        self.genre_preferences = {}
        self.rating_patterns = {}
        
    def get_existing_movies(self) -> List[Dict]:
        """Get existing movies from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, genre, director, cast, 
                       runtime, popularity, avg_rating, release_date
                FROM movies
            """)
            
            movies = []
            for row in cursor.fetchall():
                movie = {
                    'id': row[0],
                    'title': row[1],
                    'genres': [g.strip() for g in (row[2] or '').split(',')] if row[2] else [],
                    'directors': [d.strip() for d in (row[3] or '').split(',')] if row[3] else [],
                    'writers': [],  # Not available in current schema
                    'cast': [c.strip() for c in (row[4] or '').split(',')] if row[4] else [],
                    'runtime': row[5] or 0,
                    'popularity': row[6] or 0,
                    'avg_rating': row[7] or 0,
                    'release_date': row[8] or '',
                    
                    # Derived features
                    'budget_tier': 'unknown',
                    'revenue_tier': 'unknown',
                    'runtime_category': 'unknown',
                    'release_decade': 'unknown',
                    'popularity_category': 'unknown',
                    'rating_category': 'unknown'
                }
                
                # Categorize runtime
                if movie['runtime'] > 0:
                    if movie['runtime'] < 90:
                        movie['runtime_category'] = 'short'
                    elif movie['runtime'] < 150:
                        movie['runtime_category'] = 'medium'
                    else:
                        movie['runtime_category'] = 'long'
                
                # Categorize release decade
                if movie['release_date']:
                    try:
                        year = int(movie['release_date'][:4])
                        decade = (year // 10) * 10
                        movie['release_decade'] = f"{decade}s"
                    except:
                        pass
                
                # Categorize popularity
                popularity = movie['popularity']
                if popularity < 5:
                    movie['popularity_category'] = 'low'
                elif popularity < 20:
                    movie['popularity_category'] = 'medium'
                else:
                    movie['popularity_category'] = 'high'
                
                # Categorize rating
                rating = movie['avg_rating']
                if rating < 5:
                    movie['rating_category'] = 'low'
                elif rating < 7:
                    movie['rating_category'] = 'medium'
                else:
                    movie['rating_category'] = 'high'
                
                movies.append(movie)
            
            conn.close()
            return movies
            
        except Exception as e:
            logger.error(f"Error fetching movies: {e}")
            return []
    
    def generate_user_profiles(self, num_users: int = 100) -> List[Dict]:
        """Generate diverse user profiles"""
        user_types = [
            {
                'name': 'BlockbusterFan',
                'description': 'Loves big-budget action and superhero movies',
                'genre_weights': {'Action': 0.9, 'Sci-Fi': 0.8, 'Adventure': 0.7, 'Comedy': 0.3},
                'decade_preference': ['2010s', '2020s'],
                'budget_preference': ['high'],
                'rating_pattern': 'generous',
                'activity_level': 'high'
            },
            {
                'name': 'IndieLover',
                'description': 'Prefers independent films and dramas',
                'genre_weights': {'Drama': 0.9, 'Romance': 0.7, 'Comedy': 0.6, 'Thriller': 0.4},
                'decade_preference': ['2000s', '2010s'],
                'budget_preference': ['low', 'medium'],
                'rating_pattern': 'harsh',
                'activity_level': 'medium'
            },
            {
                'name': 'ClassicEnthusiast',
                'description': 'Loves old movies and classics',
                'genre_weights': {'Drama': 0.8, 'Romance': 0.7, 'Comedy': 0.6, 'War': 0.5},
                'decade_preference': ['1960s', '1970s', '1980s', '1990s'],
                'budget_preference': ['medium'],
                'rating_pattern': 'moderate',
                'activity_level': 'medium'
            },
            {
                'name': 'GenreSpecialist',
                'description': 'Deeply passionate about specific genres',
                'genre_weights': {'Horror': 0.95, 'Mystery': 0.8, 'Thriller': 0.85},
                'decade_preference': ['2000s', '2010s', '2020s'],
                'budget_preference': ['medium', 'high'],
                'rating_pattern': 'generous',
                'activity_level': 'high'
            },
            {
                'name': 'CasualViewer',
                'description': 'Watches popular mainstream movies',
                'genre_weights': {'Comedy': 0.7, 'Action': 0.6, 'Romance': 0.6, 'Family': 0.8},
                'decade_preference': ['2010s', '2020s'],
                'budget_preference': ['high'],
                'rating_pattern': 'moderate',
                'activity_level': 'low'
            },
            {
                'name': 'FilmStudent',
                'description': 'Analyzes films critically, diverse tastes',
                'genre_weights': {g: 0.6 for g in ['Drama', 'Comedy', 'Action', 'Sci-Fi', 'Horror', 'Thriller']},
                'decade_preference': ['1970s', '1980s', '1990s', '2000s', '2010s'],
                'budget_preference': ['low', 'medium', 'high'],
                'rating_pattern': 'harsh',
                'activity_level': 'high'
            }
        ]
        
        users = []
        for i in range(num_users):
            user_type = random.choice(user_types)
            
            # Generate user profile
            user = {
                'id': i + 1,
                'username': f"user_{i+1:03d}",
                'email': f"user_{i+1:03d}@example.com",
                'full_name': f"User {i+1}",
                'user_type': user_type['name'],
                'description': user_type['description'],
                
                # Preferences
                'genre_weights': user_type['genre_weights'],
                'decade_preference': user_type['decade_preference'],
                'budget_preference': user_type['budget_preference'],
                'rating_pattern': user_type['rating_pattern'],
                'activity_level': user_type['activity_level'],
                
                # Behavioral traits
                'rating_bias': self._generate_rating_bias(user_type['rating_pattern']),
                'diversity_openness': random.uniform(0.3, 0.9),
                'novelty_seeking': random.uniform(0.2, 0.8),
                'social_influence': random.uniform(0.1, 0.7)
            }
            
            users.append(user)
        
        return users
    
    def _generate_rating_bias(self, pattern: str) -> float:
        """Generate rating bias based on pattern"""
        if pattern == 'generous':
            return random.uniform(0.5, 1.5)  # Add 0.5-1.5 to base rating
        elif pattern == 'harsh':
            return random.uniform(-1.5, -0.5)  # Subtract 0.5-1.5 from base rating
        else:  # moderate
            return random.uniform(-0.5, 0.5)  # Small bias
    
    def calculate_movie_score(self, user: Dict, movie: Dict) -> float:
        """Calculate how much a user would like a movie"""
        score = 5.0  # Base score
        
        # Genre preferences
        user_genres = user['genre_weights']
        movie_genres = movie['genres']
        
        genre_score = 0
        for genre in movie_genres:
            if genre in user_genres:
                genre_score += user_genres[genre]
        
        # Normalize genre score
        if movie_genres:
            genre_score /= len(movie_genres)
        else:
            genre_score = 0.3  # Default low score for unknown genres
        
        score += (genre_score - 0.5) * 3  # Scale to +/- 1.5
        
        # Decade preference
        if movie['release_decade'] in user['decade_preference']:
            score += 0.5
        else:
            score -= 0.3
        
        # Budget preference
        if movie['budget_tier'] in user['budget_preference']:
            score += 0.3
        
        # Quality indicators
        if movie['rating_category'] == 'high':
            score += 0.5
        elif movie['rating_category'] == 'low':
            score -= 0.5
        
        if movie['popularity_category'] == 'high':
            score += 0.3
        
        # Apply user bias
        score += user['rating_bias']
        
        # Add some randomness
        score += random.uniform(-0.5, 0.5)
        
        return max(1, min(10, score))  # Clamp to 1-10 range
    
    def generate_user_ratings(self, user: Dict, movies: List[Dict], target_ratings: int = 50) -> List[Dict]:
        """Generate ratings for a user"""
        ratings = []
        
        # Calculate scores for all movies
        movie_scores = []
        for movie in movies:
            score = self.calculate_movie_score(user, movie)
            movie_scores.append((movie['id'], score))
        
        # Sort by score descending
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Determine how many ratings to generate based on activity level
        activity_multiplier = {
            'low': 0.3,
            'medium': 0.6,
            'high': 1.0
        }
        
        actual_ratings = int(target_ratings * activity_multiplier[user['activity_level']])
        
        # Generate ratings
        for i, (movie_id, score) in enumerate(movie_scores[:actual_ratings]):
            # Add some randomness to the rating
            rating = max(1, min(10, score + random.uniform(-0.5, 0.5)))
            
            # Round to nearest 0.5
            rating = round(rating * 2) / 2
            
            # Sometimes users don't rate movies they don't like
            if rating < 3 and random.random() > 0.7:
                continue
            
            ratings.append({
                'user_id': user['id'],
                'movie_id': movie_id,
                'rating': rating,
                'created_at': self._random_date()
            })
        
        return ratings
    
    def _random_date(self) -> str:
        """Generate a random date in the last year"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_friend_connections(self, users: List[Dict], avg_friends: int = 10) -> List[Tuple[int, int]]:
        """Generate friend connections between users"""
        connections = []
        
        for user in users:
            # Users are more likely to be friends with similar users
            similar_users = []
            for other_user in users:
                if other_user['id'] != user['id']:
                    # Calculate similarity based on user type
                    similarity = 1.0 if user['user_type'] == other_user['user_type'] else 0.3
                    if random.random() < similarity * 0.3:  # 30% chance for similar, 9% for different
                        similar_users.append(other_user['id'])
            
            # Add random friends up to avg_friends
            num_friends = random.randint(1, min(avg_friends * 2, len(users) - 1))
            friends = random.sample(similar_users[:num_friends], min(num_friends, len(similar_users)))
            
            for friend_id in friends:
                if (user['id'], friend_id) not in connections and (friend_id, user['id']) not in connections:
                    connections.append((user['id'], friend_id))
        
        return connections
    
    def save_synthetic_data(self, users: List[Dict], all_ratings: List[Dict], connections: List[Tuple[int, int]]):
        """Save synthetic data to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert users
            for user in users:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (id, username, email, full_name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user['id'], user['username'], user['email'], user['full_name'],
                    True, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            # Insert ratings
            for rating in all_ratings:
                cursor.execute("""
                    INSERT OR REPLACE INTO ratings (user_id, movie_id, rating, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    rating['user_id'], rating['movie_id'], rating['rating'],
                    rating['created_at'], rating['created_at']
                ))
            
            # Insert friendships
            for user1_id, user2_id in connections:
                # Create friendship
                cursor.execute("""
                    INSERT OR REPLACE INTO friendships (user1_id, user2_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user1_id, user2_id, True, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(users)} users, {len(all_ratings)} ratings, and {len(connections)} friendships")
            
        except Exception as e:
            logger.error(f"Error saving synthetic data: {e}")
    
    def generate_complete_dataset(self, num_users: int = 200, target_ratings_per_user: int = 50):
        """Generate complete synthetic dataset"""
        print("🎭 Generating Synthetic User Data...")
        
        # Get existing movies
        print("🎬 Fetching existing movies...")
        movies = self.get_existing_movies()
        print(f"Found {len(movies)} movies in database")
        
        if not movies:
            print("❌ No movies found in database. Please run tmdb_loader.py first.")
            return
        
        # Generate user profiles
        print(f"👥 Generating {num_users} user profiles...")
        users = self.generate_user_profiles(num_users)
        
        # Generate ratings for all users
        print("⭐ Generating user ratings...")
        all_ratings = []
        for i, user in enumerate(users):
            if i % 20 == 0:
                print(f"  Processed {i}/{num_users} users...")
            
            user_ratings = self.generate_user_ratings(user, movies, target_ratings_per_user)
            all_ratings.extend(user_ratings)
        
        # Generate friend connections
        print("🤝 Generating friend connections...")
        connections = self.generate_friend_connections(users)
        
        # Save to database
        print("💾 Saving synthetic data to database...")
        self.save_synthetic_data(users, all_ratings, connections)
        
        print("✅ Synthetic dataset generation complete!")
        print(f"📊 Generated: {len(users)} users, {len(all_ratings)} ratings, {len(connections)} friendships")

def main():
    """Main function to generate synthetic data"""
    generator = SyntheticUserGenerator()
    generator.generate_complete_dataset(num_users=300, target_ratings_per_user=40)

if __name__ == "__main__":
    main()
