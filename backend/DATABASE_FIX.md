# Quick Fix for Database Schema Issue

## Problem
The error `no such column: movies.original_title` means your SQLite database doesn't have the new columns yet.

## Solution (Choose One)

### Option 1: Run Migration Script (Preserves Existing Data)
```bash
python migrate_database.py
```

This will add all 20 new columns to your existing database without losing data.

### Option 2: Recreate Database (Fresh Start - Recommended for Testing)
```bash
python migrate_database.py --recreate
```

**WARNING:** This deletes all existing data and creates a fresh database with the new schema.

### Option 3: Manual SQLite Fix
If the migration script doesn't work, manually add columns:

```bash
# Stop your backend server first!

# Then run this in Python:
python
>>> import sqlite3
>>> conn = sqlite3.connect('movie_recommendation.db')
>>> cursor = conn.cursor()
>>> 
>>> # Add new columns
>>> cursor.execute("ALTER TABLE movies ADD COLUMN original_title VARCHAR(500)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN tagline VARCHAR(500)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN release_year INTEGER")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN status VARCHAR(50)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN keywords TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN adult BOOLEAN DEFAULT 0")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN cast_details TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN crew_details TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN top_actors VARCHAR(500)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN writers VARCHAR(500)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN producers VARCHAR(500)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN original_language VARCHAR(10)")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN spoken_languages TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN production_countries TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN production_companies TEXT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN budget INTEGER")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN revenue INTEGER")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN vote_average FLOAT")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN vote_count INTEGER")
>>> cursor.execute("ALTER TABLE movies ADD COLUMN tmdb_popularity FLOAT")
>>> 
>>> conn.commit()
>>> conn.close()
>>> exit()
```

## After Migration

1. **Restart your backend server** (if running)
2. **Continue import:**
   ```bash
   python data_importer.py --import
   ```

## If You Want a Clean Start

Since you're just starting the import, I recommend Option 2 (recreate):

```bash
# 1. Stop backend server (Ctrl+C in that terminal)

# 2. Recreate database
python migrate_database.py --recreate
# Type 'yes' when prompted

# 3. Restart backend server
python main.py

# 4. Continue import
python data_importer.py --import
```

This gives you a fresh database with all the new columns ready to go!
