# TMDB Dataset Expansion Guide

## Quick Start

### Step 1: Get TMDB API Key (Free)

1. Go to https://www.themoviedb.org/
2. Create a free account
3. Go to Settings → API
4. Request an API key (choose "Developer" option)
5. Copy your API key

### Step 2: Configure Environment

Add your API key to `.env` file:

```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your API key
TMDB_API_KEY=your_actual_api_key_here
```

### Step 3: Install Dependencies

```bash
pip install requests
```

### Step 4: Test Connection

```bash
python tmdb_data_fetcher.py
```

This will test the connection and fetch a single movie (The Shawshank Redemption).

### Step 5: Collect Movie IDs

Collect 1,000 movie IDs for testing:

```bash
python data_importer.py --collect --count 1000
```

This creates `movie_ids.json` with 1,000 movie IDs.

### Step 6: Import Movies

Import the collected movies into your database:

```bash
python data_importer.py --import
```

This will:
- Fetch complete data for each movie from TMDB
- Transform it to your database format
- Import with duplicate checking
- Show progress and statistics

### Step 7: Validate

Check the imported data:

```bash
python data_importer.py --validate
```

## Full Import (10,000+ Movies)

Once you've tested with 1,000 movies, do a full import:

```bash
# Collect 10,000 movie IDs
python data_importer.py --collect --count 10000

# Import all collected movies (takes 2-4 hours)
python data_importer.py --import

# Validate the results
python data_importer.py --validate
```

## All-in-One Command

```bash
python data_importer.py --collect --import --validate --count 5000
```

## What Gets Imported

Each movie will have:

### Basic Info
- Title, original title, tagline, overview
- Release date, release year, status
- Poster and backdrop images

### Financial Data (ML Features)
- Budget (production cost)
- Revenue (box office earnings)

### Ratings & Popularity
- TMDB rating (vote_average, vote_count)
- TMDB popularity score
- Our internal ratings

### Content Metadata
- Genres (comma-separated)
- Keywords (for ML content analysis)
- Adult content flag

### Cast & Crew (Enhanced)
- Top 5 actors
- Full cast details (JSON with character info)
- Directors, writers, producers
- Full crew details (JSON with departments)

### Production Details
- Production companies (JSON)
- Production countries (JSON)
- Spoken languages (JSON)
- Runtime

## Database Schema

The Movie model now has **25+ new columns** optimized for ML:

```python
# Financial features
budget, revenue

# Popularity features  
vote_average, vote_count, tmdb_popularity

# Content features
keywords, tagline, original_title, original_language

# Production features
production_companies, production_countries, spoken_languages

# Cast/crew features (JSON)
cast_details, crew_details, top_actors, writers, producers

# Metadata
release_year, status, adult
```

## Troubleshooting

**API Key Error:**
```
Error: TMDB_API_KEY not found
```
→ Make sure you added your API key to `.env` file

**Rate Limit:**
```
429 Too Many Requests
```
→ The script automatically handles this with delays

**Database Error:**
```
No such column: movies.budget
```
→ Restart your backend server to recreate tables with new schema

## Next Steps After Import

1. **Feature Engineering** - Create ML features from imported data
2. **Model Training** - Train better recommendation models
3. **API Updates** - Expose new fields in API responses
4. **Frontend Updates** - Display budget, cast, keywords, etc.

## Performance Notes

- **Collection:** ~5-10 minutes for 10,000 IDs
- **Import:** ~2-4 hours for 10,000 movies (with API rate limits)
- **Storage:** ~50-100 MB for 10,000 movies
- **Rate Limit:** 40 requests per 10 seconds (TMDB limit)
