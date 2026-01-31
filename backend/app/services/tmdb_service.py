import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class TMDBService:
    """Service to interact with TMDB API for real-time data"""
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.cache_file = os.path.join(os.path.dirname(__file__), "..", "core", "tmdb_cache.json")
        if not self.api_key:
            print("Warning: TMDB_API_KEY not found in environment variables.")

    def _load_cache(self) -> Dict:
        """Load cached TMDB data from disk"""
        import json
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading TMDB cache: {e}")
        return {}

    def _save_cache(self, key: str, data: List[Dict]):
        """Save TMDB response to disk cache"""
        import json
        from datetime import datetime
        cache = self._load_cache()
        cache[key] = {
            "timestamp": datetime.now().isoformat(),
            "results": data
        }
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error saving TMDB cache: {e}")

    def get_trending_movies(self, time_window: str = 'week') -> List[Dict]:
        """Fetch trending movies from TMDB with last-known-good fallback"""
        if not self.api_key:
            return self._load_cache().get(f"trending_{time_window}", {}).get("results", [])
        
        url = f"{self.BASE_URL}/trending/movie/{time_window}"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=3.0)
            response.raise_for_status()
            results = response.json().get('results', [])
            if results:
                self._save_cache(f"trending_{time_window}", results)
            return results
        except Exception as e:
            print(f"Error fetching trending from TMDB: {e}. Falling back to cache.")
            return self._load_cache().get(f"trending_{time_window}", {}).get("results", [])

    def get_upcoming_movies(self, region: str = 'US') -> List[Dict]:
        """Fetch upcoming movies from TMDB with last-known-good fallback"""
        if not self.api_key:
            return self._load_cache().get("upcoming", {}).get("results", [])
            
        url = f"{self.BASE_URL}/movie/upcoming"
        params = {
            'api_key': self.api_key,
            'region': region,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=3.0)
            response.raise_for_status()
            results = response.json().get('results', [])
            if results:
                self._save_cache("upcoming", results)
            return results
        except Exception as e:
            print(f"Error fetching upcoming from TMDB: {e}. Falling back to cache.")
            return self._load_cache().get("upcoming", {}).get("results", [])

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Fetch full details for a specific movie from TMDB with caching.
        """
        cache_key = f"details_{tmdb_id}"
        
        # 1. Try Cache
        cached = self._load_cache().get(cache_key)
        if cached and cached.get("results"):
             return cached["results"]
             
        if not self.api_key:
            return None
            
        url = f"{self.BASE_URL}/movie/{tmdb_id}"
        params = {
            'api_key': self.api_key,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=3.0)
            response.raise_for_status()
            data = response.json()
            # 2. Save to Cache
            self._save_cache(cache_key, data)
            return data
        except Exception as e:
            print(f"Error fetching movie details from TMDB (ID: {tmdb_id}): {e}")
            # Fallback to cache if available even if potentially old (though unlikely with above check)
            if cached and cached.get("results"):
                 return cached["results"]
            return None

    def get_movie_credits(self, tmdb_id: int) -> List[Dict]:
        """
        Fetch cast and crew for a specific movie with caching.
        """
        cache_key = f"credits_{tmdb_id}"
        
        # 1. Try Cache
        cached = self._load_cache().get(cache_key)
        if cached and cached.get("results"):
             return cached["results"]

        if not self.api_key:
            return []
            
        url = f"{self.BASE_URL}/movie/{tmdb_id}/credits"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=3.0)
            response.raise_for_status()
            data = response.json().get('cast', [])
            # 2. Save to Cache
            self._save_cache(cache_key, data)
            return data
        except Exception as e:
            print(f"Error fetching credits from TMDB (ID: {tmdb_id}): {e}")
            if cached and cached.get("results"):
                 return cached["results"]
            return []
