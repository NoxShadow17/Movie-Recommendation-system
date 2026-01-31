# Synthetic User Generation Guide

## Overview

The synthetic user generator creates realistic users and ratings for collaborative filtering model training.

## What It Does

**Creates:**
- 500 synthetic users (configurable)
- 50,000-75,000 ratings (avg 100-150 per user)
- Realistic rating patterns based on genre preferences
- Temporal distribution (ratings spread over past year)
- Mood tags for each rating

## User Personas (10 Types)

1. **Action Lover** - Prefers action, adventure, thriller
2. **Drama Enthusiast** - Loves drama, romance, biography
3. **Comedy Fan** - Enjoys comedy, animation, family films
4. **Horror Buff** - Watches horror, thriller, mystery
5. **Sci-Fi Geek** - Likes sci-fi, fantasy, adventure
6. **Indie Critic** - Prefers drama, documentary, foreign films
7. **Family Viewer** - Watches family, animation, comedy
8. **Blockbuster Chaser** - Enjoys action, sci-fi, adventure
9. **Romance Reader** - Loves romance, drama, comedy
10. **Classic Film Buff** - Prefers classic drama, film-noir, westerns

## How It Works

### 1. Movie Scoring
Each user persona scores movies based on:
- **Genre match** (+0.3 for preferred, -0.4 for disliked)
- **Quality** (TMDB rating influence)
- **Popularity** (more popular = more likely to watch)
- **Recency** (newer movies slightly preferred)

### 2. Movie Selection
Users watch movies with weighted probability:
- 50% from top-matching movies (genre preferences)
- 30% from moderately-matching movies
- 20% from diverse selection (for variety)

### 3. Rating Generation
Ratings (1-5 stars) based on:
- TMDB rating as baseline
- Persona bias (some users rate higher/lower)
- Genre match quality
- Random variation (±0.5 stars)

### 4. Mood Assignment
Mood tags assigned based on:
- Movie genres
- Rating value
- Realistic mood-genre mapping

## Usage

### Generate 500 Users (Default)
```bash
python generate_synthetic_users.py
```

### Generate Custom Number
```bash
# 1000 users (~100,000-150,000 ratings)
python generate_synthetic_users.py --users 1000

# 100 users for testing (~10,000-15,000 ratings)
python generate_synthetic_users.py --users 100
```

### Validate Generated Data
```bash
python generate_synthetic_users.py --validate
```

## Expected Output

```
Generating 500 synthetic users...
======================================================================
Loading movies from database...
  Loaded 6,204 movies
  Found 20 unique genres

  [50/500] Created users with 6,234 ratings
  [100/500] Created users with 12,567 ratings
  [150/500] Created users with 18,891 ratings
  ...
  [500/500] Created users with 62,450 ratings

======================================================================
Synthetic Data Generation Complete!
======================================================================
  Users created:    500
  Ratings created:  62,450
  Avg ratings/user: 124.9
======================================================================
```

## Data Quality

### Realistic Patterns
- ✅ Genre preferences (users consistently rate preferred genres higher)
- ✅ Quality awareness (higher-rated movies get better ratings)
- ✅ Temporal distribution (ratings spread over time)
- ✅ Rating variance (not all 5 stars, realistic distribution)
- ✅ Mood consistency (moods match genres and ratings)

### Statistics
- **Users:** 500
- **Ratings:** 50,000-75,000
- **Avg ratings/user:** 100-150
- **Rating distribution:** Bell curve centered around 3.5-4.0
- **Coverage:** ~80% of movies rated by at least one user

## Benefits for ML Training

### 1. Collaborative Filtering
- ✅ Sufficient user-item interactions (50,000+)
- ✅ Sparse matrix suitable for matrix factorization
- ✅ User similarity patterns for k-NN

### 2. Cold Start Handling
- ✅ New users can be matched to similar personas
- ✅ New movies get ratings from diverse users

### 3. Evaluation
- ✅ Can split into train/test sets
- ✅ Realistic user behavior for testing
- ✅ Ground truth for recommendation quality

## Next Steps

After generating synthetic users:

### 1. Validate Data
```bash
python generate_synthetic_users.py --validate
```

### 2. Train Collaborative Filtering
```python
from sklearn.decomposition import NMF
from app.models import Rating

# Load ratings
ratings = db.query(Rating).all()

# Create user-item matrix
# Train matrix factorization model
# Generate recommendations
```

### 3. Test Recommendations
```python
# Get recommendations for synthetic user
user_id = 1  # synthetic_user_0001
recommendations = get_collaborative_recommendations(user_id)
```

### 4. Compare with Content-Based
```python
# Compare collaborative vs content-based
# Measure precision, recall, diversity
# Tune hybrid weights
```

## Customization

### Add New Personas
Edit `USER_PERSONAS` in `generate_synthetic_users.py`:
```python
{
    "name": "Documentary Lover",
    "preferred_genres": ["Documentary", "Biography"],
    "disliked_genres": ["Action", "Horror"],
    "rating_bias": -0.2,
    "rating_count_range": (80, 160)
}
```

### Adjust Rating Patterns
Modify `generate_rating()` method:
- Change bias strength
- Adjust randomness
- Modify quality influence

### Change Distribution
Modify `generate_ratings_for_user()`:
- Change top/middle/bottom percentages
- Adjust rating count ranges
- Modify temporal distribution

## Troubleshooting

**"Not enough movies"**
→ Need at least 1,000 movies in database

**"Slow generation"**
→ Normal for 500+ users, takes 2-5 minutes

**"Duplicate users"**
→ Script skips existing synthetic users

**"Low rating count"**
→ Increase `rating_count_range` in personas

## Performance

- **100 users:** ~30 seconds
- **500 users:** ~2-3 minutes
- **1000 users:** ~5-7 minutes

Memory usage: ~100-200 MB
