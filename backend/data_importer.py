"""
Data Importer for TMDB Movie Data
Imports fetched TMDB data into the database with validation and duplicate handling
"""

import json
import sys
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Add parent directory to path
sys.path.append('.')

from app.core.database import SessionLocal, engine, Base
from app.models import Movie
from tmdb_data_fetcher import TMDBFetcher, transform_movie_data, load_movie_ids_from_file


class MovieImporter:
    """Import TMDB movie data into database"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.fetcher = TMDBFetcher()
        self.stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def import_movie(self, movie_data: Dict) -> bool:
        """
        Import a single movie into database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            tmdb_id = movie_data.get('tmdb_id')
            if not tmdb_id:
                print("  ✗ No TMDB ID found")
                self.stats['errors'] += 1
                return False
            
            # Check if movie already exists
            existing_movie = self.db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
            
            if existing_movie:
                # Update existing movie with new data
                for key, value in movie_data.items():
                    if hasattr(existing_movie, key):
                        setattr(existing_movie, key, value)
                
                self.db.commit()
                print(f"  ✓ Updated: {movie_data.get('title')}")
                self.stats['updated'] += 1
                return True
            else:
                # Create new movie
                movie = Movie(**movie_data)
                self.db.add(movie)
                self.db.commit()
                print(f"  ✓ Imported: {movie_data.get('title')}")
                self.stats['imported'] += 1
                return True
                
        except IntegrityError as e:
            self.db.rollback()
            print(f"  ✗ Integrity error: {e}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self.db.rollback()
            print(f"  ✗ Error: {e}")
            self.stats['errors'] += 1
            return False
    
    def import_from_tmdb_ids(self, movie_ids: List[int], batch_size: int = 100):
        """
        Import movies from a list of TMDB IDs
        
        Args:
            movie_ids: List of TMDB movie IDs
            batch_size: Number of movies to process before showing progress
        """
        self.stats['total'] = len(movie_ids)
        
        print(f"\nImporting {len(movie_ids)} movies from TMDB...")
        print("=" * 60)
        
        for i, movie_id in enumerate(movie_ids, 1):
            print(f"\n[{i}/{len(movie_ids)}] Fetching movie ID: {movie_id}")
            
            # Fetch complete movie data from TMDB
            tmdb_data = self.fetcher.get_complete_movie_data(movie_id)
            
            if not tmdb_data:
                print(f"  ✗ Failed to fetch data")
                self.stats['skipped'] += 1
                continue
            
            # Transform to database format
            try:
                movie_data = transform_movie_data(tmdb_data)
            except Exception as e:
                print(f"  ✗ Transform error: {e}")
                self.stats['errors'] += 1
                continue
            
            # Import to database
            self.import_movie(movie_data)
            
            # Show progress every batch_size movies
            if i % batch_size == 0:
                self.print_stats()
        
        print("\n" + "=" * 60)
        print("Import Complete!")
        self.print_stats()
    
    def import_from_file(self, filename: str = 'movie_ids.json'):
        """Import movies from a saved movie IDs file"""
        movie_ids = load_movie_ids_from_file(filename)
        if movie_ids:
            self.import_from_tmdb_ids(movie_ids)
        else:
            print("No movie IDs found in file")
    
    def print_stats(self):
        """Print import statistics"""
        print("\n" + "-" * 60)
        print("Import Statistics:")
        print(f"  Total:    {self.stats['total']}")
        print(f"  Imported: {self.stats['imported']} (new)")
        print(f"  Updated:  {self.stats['updated']} (existing)")
        print(f"  Skipped:  {self.stats['skipped']}")
        print(f"  Errors:   {self.stats['errors']}")
        
        if self.stats['total'] > 0:
            success_rate = ((self.stats['imported'] + self.stats['updated']) / self.stats['total']) * 100
            print(f"  Success:  {success_rate:.1f}%")
        print("-" * 60)
    
    def validate_database(self):
        """Validate imported data"""
        print("\nValidating database...")
        
        total_movies = self.db.query(Movie).count()
        print(f"  Total movies in database: {total_movies}")
        
        # Check for movies with TMDB data
        movies_with_tmdb = self.db.query(Movie).filter(Movie.tmdb_id.isnot(None)).count()
        print(f"  Movies with TMDB ID: {movies_with_tmdb}")
        
        # Check for movies with enhanced data
        movies_with_budget = self.db.query(Movie).filter(Movie.budget.isnot(None), Movie.budget > 0).count()
        print(f"  Movies with budget data: {movies_with_budget}")
        
        movies_with_keywords = self.db.query(Movie).filter(Movie.keywords.isnot(None)).count()
        print(f"  Movies with keywords: {movies_with_keywords}")
        
        movies_with_cast_details = self.db.query(Movie).filter(Movie.cast_details.isnot(None)).count()
        print(f"  Movies with cast details: {movies_with_cast_details}")
        
        # Sample some movies
        print("\nSample movies:")
        sample_movies = self.db.query(Movie).filter(Movie.tmdb_id.isnot(None)).limit(5).all()
        for movie in sample_movies:
            print(f"  - {movie.title} ({movie.release_year})")
            print(f"    Budget: ${movie.budget:,}" if movie.budget else "    Budget: N/A")
            print(f"    Rating: {movie.vote_average}/10" if movie.vote_average else "    Rating: N/A")
    
    def close(self):
        """Close database connection"""
        self.db.close()


def collect_movie_ids(fetcher: TMDBFetcher, target_count: int = 10000) -> List[int]:
    """
    Collect movie IDs from various sources to reach target count
    
    Args:
        fetcher: TMDBFetcher instance
        target_count: Target number of unique movie IDs
    
    Returns:
        List of unique movie IDs
    """
    all_movie_ids = set()
    
    print(f"Collecting {target_count} movie IDs from TMDB...")
    print("=" * 60)
    
    # 1. Popular movies (500 pages = ~10,000 movies)
    print("\n1. Fetching popular movies...")
    popular_ids = fetcher.fetch_movie_ids_by_category('popular', max_pages=250)
    all_movie_ids.update(popular_ids)
    print(f"   Total unique IDs: {len(all_movie_ids)}")
    
    if len(all_movie_ids) >= target_count:
        return list(all_movie_ids)[:target_count]
    
    # 2. Top rated movies
    print("\n2. Fetching top rated movies...")
    top_rated_ids = fetcher.fetch_movie_ids_by_category('top_rated', max_pages=100)
    all_movie_ids.update(top_rated_ids)
    print(f"   Total unique IDs: {len(all_movie_ids)}")
    
    if len(all_movie_ids) >= target_count:
        return list(all_movie_ids)[:target_count]
    
    # 3. Discover movies (sorted by popularity)
    print("\n3. Fetching discovered movies...")
    discover_ids = fetcher.fetch_movie_ids_by_category('discover', max_pages=200)
    all_movie_ids.update(discover_ids)
    print(f"   Total unique IDs: {len(all_movie_ids)}")
    
    if len(all_movie_ids) >= target_count:
        return list(all_movie_ids)[:target_count]
    
    # 4. Movies by year (recent years)
    print("\n4. Fetching movies by year (2015-2024)...")
    year_ids = fetcher.fetch_movies_by_year_range(2015, 2024, max_pages=10)
    all_movie_ids.update(year_ids)
    print(f"   Total unique IDs: {len(all_movie_ids)}")
    
    print("\n" + "=" * 60)
    print(f"Collected {len(all_movie_ids)} unique movie IDs")
    
    return list(all_movie_ids)[:target_count]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import TMDB movie data')
    parser.add_argument('--collect', action='store_true', help='Collect movie IDs from TMDB')
    parser.add_argument('--import', dest='import_data', action='store_true', help='Import movies from collected IDs')
    parser.add_argument('--count', type=int, default=1000, help='Number of movies to collect (default: 1000)')
    parser.add_argument('--validate', action='store_true', help='Validate database after import')
    parser.add_argument('--file', type=str, default='movie_ids.json', help='File to save/load movie IDs')
    
    args = parser.parse_args()
    
    # Create tables if they don't exist
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    if args.collect:
        # Collect movie IDs
        try:
            fetcher = TMDBFetcher()
            movie_ids = collect_movie_ids(fetcher, target_count=args.count)
            
            # Save to file
            from tmdb_data_fetcher import save_movie_ids_to_file
            save_movie_ids_to_file(movie_ids, args.file)
            
        except ValueError as e:
            print(f"Error: {e}")
            print("\nPlease add your TMDB API key to the .env file:")
            print("TMDB_API_KEY=your_api_key_here")
            exit(1)
    
    if args.import_data:
        # Import movies
        importer = MovieImporter()
        try:
            importer.import_from_file(args.file)
        finally:
            importer.close()
    
    if args.validate:
        # Validate database
        importer = MovieImporter()
        try:
            importer.validate_database()
        finally:
            importer.close()
    
    if not any([args.collect, args.import_data, args.validate]):
        parser.print_help()
        print("\nExample usage:")
        print("  # Collect 10,000 movie IDs")
        print("  python data_importer.py --collect --count 10000")
        print("\n  # Import collected movies")
        print("  python data_importer.py --import")
        print("\n  # Validate database")
        print("  python data_importer.py --validate")
        print("\n  # Do everything")
        print("  python data_importer.py --collect --import --validate --count 5000")
