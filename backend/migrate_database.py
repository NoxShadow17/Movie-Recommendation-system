"""
Database Migration Script
Adds new columns to existing movies table for TMDB data expansion
"""

import sqlite3
import os
from sqlalchemy import create_engine, inspect, text
from app.core.database import engine, SessionLocal
from app.models import Base

def get_existing_columns(table_name='movies'):
    """Get list of existing columns in the table"""
    inspector = inspect(engine)
    if table_name in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return columns
    return []

def migrate_sqlite_database():
    """Migrate SQLite database by adding new columns"""
    print("Starting database migration...")
    print("=" * 60)
    
    # Get database URL
    db_url = str(engine.url)
    print(f"Database: {db_url}")
    
    # Check if using SQLite
    if not db_url.startswith('sqlite'):
        print("\n⚠️  This migration is for SQLite databases only")
        print("For PostgreSQL, the columns will be created automatically")
        print("Just restart your backend server.")
        return
    
    # Get existing columns
    existing_columns = get_existing_columns('movies')
    print(f"\nExisting columns: {len(existing_columns)}")
    
    # Define new columns to add
    new_columns = {
        'original_title': 'VARCHAR(500)',
        'tagline': 'VARCHAR(500)',
        'release_year': 'INTEGER',
        'status': 'VARCHAR(50)',
        'keywords': 'TEXT',
        'adult': 'BOOLEAN DEFAULT 0',
        'cast_details': 'TEXT',
        'crew_details': 'TEXT',
        'top_actors': 'VARCHAR(500)',
        'writers': 'VARCHAR(500)',
        'producers': 'VARCHAR(500)',
        'original_language': 'VARCHAR(10)',
        'spoken_languages': 'TEXT',
        'production_countries': 'TEXT',
        'production_companies': 'TEXT',
        'budget': 'INTEGER',
        'revenue': 'INTEGER',
        'vote_average': 'FLOAT',
        'vote_count': 'INTEGER',
        'tmdb_popularity': 'FLOAT'
    }
    
    # Connect to database
    db = SessionLocal()
    
    try:
        added_count = 0
        skipped_count = 0
        
        for column_name, column_type in new_columns.items():
            if column_name in existing_columns:
                print(f"  ⏭️  {column_name} - already exists")
                skipped_count += 1
            else:
                try:
                    # Add column using raw SQL
                    sql = f"ALTER TABLE movies ADD COLUMN {column_name} {column_type}"
                    db.execute(text(sql))
                    db.commit()
                    print(f"  ✅ {column_name} - added")
                    added_count += 1
                except Exception as e:
                    print(f"  ❌ {column_name} - error: {e}")
                    db.rollback()
        
        print("\n" + "=" * 60)
        print(f"Migration complete!")
        print(f"  Added: {added_count} columns")
        print(f"  Skipped: {skipped_count} columns (already exist)")
        print(f"  Total columns now: {len(existing_columns) + added_count}")
        
        # Verify
        print("\nVerifying migration...")
        new_existing = get_existing_columns('movies')
        print(f"  Final column count: {len(new_existing)}")
        
        if len(new_existing) >= 36:
            print("  ✅ Migration successful!")
        else:
            print("  ⚠️  Some columns may be missing")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


def recreate_database():
    """Recreate database from scratch (WARNING: deletes all data!)"""
    print("\n⚠️  WARNING: This will DELETE ALL DATA and recreate the database!")
    response = input("Are you sure? Type 'yes' to continue: ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\nRecreating database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("  ✅ Dropped all tables")
    
    # Create all tables with new schema
    Base.metadata.create_all(bind=engine)
    print("  ✅ Created all tables with new schema")
    
    # Verify
    existing_columns = get_existing_columns('movies')
    print(f"\n  Total columns: {len(existing_columns)}")
    print("  ✅ Database recreated successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database to add new columns')
    parser.add_argument('--recreate', action='store_true', 
                       help='Recreate database from scratch (DELETES ALL DATA)')
    
    args = parser.parse_args()
    
    if args.recreate:
        recreate_database()
    else:
        migrate_sqlite_database()
        
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Restart your backend server if it's running")
        print("2. Continue with data import:")
        print("   python data_importer.py --import")
