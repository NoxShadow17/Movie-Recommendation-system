# Advanced Recommendation Engine Documentation

## Overview

The Movie Recommendation System now features a sophisticated, multi-algorithm recommendation engine that combines multiple advanced techniques to provide highly personalized movie suggestions.

## 🚀 Enhanced Features

### 1. Advanced Trending Analysis
- **Multi-factor Trend Scoring**: Volume, quality, recency, and momentum analysis
- **Time-based Periods**: Daily, weekly, and monthly trending calculations
- **Momentum Detection**: Identifies movies gaining popularity velocity
- **Quality Filtering**: Penalizes high variance in ratings to ensure quality

### 2. Sophisticated Social Recommendations
- **Friend-based Filtering**: Recommendations from users' social connections
- **Preference Matching**: Matches friends' recommendations with user preferences
- **Variance Analysis**: Penalizes recommendations with high rating variance
- **Quality Boosts**: Enhances scores based on overall movie quality

### 3. Advanced Mood-Based Recommendations
- **Historical Mood Analysis**: Learns from user's past mood-based ratings
- **Director Preferences**: Maps directors to specific moods
- **Genre-Mood Mapping**: Advanced genre-to-mood compatibility scoring
- **Personalization**: Adapts to individual user mood patterns

### 4. Intelligent User Profiling
- **Automatic Profile Updates**: Continuously learns from user behavior
- **Preference Extraction**: Analyzes genre, director, and language preferences
- **Mood Pattern Recognition**: Identifies user's mood rating patterns
- **Profile Statistics**: Comprehensive user preference analytics

## 📊 Recommendation Algorithms

### Hybrid Recommendation Engine
Combines multiple algorithms with weighted scoring:

```python
# Weight configuration (configurable)
COLLABORATIVE_WEIGHT = 0.6  # 60% collaborative filtering
CONTENT_BASED_WEIGHT = 0.4  # 40% content-based filtering

# Hybrid scoring formula:
hybrid_score = (
    COLLABORATIVE_WEIGHT * 0.8 * normalized_collaborative +
    CONTENT_BASED_WEIGHT * 0.6 * normalized_enhanced_content +
    CONTENT_BASED_WEIGHT * 0.4 * normalized_basic_content
)
```

### Collaborative Filtering
- **User Similarity**: Cosine similarity based on rating patterns
- **Minimum Threshold**: Requires minimum common ratings (configurable)
- **Weighted Averaging**: Applies similarity weights to predictions
- **Cold Start Handling**: Graceful degradation for new users

### Content-Based Filtering
- **Genre Matching**: Multi-genre compatibility scoring
- **Director Analysis**: Director preference matching
- **Language Filtering**: Language-based recommendations
- **Quality Scoring**: Combines user preferences with movie quality

## 🔧 API Endpoints

### Enhanced Recommendation Endpoints

#### 1. Personalized Recommendations
```http
GET /api/v1/recommendations/
```
- **Description**: Get hybrid recommendations based on complete user profile
- **Parameters**: `limit` (1-500)
- **Returns**: Personalized movie recommendations with reasons

#### 2. Trending by Period
```http
GET /api/v1/recommendations/trending/{period}
```
- **Description**: Get trending movies for specific time periods
- **Parameters**: `period` (daily|weekly|monthly), `limit`
- **Features**: Advanced trend scoring with momentum analysis

#### 3. Detailed Social Recommendations
```http
GET /api/v1/recommendations/friends/detailed
```
- **Description**: Get social recommendations with detailed metadata
- **Features**: Friend count, average ratings, preference matching
- **Returns**: Enhanced social recommendation data

#### 4. Advanced Mood Recommendations
```http
GET /api/v1/recommendations/mood/{mood}/advanced
```
- **Description**: Get mood-based recommendations with history analysis
- **Features**: User mood history, director preferences, compatibility scoring
- **Moods**: happy, sad, excited, relaxed, thoughtful, scared

### Profile Management Endpoints

#### 1. Update User Profile
```http
POST /api/v1/recommendations/profile/update
```
- **Description**: Automatically update user preferences from rating history
- **Features**: Genre analysis, director preferences, mood patterns
- **Returns**: Success/failure status

#### 2. Get Profile Statistics
```http
GET /api/v1/recommendations/profile/stats
```
- **Description**: Get comprehensive user preference analytics
- **Returns**: 
  - Total ratings count
  - Preferred genres and directors
  - Mood distribution analysis
  - Top genre preferences
  - Last update timestamp

## 🎯 Advanced Features

### 1. Mood-to-Genre Mapping
```python
MOOD_TO_GENRES = {
    "happy": ["Comedy", "Animation", "Family", "Musical"],
    "sad": ["Drama", "Romance", "Tragedy"],
    "excited": ["Action", "Adventure", "Thriller", "Sci-Fi"],
    "relaxed": ["Comedy", "Drama", "Animation", "Slice of Life"],
    "thoughtful": ["Drama", "Documentary", "Sci-Fi", "Mystery", "Philosophical"],
    "scared": ["Horror", "Thriller", "Suspense", "Supernatural"]
}
```

### 2. Mood-to-Director Mapping
```python
MOOD_TO_DIRECTORS = {
    "happy": ["Wes Anderson", "Richard Linklater", "Greta Gerwig"],
    "sad": ["Denis Villeneuve", "Darren Aronofsky", "Lars von Trier"],
    "excited": ["Christopher Nolan", "James Cameron", "George Miller"],
    "relaxed": ["Hayao Miyazaki", "Wes Anderson", "Richard Linklater"],
    "thoughtful": ["Christopher Nolan", "Denis Villeneuve", "Stanley Kubrick"],
    "scared": ["James Wan", "Jordan Peele", "Ari Aster"]
}
```

### 3. Trending Score Calculation
```python
# Advanced trend score with multiple factors
trend_score = (
    volume_score * 0.4 +      # How many ratings
    quality_score * 0.3 +     # Average rating with confidence
    recency_score * 0.2 +     # How recent the activity
    momentum_score * 0.1      # Growth rate
) * 100  # Scale to 0-100
```

## 📈 Dashboard Features

### Recommendation Dashboard (`RecommendationDashboard.js`)
- **Interactive Charts**: Mood distribution, genre preferences
- **Profile Analytics**: Comprehensive user statistics
- **Real-time Updates**: Live profile statistics
- **Action Buttons**: Quick access to different recommendation types

### Chart Types
1. **Pie Chart**: Mood distribution analysis
2. **Bar Chart**: Genre preference visualization
3. **Stat Cards**: Key metrics and insights

## 🔧 Configuration

### Algorithm Weights
```python
# In backend/app/core/config.py
COLLABORATIVE_WEIGHT = 0.6  # Weight for collaborative filtering
CONTENT_BASED_WEIGHT = 0.4  # Weight for content-based filtering
MIN_COMMON_RATINGS = 3      # Minimum common ratings for similarity
RECOMMENDATION_COUNT = 10   # Default recommendation count
```

### Feature Flags
```python
ENABLE_SOCIAL_FEATURES = True   # Enable friend-based recommendations
ENABLE_MOOD_BASED = True        # Enable mood-based recommendations
ENABLE_TRENDING = True          # Enable trending analysis
```

## 🎨 Frontend Integration

### Enhanced Recommendations Page
- **Tabbed Interface**: Personalized, trending, mood, friends
- **Mood Selector**: Interactive mood selection for recommendations
- **Real-time Updates**: Live recommendation updates

### Dashboard Components
- **Statistics Overview**: Key metrics and insights
- **Mood Analysis**: Visual mood pattern analysis
- **Genre Preferences**: Genre preference visualization
- **Profile Management**: One-click profile updates

## 📊 Performance Optimizations

### Database Optimizations
- **Indexed Queries**: Optimized database queries for large datasets
- **Caching Strategy**: Strategic caching for frequently accessed data
- **Pagination**: Efficient handling of large recommendation lists

### Algorithm Optimizations
- **Lazy Loading**: Load data only when needed
- **Batch Processing**: Process recommendations in batches
- **Memory Management**: Efficient memory usage for large datasets

## 🔍 Quality Assurance

### Testing Strategy
- **Unit Tests**: Individual algorithm component testing
- **Integration Tests**: End-to-end recommendation flow testing
- **Performance Tests**: Load testing for recommendation algorithms
- **A/B Testing**: Compare different algorithm configurations

### Monitoring
- **Recommendation Quality**: Track recommendation accuracy over time
- **User Engagement**: Monitor user interaction with recommendations
- **Algorithm Performance**: Track algorithm response times and accuracy

## 🚀 Future Enhancements

### Planned Features
1. **Deep Learning Integration**: Neural network-based recommendations
2. **Real-time Processing**: Streaming recommendation updates
3. **A/B Testing Framework**: Automated algorithm comparison
4. **Multi-modal Recommendations**: Combine text, image, and audio analysis
5. **Explainable AI**: Detailed explanation of recommendation reasoning

### Research Areas
- **Context-aware Recommendations**: Time, location, device-based suggestions
- **Emotion Recognition**: AI-based emotion detection for mood recommendations
- **Social Network Analysis**: Advanced social graph-based recommendations
- **Cross-domain Recommendations**: Leverage preferences from other domains

## 📚 Technical Architecture

### Backend Architecture
- **Microservices**: Modular recommendation algorithm services
- **Database Design**: Optimized schema for recommendation queries
- **API Design**: RESTful endpoints with comprehensive documentation
- **Security**: JWT-based authentication and authorization

### Frontend Architecture
- **Component-based**: Modular React components
- **State Management**: Efficient state management for large datasets
- **Responsive Design**: Mobile-first responsive design
- **Performance**: Optimized rendering and data fetching

This advanced recommendation engine represents a significant upgrade from basic recommendation systems, providing users with highly personalized, context-aware movie suggestions that continuously improve based on user behavior and preferences.
