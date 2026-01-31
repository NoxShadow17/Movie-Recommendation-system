from app.core.database import SessionLocal
from app.models import User, Movie, Rating
from app.services.ml_recommendations import ml_engine
from app.services.advanced_recommendations import MoodBasedRecommendation, TrendingAnalyzer, SocialRecommendationEngine
import random
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def get_movie_by_title(db, title):
    return db.query(Movie).filter(Movie.title.ilike(f"%{title}%")).first()

def ensure_social_connections(db, user_id):
    """Ensure user has friends and friends have ratings for demo purposes"""
    user = db.query(User).filter(User.id == user_id).first()
    
    # 1. Provide a friend if none exists
    if not user.friends:
        print("  > (Setup) connecting User to a Friend for demo...")
        friend = db.query(User).filter(User.id != user_id).first()
        if friend:
            user.friends.append(friend)
            db.commit()
    
    # 2. Ensure friend has ratings
    if user.friends:
        friend = user.friends[0]
        friend_ratings = db.query(Rating).filter(Rating.user_id == friend.id).count()
        if friend_ratings < 3:
             print(f"  > (Setup) seeding ratings for friend '{friend.username}'...")
             # Rate a popular movie high
             inception = get_movie_by_title(db, "Inception")
             if inception:
                db.add(Rating(user_id=friend.id, movie_id=inception.id, rating=5.0))
                db.commit()

def demo_system():
    db = SessionLocal()
    try:
        # 1. Setup - Use a demo user or User 1
        user_id = 1
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
             print("Error: User 1 not found. Please seed the database first.")
             return

        print_header(f"DEMO STARTED: User '{user.username}' (ID: {user.id})")
        
        # ---------------------------------------------------------
        # 2. Baseline Recommendations (AI/ML)
        # ---------------------------------------------------------
        print("\n[Step 1] Fetching Baseline Recommendations (Hybrid ML)...")
        recs_before = ml_engine.get_ml_recommendations(user_id, db, limit=3)
        for r in recs_before:
            movie = db.query(Movie).filter(Movie.id == r['movie_id']).first()
            print(f"  - {movie.title} ({r['score']:.1f}%) - Reason: {r['reason']}")
            
        # ---------------------------------------------------------
        # 3. Social Graph Recommendations
        # ---------------------------------------------------------
        print_header("SOCIAL GRAPH ANALYSIS")
        ensure_social_connections(db, user.id)
        
        social_recs = SocialRecommendationEngine.get_friend_recommendations(user_id, db, limit=3)
        if social_recs:
            print("  > Analyzing friend activity...")
            for r in social_recs:
                movie = db.query(Movie).filter(Movie.id == r['movie_id']).first()
                # Ensure score is formatted nicely
                score_val = r['score']
                print(f"  - {movie.title} (Score: {score_val:.2f}) - {r['reason']}")
        else:
             print("  > No specific friend recommendations found right now.")

        # ---------------------------------------------------------
        # 4. Simulate User Action: Rating a specific genre highly
        # ---------------------------------------------------------
        target_movie_title = "The Dark Knight"
        target_movie = get_movie_by_title(db, target_movie_title)
        
        if target_movie:
            print_header(f"ACTION: User rates '{target_movie.title}' -> 5 Stars")
            
            # Check if rating exists, if so update, else create
            existing_rating = db.query(Rating).filter(Rating.user_id==user_id, Rating.movie_id==target_movie.id).first()
            if existing_rating:
                existing_rating.rating = 5.0
            else:
                new_rating = Rating(user_id=user_id, movie_id=target_movie.id, rating=5.0)
                db.add(new_rating)
            db.commit()
            
            print("  > System detects new high rating...")
            print("  > Updating User Latent Vector (Real-time)...")
            ml_engine.is_trained = True # Force simulated re-calc
            
            # Fetch New Recommendations
            print("\n[Step 2] Fetching UPDATED Recommendations...")
            recs_after = ml_engine.get_ml_recommendations(user_id, db, limit=3)
            for r in recs_after:
                movie = db.query(Movie).filter(Movie.id == r['movie_id']).first()
                print(f"  - {movie.title} ({r['score']:.1f}%) - Reason: {r['reason']}")
                
        # ---------------------------------------------------------
        # 5. Mood Demonstration
        # ---------------------------------------------------------
        print_header("ACTION: User changes Mood to 'SCARED'")
        print("  > System applying 'Scared' filter (Horror/Thriller)...")
        print("  > Checking Director preferences...")
        
        mood_recs = MoodBasedRecommendation.get_mood_recommendations(user_id, "scared", db, limit=3)
        for r in mood_recs:
             # Need to fetch movie obj manually since service returns dict
             m = db.query(Movie).filter(Movie.id == r['movie_id']).first()
             match_score = r['score'] * 100
             print(f"  - {m.title} (Match: {match_score:.1f}%) - Reason: {r['reason']}")

        # ---------------------------------------------------------
        # 6. Trending Analysis
        # ---------------------------------------------------------
        print_header("GLOBAL TRENDING ANALYSIS")
        # Ensure trends exist
        TrendingAnalyzer.update_trending_scores(db) # Force update for demo
        
        trending = TrendingAnalyzer.get_trending_movies(db, limit=3)
        print("  > Identifying globally popular content...")
        for m in trending:
            print(f"  - #{m.trending_rank} {m.title} (Trend Score: {m.trending_score:.0f})")

    finally:
        db.close()

if __name__ == "__main__":
    demo_system()
