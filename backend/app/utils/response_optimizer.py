from typing import Dict, Any, List, Optional
from fastapi.responses import JSONResponse
import json
import logging

logger = logging.getLogger(__name__)


class ResponseOptimizer:
    """Optimize API responses for better performance and smaller payloads"""
    
    @staticmethod
    def optimize_movie_response(movies: List, include_fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Optimize movie response by including only necessary fields
        
        Args:
            movies: List of movie objects
            include_fields: List of fields to include. If None, uses default optimized set
        """
        if not include_fields:
            # Default optimized field set
            include_fields = [
                'id', 'title', 'poster_path', 'overview', 'release_date',
                'genre', 'avg_rating', 'rating_count', 'popularity'
            ]
        
        optimized_movies = []
        for movie in movies:
            if hasattr(movie, '__dict__'):
                # Convert SQLAlchemy object to dict
                movie_dict = {field: getattr(movie, field, None) for field in include_fields}
            else:
                # Already a dict
                movie_dict = {field: movie.get(field) for field in include_fields}
            
            optimized_movies.append(movie_dict)
        
        return optimized_movies
    
    @staticmethod
    def optimize_recommendation_response(recommendations: List[Dict]) -> List[Dict]:
        """Optimize recommendation response by removing unnecessary fields"""
        optimized_recommendations = []
        
        for rec in recommendations:
            optimized_rec = {
                'movie_id': rec.get('movie_id'),
                'score': rec.get('score'),
                'reason': rec.get('reason'),
                'algorithm': rec.get('algorithm')
            }
            
            # Include movie data if present, but optimized
            if 'movie' in rec and rec['movie']:
                movie = rec['movie']
                optimized_rec['movie'] = {
                    'id': movie.id,
                    'title': movie.title,
                    'poster_path': movie.poster_path,
                    'overview': movie.overview[:200] + '...' if movie.overview and len(movie.overview) > 200 else movie.overview,
                    'genre': movie.genre,
                    'avg_rating': movie.avg_rating,
                    'popularity': movie.popularity
                }
            
            optimized_recommendations.append(optimized_rec)
        
        return optimized_recommendations
    
    @staticmethod
    def optimize_user_response(users: List, include_fields: Optional[List[str]] = None) -> List[Dict]:
        """Optimize user response by including only necessary fields"""
        if not include_fields:
            include_fields = ['id', 'username', 'profile_picture', 'full_name']
        
        optimized_users = []
        for user in users:
            if hasattr(user, '__dict__'):
                user_dict = {field: getattr(user, field, None) for field in include_fields}
            else:
                user_dict = {field: user.get(field) for field in include_fields}
            
            optimized_users.append(user_dict)
        
        return optimized_users
    
    @staticmethod
    def create_optimized_response(data: Any, status_code: int = 200, 
                                compression_enabled: bool = True) -> JSONResponse:
        """Create an optimized JSON response with proper headers"""
        response = JSONResponse(
            content=data,
            status_code=status_code
        )
        
        # Add performance headers
        response.headers["X-Response-Optimized"] = "true"
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        if compression_enabled:
            response.headers["Content-Encoding"] = "gzip"
        
        return response


# Utility functions for common response patterns
def create_paginated_response(data: List, total: int, page: int, limit: int, 
                            optimize_func: callable = None) -> Dict:
    """Create a standardized paginated response"""
    if optimize_func:
        data = optimize_func(data)
    
    return {
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "has_next": page * limit < total,
            "has_prev": page > 1
        }
    }


def create_success_response(data: Any = None, message: str = "Success", 
                          optimize_func: callable = None) -> Dict:
    """Create a standardized success response"""
    response_data = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        if optimize_func:
            data = optimize_func(data)
        response_data["data"] = data
    
    return response_data


def create_error_response(message: str, error_code: str = None, 
                         status_code: int = 400) -> Dict:
    """Create a standardized error response"""
    response_data = {
        "success": False,
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code
        }
    }
    
    return response_data


# Middleware for automatic response optimization
class ResponseOptimizationMiddleware:
    """Middleware to automatically optimize responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Process the request
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add optimization headers
                headers = dict(message.get("headers", []))
                headers[b"X-Response-Optimized"] = b"true"
                headers[b"X-Content-Type-Options"] = b"nosniff"
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)