"""
Synthetic User Data Generator
Creates realistic users and ratings for collaborative filtering model training
"""

import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models import User, Movie, Rating, MoodEnum
from app.core.security import get_password_hash

# User persona templates with genre preferences
USER_PERSONAS = [
    {
        "name": "Action Lover",
        "preferred_genres": ["Action", "Adventure", "Thriller"],
        "disliked_genres": ["Romance", "Drama"],
        "rating_bias": 0.5,  # Tends to rate higher
        "rating_count_range": (80, 150)
    },
    {
        "name": "Drama Enthusiast",
        "preferred_genres": ["Drama", "Romance", "Biography"],
        "disliked_genres": ["Horror", "Action"],
        "rating_bias": 0.0,
        "rating_count_range": (100, 200)
    },
    {
        "name": "Comedy Fan",
        "preferred_genres": ["Comedy", "Animation", "Family"],
        "disliked_genres": ["Horror", "Thriller"],
        "rating_bias": 0.3,
        "rating_count_range": (60, 120)
    },
    {
        "name": "Horror Buff",
        "preferred_genres": ["Horror", "Thriller", "Mystery"],
        "disliked_genres": ["Comedy", "Romance"],
        "rating_bias": -0.2,  # More critical
        "rating_count_range": (70, 130)
    },
    {
        "name": "Sci-Fi Geek",
        "preferred_genres": ["Science Fiction", "Fantasy", "Adventure"],
        "disliked_genres": ["Romance", "Drama"],
        "rating_bias": 0.4,
        "rating_count_range": (90, 160)
    },
    {
        "name": "Indie Critic",
        "preferred_genres": ["Drama", "Documentary", "Foreign"],
        "disliked_genres": ["Action", "Animation"],
        "rating_bias": -0.5,  # Very critical
        "rating_count_range": (120, 200)
    },
    {
        "name": "Family Viewer",
        "preferred_genres": ["Family", "Animation", "Comedy"],
        "disliked_genres": ["Horror", "Thriller"],
        "rating_bias": 0.6,
        "rating_count_range": (50, 100)
    },
    {
        "name": "Blockbuster Chaser",
        "preferred_genres": ["Action", "Science Fiction", "Adventure"],
        "disliked_genres": ["Documentary", "Drama"],
        "rating_bias": 0.3,
        "rating_count_range": (70, 140)
    },
    {
        "name": "Romance Reader",
        "preferred_genres": ["Romance", "Drama", "Comedy"],
        "disliked_genres": ["Horror", "Action"],
        "rating_bias": 0.4,
        "rating_count_range": (80, 150)
    },
    {
        "name": "Classic Film Buff",
        "preferred_genres": ["Drama", "Film-Noir", "Western"],
        "disliked_genres": ["Science Fiction", "Animation"],
        "rating_bias": -0.3,
        "rating_count_range": (100, 180)
    }
]

class SyntheticUserGenerator:
    """Generate realistic synthetic users and ratings"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.movies = []
        self.genre_to_movies = {}
        
    def load_movies(self):
        """Load all movies and organize by genre"""
        print("Loading movies from database...")
        self.movies = self.db.query(Movie).filter(Movie.tmdb_id.isnot(None)).all()
        print(f"  Loaded {len(self.movies):,} movies")
        
        # Organize movies by genre
        for movie in self.movies:
            if movie.genre:
                genres = [g.strip() for g in movie.genre.split(',')]
                for genre in genres:
                    if genre not in self.genre_to_movies:
                        self.genre_to_movies[genre] = []
                    self.genre_to_movies[genre].append(movie)
        
        print(f"  Found {len(self.genre_to_movies)} unique genres")
    
    def calculate_movie_score(self, movie: Movie, persona: dict) -> float:
        """
        Calculate how much a user persona would like a movie
        Returns score 0-1 (higher = more likely to watch and rate highly)
        """
        score = 0.5  # Base score
        
        if not movie.genre:
            return score
        
        movie_genres = [g.strip() for g in movie.genre.split(',')]
        
        # Preferred genres boost
        for genre in movie_genres:
            if genre in persona['preferred_genres']:
                score += 0.3
        
        # Disliked genres penalty
        for genre in movie_genres:
            if genre in persona['disliked_genres']:
                score -= 0.4
        
        # Quality factor (TMDB rating)
        if movie.vote_average:
            quality_factor = (movie.vote_average - 5) / 10  # -0.5 to 0.5
            score += quality_factor * 0.3
        
        # Popularity factor (more popular = more likely to watch)
        if movie.tmdb_popularity:
            popularity_factor = min(movie.tmdb_popularity / 100, 1.0)
            score += popularity_factor * 0.2
        
        # Recency factor (newer movies slightly preferred)
        if movie.release_year:
            if movie.release_year >= 2015:
                score += 0.1
            elif movie.release_year >= 2000:
                score += 0.05
        
        return max(0, min(1, score))  # Clamp to 0-1
    
    def generate_rating(self, movie: Movie, persona: dict, watch_probability: float) -> float:
        """
        Generate a realistic rating for a movie based on persona and movie quality
        """
        # Base rating from TMDB (if available)
        if movie.vote_average:
            base_rating = movie.vote_average / 2  # Convert 0-10 to 0-5
        else:
            base_rating = 3.0  # Default middle rating
        
        # Apply persona bias
        rating = base_rating + persona['rating_bias']
        
        # Add some randomness
        rating += np.random.normal(0, 0.5)
        
        # Adjust based on watch probability (higher probability = better match = higher rating)
        rating += (watch_probability - 0.5) * 1.0
        
        # Clamp to 1-5 range
        rating = max(1.0, min(5.0, rating))
        
        # Round to nearest 0.5
        rating = round(rating * 2) / 2
        
        return rating
    
    def select_mood(self, rating: float, movie_genres: list) -> str:
        """Select appropriate mood based on rating and genres"""
        moods = {
            "HAPPY": ["Comedy", "Animation", "Family", "Musical"],
            "SAD": ["Drama", "Romance"],
            "EXCITED": ["Action", "Adventure", "Thriller"],
            "RELAXED": ["Comedy", "Drama", "Documentary"],
            "THOUGHTFUL": ["Drama", "Documentary", "Science Fiction"],
            "SCARED": ["Horror", "Thriller"]
        }
        
        # Find matching moods based on genres
        matching_moods = []
        for mood, mood_genres in moods.items():
            if any(g in mood_genres for g in movie_genres):
                matching_moods.append(mood)
        
        if matching_moods:
            return random.choice(matching_moods)
        
        # Default mood based on rating
        if rating >= 4.0:
            return random.choice(["HAPPY", "EXCITED"])
        elif rating <= 2.5:
            return random.choice(["SAD", "THOUGHTFUL"])
        else:
            return random.choice(["RELAXED", "THOUGHTFUL"])
    
    def create_user(self, persona: dict, user_index: int) -> User:
        """Create a synthetic user based on persona"""
        username = f"synthetic_user_{user_index:04d}"
        email = f"synthetic_{user_index:04d}@example.com"
        
        # Check if user already exists
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            return existing
        
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash("synthetic123"),
            full_name=f"{persona['name']} {user_index}",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def generate_ratings_for_user(self, user: User, persona: dict):
        """Generate realistic ratings for a user based on their persona"""
        # Determine how many movies to rate
        min_ratings, max_ratings = persona['rating_count_range']
        num_ratings = random.randint(min_ratings, max_ratings)
        
        # Calculate watch probability for all movies
        movie_scores = []
        for movie in self.movies:
            score = self.calculate_movie_score(movie, persona)
            movie_scores.append((movie, score))
        
        # Sort by score and select top candidates
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select movies with weighted random selection (higher scores more likely)
        selected_movies = []
        
        # Top 30% - very likely to watch
        top_30_count = int(num_ratings * 0.5)
        top_30_movies = [m for m, s in movie_scores[:int(len(movie_scores) * 0.3)]]
        selected_movies.extend(random.sample(top_30_movies, min(top_30_count, len(top_30_movies))))
        
        # Middle 40% - moderately likely
        middle_40_count = int(num_ratings * 0.3)
        middle_40_movies = [m for m, s in movie_scores[int(len(movie_scores) * 0.3):int(len(movie_scores) * 0.7)]]
        if middle_40_movies:
            selected_movies.extend(random.sample(middle_40_movies, min(middle_40_count, len(middle_40_movies))))
        
        # Bottom 30% - occasionally watch (for diversity)
        bottom_30_count = num_ratings - len(selected_movies)
        bottom_30_movies = [m for m, s in movie_scores[int(len(movie_scores) * 0.7):]]
        if bottom_30_movies and bottom_30_count > 0:
            selected_movies.extend(random.sample(bottom_30_movies, min(bottom_30_count, len(bottom_30_movies))))
        
        # Generate ratings
        ratings_created = 0
        for movie in selected_movies[:num_ratings]:
            # Check if rating already exists
            existing_rating = self.db.query(Rating).filter(
                Rating.user_id == user.id,
                Rating.movie_id == movie.id
            ).first()
            
            if existing_rating:
                continue
            
            # Calculate watch probability for this movie
            watch_prob = self.calculate_movie_score(movie, persona)
            
            # Generate rating
            rating_value = self.generate_rating(movie, persona, watch_prob)
            
            # Select mood
            movie_genres = [g.strip() for g in movie.genre.split(',')] if movie.genre else []
            mood = self.select_mood(rating_value, movie_genres)
            
            # Create rating with timestamp spread over past year
            days_ago = random.randint(1, 365)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            rating = Rating(
                user_id=user.id,
                movie_id=movie.id,
                rating=rating_value,
                mood=MoodEnum[mood],
                created_at=created_at,
                updated_at=created_at
            )
            
            self.db.add(rating)
            ratings_created += 1
        
        self.db.commit()
        return ratings_created
    
    def generate_users(self, num_users: int = 500):
        """Generate synthetic users with ratings"""
        print(f"\nGenerating {num_users} synthetic users...")
        print("=" * 70)
        
        self.load_movies()
        
        total_ratings = 0
        
        for i in range(num_users):
            # Select random persona
            persona = random.choice(USER_PERSONAS)
            
            # Create user
            user = self.create_user(persona, i + 1)
            
            # Generate ratings
            num_ratings = self.generate_ratings_for_user(user, persona)
            total_ratings += num_ratings
            
            if (i + 1) % 50 == 0:
                print(f"  [{i + 1}/{num_users}] Created users with {total_ratings:,} ratings")
        
        print("\n" + "=" * 70)
        print("Synthetic Data Generation Complete!")
        print("=" * 70)
        print(f"  Users created:    {num_users:,}")
        print(f"  Ratings created:  {total_ratings:,}")
        print(f"  Avg ratings/user: {total_ratings/num_users:.1f}")
        print("=" * 70)
    
    def close(self):
        """Close database connection"""
        self.db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic users and ratings')
    parser.add_argument('--users', type=int, default=500, 
                       help='Number of synthetic users to create (default: 500)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate generated data')
    
    args = parser.parse_args()
    
    generator = SyntheticUserGenerator()
    
    try:
        if args.validate:
            # Validate existing data
            db = SessionLocal()
            total_users = db.query(User).count()
            total_ratings = db.query(Rating).count()
            synthetic_users = db.query(User).filter(User.username.like('synthetic_user_%')).count()
            
            print("\n" + "=" * 70)
            print("SYNTHETIC DATA VALIDATION")
            print("=" * 70)
            print(f"  Total users:      {total_users:,}")
            print(f"  Synthetic users:  {synthetic_users:,}")
            print(f"  Total ratings:    {total_ratings:,}")
            
            if synthetic_users > 0:
                avg_ratings = total_ratings / total_users
                print(f"  Avg ratings/user: {avg_ratings:.1f}")
            
            # Rating distribution
            rating_dist = db.query(Rating.rating, func.count(Rating.id)).group_by(Rating.rating).all()
            print("\n  Rating Distribution:")
            for rating, count in sorted(rating_dist):
                print(f"    {rating:.1f} stars: {count:,} ({count/total_ratings*100:.1f}%)")
            
            db.close()
        else:
            # Generate users
            generator.generate_users(num_users=args.users)
            
            print("\nNext steps:")
            print("1. Validate data: python generate_synthetic_users.py --validate")
            print("2. Train collaborative filtering model")
            print("3. Test recommendations with synthetic users")
    
    finally:
        generator.close()
