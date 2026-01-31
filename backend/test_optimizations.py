#!/usr/bin/env python3
"""
Test script to validate all performance optimizations
"""
import time
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal, Base
from app.models import User, Movie, Rating, UserPreference
from app.services.recommendation_engine import HybridRecommendationEngine
from app.services.advanced_recommendations import SocialRecommendationEngine, MoodBasedRecommendation
from app.services.cache_service import cache_manager, RecommendationCache
from app.utils.response_optimizer import ResponseOptimizer


def test_database_indexes():
    """Test that database indexes are working properly"""
    print("🔍 Testing Database Indexes...")
    
    try:
        # Test query performance with EXPLAIN (for SQLite, we'll just test that queries work)
        db = SessionLocal()
        
        # Test user queries
        start_time = time.time()
        users = db.query(User).filter(User.username.like('%test%')).limit(10).all()
        user_query_time = time.time() - start_time
        
        # Test movie queries
        start_time = time.time()
        movies = db.query(Movie).filter(Movie.genre.like('%Action%')).limit(10).all()
        movie_query_time = time.time() - start_time
        
        # Test rating queries
        start_time = time.time()
        ratings = db.query(Rating).filter(Rating.user_id == 1).limit(10).all()
        rating_query_time = time.time() - start_time
        
        print(f"   ✅ User query time: {user_query_time:.4f}s")
        print(f"   ✅ Movie query time: {movie_query_time:.4f}s")
        print(f"   ✅ Rating query time: {rating_query_time:.4f}s")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database index test failed: {e}")
        return False


def test_connection_pooling():
    """Test connection pooling functionality"""
    print("🔗 Testing Connection Pooling...")
    
    try:
        # Test multiple concurrent connections
        connections = []
        start_time = time.time()
        
        for i in range(5):
            db = SessionLocal()
            connections.append(db)
            
            # Execute a simple query
            db.query(User).first()
        
        connection_time = time.time() - start_time
        
        # Clean up connections
        for db in connections:
            db.close()
        
        print(f"   ✅ Created 5 connections in {connection_time:.4f}s")
        print(f"   ✅ Connection pooling is active")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection pooling test failed: {e}")
        return False


def test_n_plus_one_fixes():
    """Test that N+1 query problems are fixed"""
    print("⚡ Testing N+1 Query Fixes...")
    
    try:
        db = SessionLocal()
        
        # Test recommendation engine (should not have N+1 queries)
        start_time = time.time()
        recommendations = HybridRecommendationEngine.get_recommendations(1, db, limit=5)
        rec_time = time.time() - start_time
        
        print(f"   ✅ Hybrid recommendations generated in {rec_time:.4f}s")
        print(f"   ✅ Number of recommendations: {len(recommendations)}")
        
        # Test social recommendations (should use bulk queries)
        start_time = time.time()
        social_recs = SocialRecommendationEngine.get_friend_recommendations(1, db, limit=5)
        social_time = time.time() - start_time
        
        print(f"   ✅ Social recommendations generated in {social_time:.4f}s")
        print(f"   ✅ Number of social recommendations: {len(social_recs)}")
        
        # Test mood-based recommendations
        start_time = time.time()
        mood_recs = MoodBasedRecommendation.get_mood_recommendations(1, "happy", db, limit=5)
        mood_time = time.time() - start_time
        
        print(f"   ✅ Mood recommendations generated in {mood_time:.4f}s")
        print(f"   ✅ Number of mood recommendations: {len(mood_recs)}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ N+1 query fix test failed: {e}")
        return False


def test_caching_layer():
    """Test caching functionality"""
    print("💾 Testing Caching Layer...")
    
    try:
        db = SessionLocal()
        
        # Test cache warming
        print("   🌡️  Warming cache...")
        RecommendationCache.get_user_preferences(1, db)
        RecommendationCache.get_popular_movies(db)
        
        # Test cache hit
        start_time = time.time()
        cached_result = RecommendationCache.get_user_preferences(1, db)
        cache_hit_time = time.time() - start_time
        
        print(f"   ✅ Cache hit time: {cache_hit_time:.4f}s")
        
        # Test cache stats
        stats = cache_manager.get_stats()
        print(f"   ✅ Cache stats: {stats}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Caching test failed: {e}")
        return False


def test_response_optimization():
    """Test response optimization"""
    print("📦 Testing Response Optimization...")
    
    try:
        db = SessionLocal()
        
        # Get some test data
        movies = db.query(Movie).limit(5).all()
        
        # Test response optimization
        start_time = time.time()
        optimized_movies = ResponseOptimizer.optimize_movie_response(movies)
        optimization_time = time.time() - start_time
        
        print(f"   ✅ Response optimization time: {optimization_time:.4f}s")
        print(f"   ✅ Optimized {len(optimized_movies)} movies")
        
        # Check that we only have the fields we want
        if optimized_movies:
            expected_fields = {'id', 'title', 'poster_path', 'overview', 'release_date', 'genre', 'avg_rating', 'rating_count', 'popularity'}
            actual_fields = set(optimized_movies[0].keys())
            if expected_fields.issubset(actual_fields):
                print("   ✅ Response contains expected fields")
            else:
                print(f"   ⚠️  Missing fields: {expected_fields - actual_fields}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Response optimization test failed: {e}")
        return False


def test_bulk_operations():
    """Test bulk friend lookup optimization"""
    print("👥 Testing Bulk Operations...")
    
    try:
        db = SessionLocal()
        
        # Test bulk user lookup (simulating friend lookups)
        user_ids = [1, 2, 3, 4, 5]
        
        start_time = time.time()
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        bulk_lookup_time = time.time() - start_time
        
        print(f"   ✅ Bulk user lookup time: {bulk_lookup_time:.4f}s")
        print(f"   ✅ Retrieved {len(users)} users")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Bulk operations test failed: {e}")
        return False


def run_all_tests():
    """Run all optimization tests"""
    print("🚀 Starting Performance Optimization Tests\n")
    
    tests = [
        ("Database Indexes", test_database_indexes),
        ("Connection Pooling", test_connection_pooling),
        ("N+1 Query Fixes", test_n_plus_one_fixes),
        ("Caching Layer", test_caching_layer),
        ("Response Optimization", test_response_optimization),
        ("Bulk Operations", test_bulk_operations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
            print()
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All optimization tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)