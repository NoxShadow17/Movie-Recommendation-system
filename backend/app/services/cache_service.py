from functools import lru_cache
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, List
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class CacheManager:
    """Advanced caching layer for frequently accessed, slowly changing data"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_times: Dict[str, datetime] = {}
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a cache key based on function name and arguments"""
        # Create a string representation of all arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to JSON string and hash it for a consistent key
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_or_compute(self, func: Callable, *args, ttl: Optional[int] = None, **kwargs) -> Any:
        """
        Get cached value or compute and cache it
        
        Args:
            func: The function to compute the value
            *args: Arguments for the function and cache key
            ttl: Time to live in seconds (optional, uses default if not provided)
            **kwargs: Keyword arguments for the function and cache key
        """
        cache_key = self._generate_key(func.__name__, *args, **kwargs)
        current_ttl = ttl or self.default_ttl
        
        # Check if we have a valid cached value
        if cache_key in self._cache:
            cache_time = self._cache_times.get(cache_key, datetime.min)
            if datetime.now() - cache_time < timedelta(seconds=current_ttl):
                logger.debug(f"Cache hit for {func.__name__}")
                return self._cache[cache_key]
        
        # Compute the value
        try:
            logger.debug(f"Cache miss for {func.__name__}, computing...")
            value = func(*args, **kwargs)
            
            # Cache the result
            self._cache[cache_key] = value
            self._cache_times[cache_key] = datetime.now()
            
            logger.debug(f"Cached result for {func.__name__} with key {cache_key}")
            return value
            
        except Exception as e:
            logger.error(f"Error computing cache value for {func.__name__}: {e}")
            raise
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern"""
        import re
        pattern_regex = re.compile(pattern)
        
        keys_to_remove = [key for key in self._cache.keys() if pattern_regex.search(key)]
        
        for key in keys_to_remove:
            del self._cache[key]
            del self._cache_times[key]
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
        return len(keys_to_remove)
    
    def clear(self) -> int:
        """Clear all cached values"""
        count = len(self._cache)
        self._cache.clear()
        self._cache_times.clear()
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for key, cache_time in self._cache_times.items():
            if now - cache_time < timedelta(seconds=self.default_ttl):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'default_ttl': self.default_ttl
        }


# Global cache instance
cache_manager = CacheManager(default_ttl=300)  # 5 minutes


# Decorator for easy caching
def cached(ttl: Optional[int] = None):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=600)  # Cache for 10 minutes
        def expensive_function(user_id: int):
            # ... expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return cache_manager.get_or_compute(func, *args, ttl=ttl, **kwargs)
        return wrapper
    return decorator


# Specific cache functions for common operations
class RecommendationCache:
    """Specialized caching for recommendation operations"""
    
    @staticmethod
    @cached(ttl=600)  # 10 minutes for user preferences
    def get_user_preferences(user_id: int, db) -> Dict:
        """Cache user preferences to avoid repeated database queries"""
        from app.services.recommendation_engine import ContentBasedFiltering
        return ContentBasedFiltering.get_user_preferences(user_id, db)
    
    @staticmethod
    @cached(ttl=300)  # 5 minutes for genre calculations
    def get_enhanced_content_scores(user_id: int, db, user_preferences: Dict) -> Dict:
        """Cache enhanced content scores"""
        from app.services.recommendation_engine import HybridRecommendationEngine
        return HybridRecommendationEngine._get_enhanced_content_scores(user_id, db, user_preferences)
    
    @staticmethod
    @cached(ttl=1800)  # 30 minutes for popular movies
    def get_popular_movies(db, limit: int = 20) -> List:
        """Cache popular movies list"""
        from app.models import Movie
        return db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()
    
    @staticmethod
    @cached(ttl=900)  # 15 minutes for trending
    def get_trending_cache(db, period: str = 'weekly') -> List:
        """Cache trending movies"""
        from app.services.advanced_recommendations import TrendingAnalyzer
        return TrendingAnalyzer.get_trending_movies(db, period=period, limit=20)
    
    @staticmethod
    @cached(ttl=3600)  # 1 hour for user mood history
    def get_user_mood_history(user_id: int, db) -> Dict:
        """Cache user mood history"""
        from app.services.advanced_recommendations import MoodBasedRecommendation
        return MoodBasedRecommendation._get_user_mood_history(user_id, db)


# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for invalidating specific cache patterns"""
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a specific user"""
        pattern = f".*{user_id}.*"
        return cache_manager.invalidate_pattern(pattern)
    
    @staticmethod
    def invalidate_recommendation_cache():
        """Invalidate all recommendation-related cache"""
        patterns = [
            "get_user_preferences",
            "get_enhanced_content_scores", 
            "get_user_mood_history"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += cache_manager.invalidate_pattern(pattern)
        
        return total_invalidated
    
    @staticmethod
    def invalidate_movie_cache():
        """Invalidate all movie-related cache"""
        patterns = [
            "get_popular_movies",
            "get_trending_cache"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += cache_manager.invalidate_pattern(pattern)
        
        return total_invalidated


# Cache warming functions
class CacheWarmer:
    """Pre-populate cache with commonly accessed data"""
    
    @staticmethod
    def warm_user_preferences(db, user_ids: List[int]):
        """Pre-cache user preferences for active users"""
        for user_id in user_ids:
            try:
                RecommendationCache.get_user_preferences(user_id, db)
            except Exception as e:
                logger.warning(f"Failed to warm cache for user {user_id}: {e}")
    
    @staticmethod
    def warm_popular_movies(db):
        """Pre-cache popular movies"""
        try:
            RecommendationCache.get_popular_movies(db)
        except Exception as e:
            logger.warning(f"Failed to warm popular movies cache: {e}")
    
    @staticmethod
    def warm_trending_movies(db):
        """Pre-cache trending movies"""
        try:
            RecommendationCache.get_trending_cache(db, 'weekly')
            RecommendationCache.get_trending_cache(db, 'daily')
        except Exception as e:
            logger.warning(f"Failed to warm trending movies cache: {e}")