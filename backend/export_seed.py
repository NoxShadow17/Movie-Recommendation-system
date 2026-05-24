"""
Export local SQLite data to a compressed JSON seed file.
Run this ONCE locally to generate seed_data.json.gz
"""
import sqlite3
import json
import gzip
import os

DB_PATH = 'movie_recommendation.db'
OUTPUT_PATH = 'seed_data/seed_data.json.gz'

os.makedirs('seed_data', exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

tables_to_export = ['users', 'movies', 'ratings', 'friendships', 'user_friends', 'user_watchlist', 'trending_movies']

data = {}
for table in tables_to_export:
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    data[table] = [dict(row) for row in rows]
    print(f"Exported {len(rows)} rows from {table}")

conn.close()

# Write compressed JSON
with gzip.open(OUTPUT_PATH, 'wt', encoding='utf-8') as f:
    json.dump(data, f)

size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
print(f"\nSeed file written to {OUTPUT_PATH} ({size_mb:.2f} MB)")
print("Done! Commit this file to git and Render will auto-seed on startup.")
