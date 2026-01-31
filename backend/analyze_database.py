"""
Database Analysis and ML Readiness Check
Analyzes the imported movie dataset for ML model training
"""

import sys
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models import Movie, Rating, User

def analyze_database():
    """Comprehensive database analysis for ML readiness"""
    db = SessionLocal()
    
    print("=" * 70)
    print("DATABASE ANALYSIS FOR ML MODEL TRAINING")
    print("=" * 70)
    
    # Basic counts
    print("\n📊 DATASET SIZE")
    print("-" * 70)
    total_movies = db.query(Movie).count()
    total_users = db.query(User).count()
    total_ratings = db.query(Rating).count()
    
    print(f"  Movies:  {total_movies:,}")
    print(f"  Users:   {total_users:,}")
    print(f"  Ratings: {total_ratings:,}")
    
    # Movie data quality
    print("\n🎬 MOVIE DATA QUALITY")
    print("-" * 70)
    
    movies_with_tmdb = db.query(Movie).filter(Movie.tmdb_id.isnot(None)).count()
    movies_with_budget = db.query(Movie).filter(Movie.budget.isnot(None), Movie.budget > 0).count()
    movies_with_revenue = db.query(Movie).filter(Movie.revenue.isnot(None), Movie.revenue > 0).count()
    movies_with_keywords = db.query(Movie).filter(Movie.keywords.isnot(None), Movie.keywords != '').count()
    movies_with_cast = db.query(Movie).filter(Movie.cast_details.isnot(None)).count()
    movies_with_crew = db.query(Movie).filter(Movie.crew_details.isnot(None)).count()
    movies_with_vote_avg = db.query(Movie).filter(Movie.vote_average.isnot(None)).count()
    movies_with_popularity = db.query(Movie).filter(Movie.tmdb_popularity.isnot(None)).count()
    
    print(f"  TMDB ID:           {movies_with_tmdb:,} ({movies_with_tmdb/total_movies*100:.1f}%)")
    print(f"  Budget data:       {movies_with_budget:,} ({movies_with_budget/total_movies*100:.1f}%)")
    print(f"  Revenue data:      {movies_with_revenue:,} ({movies_with_revenue/total_movies*100:.1f}%)")
    print(f"  Keywords:          {movies_with_keywords:,} ({movies_with_keywords/total_movies*100:.1f}%)")
    print(f"  Cast details:      {movies_with_cast:,} ({movies_with_cast/total_movies*100:.1f}%)")
    print(f"  Crew details:      {movies_with_crew:,} ({movies_with_crew/total_movies*100:.1f}%)")
    print(f"  TMDB ratings:      {movies_with_vote_avg:,} ({movies_with_vote_avg/total_movies*100:.1f}%)")
    print(f"  Popularity score:  {movies_with_popularity:,} ({movies_with_popularity/total_movies*100:.1f}%)")
    
    # Genre distribution
    print("\n🎭 GENRE DISTRIBUTION (Top 10)")
    print("-" * 70)
    genre_counts = {}
    movies = db.query(Movie).all()
    for movie in movies:
        if movie.genre:
            genres = [g.strip() for g in movie.genre.split(',')]
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for genre, count in top_genres:
        print(f"  {genre:20} {count:,} movies")
    
    # Year distribution
    print("\n📅 RELEASE YEAR DISTRIBUTION")
    print("-" * 70)
    year_stats = db.query(
        func.min(Movie.release_year),
        func.max(Movie.release_year),
        func.avg(Movie.release_year)
    ).filter(Movie.release_year.isnot(None)).first()
    
    if year_stats[0]:
        print(f"  Oldest:  {int(year_stats[0])}")
        print(f"  Newest:  {int(year_stats[1])}")
        print(f"  Average: {int(year_stats[2])}")
    
    # Recent movies
    recent_movies = db.query(Movie).filter(Movie.release_year >= 2020).count()
    print(f"  Movies from 2020+: {recent_movies:,}")
    
    # Rating statistics
    print("\n⭐ RATING STATISTICS")
    print("-" * 70)
    rating_stats = db.query(
        func.min(Movie.vote_average),
        func.max(Movie.vote_average),
        func.avg(Movie.vote_average)
    ).filter(Movie.vote_average.isnot(None)).first()
    
    if rating_stats[0]:
        print(f"  Min rating:  {rating_stats[0]:.1f}/10")
        print(f"  Max rating:  {rating_stats[1]:.1f}/10")
        print(f"  Avg rating:  {rating_stats[2]:.1f}/10")
    
    # Budget/Revenue statistics
    print("\n💰 FINANCIAL DATA")
    print("-" * 70)
    budget_stats = db.query(
        func.min(Movie.budget),
        func.max(Movie.budget),
        func.avg(Movie.budget)
    ).filter(Movie.budget.isnot(None), Movie.budget > 0).first()
    
    if budget_stats[0]:
        print(f"  Min budget:  ${budget_stats[0]:,}")
        print(f"  Max budget:  ${budget_stats[1]:,}")
        print(f"  Avg budget:  ${int(budget_stats[2]):,}")
    
    revenue_stats = db.query(
        func.min(Movie.revenue),
        func.max(Movie.revenue),
        func.avg(Movie.revenue)
    ).filter(Movie.revenue.isnot(None), Movie.revenue > 0).first()
    
    if revenue_stats[0]:
        print(f"  Min revenue: ${revenue_stats[0]:,}")
        print(f"  Max revenue: ${revenue_stats[1]:,}")
        print(f"  Avg revenue: ${int(revenue_stats[2]):,}")
    
    # Sample movies
    print("\n🎬 SAMPLE MOVIES (Random 5)")
    print("-" * 70)
    sample_movies = db.query(Movie).filter(
        Movie.tmdb_id.isnot(None)
    ).order_by(func.random()).limit(5).all()
    
    for movie in sample_movies:
        print(f"\n  {movie.title} ({movie.release_year})")
        print(f"    Rating: {movie.vote_average}/10 ({movie.vote_count:,} votes)")
        if movie.budget and movie.budget > 0:
            print(f"    Budget: ${movie.budget:,}")
        if movie.revenue and movie.revenue > 0:
            print(f"    Revenue: ${movie.revenue:,}")
        if movie.keywords:
            keywords = movie.keywords.split(',')[:5]
            print(f"    Keywords: {', '.join(keywords)}")
    
    # ML Readiness Assessment
    print("\n" + "=" * 70)
    print("🤖 ML MODEL TRAINING READINESS")
    print("=" * 70)
    
    readiness_score = 0
    max_score = 10
    
    # Criterion 1: Dataset size (2 points)
    if total_movies >= 5000:
        print("  ✅ Dataset Size: EXCELLENT (6,000+ movies)")
        readiness_score += 2
    elif total_movies >= 1000:
        print("  ✅ Dataset Size: GOOD (1,000+ movies)")
        readiness_score += 1.5
    else:
        print("  ⚠️  Dataset Size: SMALL (<1,000 movies)")
        readiness_score += 0.5
    
    # Criterion 2: Feature completeness (2 points)
    feature_completeness = (movies_with_keywords + movies_with_cast + movies_with_vote_avg) / (total_movies * 3)
    if feature_completeness >= 0.9:
        print(f"  ✅ Feature Completeness: EXCELLENT ({feature_completeness*100:.1f}%)")
        readiness_score += 2
    elif feature_completeness >= 0.7:
        print(f"  ✅ Feature Completeness: GOOD ({feature_completeness*100:.1f}%)")
        readiness_score += 1.5
    else:
        print(f"  ⚠️  Feature Completeness: MODERATE ({feature_completeness*100:.1f}%)")
        readiness_score += 1
    
    # Criterion 3: Financial data (1 point)
    financial_completeness = movies_with_budget / total_movies
    if financial_completeness >= 0.5:
        print(f"  ✅ Financial Data: GOOD ({financial_completeness*100:.1f}%)")
        readiness_score += 1
    else:
        print(f"  ⚠️  Financial Data: LIMITED ({financial_completeness*100:.1f}%)")
        readiness_score += 0.5
    
    # Criterion 4: Genre diversity (1 point)
    if len(genre_counts) >= 15:
        print(f"  ✅ Genre Diversity: EXCELLENT ({len(genre_counts)} genres)")
        readiness_score += 1
    else:
        print(f"  ⚠️  Genre Diversity: MODERATE ({len(genre_counts)} genres)")
        readiness_score += 0.5
    
    # Criterion 5: Temporal coverage (1 point)
    if year_stats[0] and (year_stats[1] - year_stats[0]) >= 50:
        print(f"  ✅ Temporal Coverage: EXCELLENT ({int(year_stats[1] - year_stats[0])} years)")
        readiness_score += 1
    else:
        print(f"  ⚠️  Temporal Coverage: MODERATE")
        readiness_score += 0.5
    
    # Criterion 6: User ratings (3 points)
    if total_ratings >= 1000:
        print(f"  ✅ User Ratings: EXCELLENT ({total_ratings:,} ratings)")
        readiness_score += 3
    elif total_ratings >= 100:
        print(f"  ⚠️  User Ratings: MODERATE ({total_ratings:,} ratings)")
        readiness_score += 1.5
    else:
        print(f"  ⚠️  User Ratings: LIMITED ({total_ratings:,} ratings)")
        print("     → Need more user interactions for collaborative filtering")
        readiness_score += 0.5
    
    # Final assessment
    print("\n" + "=" * 70)
    print(f"OVERALL READINESS SCORE: {readiness_score:.1f}/{max_score}")
    print("=" * 70)
    
    if readiness_score >= 8:
        print("\n✅ EXCELLENT - Ready for advanced ML model training!")
        print("   Recommended models:")
        print("   • Matrix Factorization (SVD, NMF)")
        print("   • Deep Learning (Neural Collaborative Filtering)")
        print("   • Content-based with keyword embeddings")
        print("   • Hybrid ensemble models")
    elif readiness_score >= 6:
        print("\n✅ GOOD - Ready for ML model training!")
        print("   Recommended models:")
        print("   • Content-based filtering (keywords, genres, cast)")
        print("   • Popularity-based models")
        print("   • Simple collaborative filtering")
        print("   • Hybrid approaches")
        print("\n   To improve:")
        print("   • Collect more user ratings (current: {})".format(total_ratings))
        print("   • Add user interaction data")
    else:
        print("\n⚠️  MODERATE - Can train basic models")
        print("   Recommended:")
        print("   • Start with content-based filtering")
        print("   • Use TMDB ratings as proxy for user preferences")
        print("   • Collect user interaction data")
        print("   • Consider importing more movies")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\n1. ✅ Dataset is sufficient for content-based models")
    print(f"   • {movies_with_keywords:,} movies with keywords")
    print(f"   • {movies_with_cast:,} movies with cast details")
    print(f"   • Rich metadata for feature engineering")
    
    print("\n2. ⚠️  Need more user ratings for collaborative filtering")
    print(f"   • Current: {total_ratings:,} ratings")
    print(f"   • Recommended: 10,000+ ratings")
    print("   • Solution: Generate synthetic users or collect real data")
    
    print("\n3. ✅ Financial data available for advanced features")
    print(f"   • {movies_with_budget:,} movies with budget")
    print(f"   • {movies_with_revenue:,} movies with revenue")
    print("   • Can use for ROI-based recommendations")
    
    print("\n4. ✅ TMDB ratings can bootstrap collaborative filtering")
    print(f"   • {movies_with_vote_avg:,} movies with TMDB ratings")
    print("   • Can use as initial user preference proxy")
    
    db.close()


if __name__ == "__main__":
    analyze_database()
