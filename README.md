# Advanced Movie Recommendation System

A sophisticated movie recommendation platform featuring hybrid recommendation algorithms, social discovery, mood-based suggestions, and trending analysis.

## Features

### Core Recommendation Engine
- **Hybrid Recommendations**: Combines collaborative filtering (60%) and content-based filtering (40%)
- **Collaborative Filtering**: User-based similarity matching using cosine similarity
- **Content-Based Filtering**: Movie similarity based on genres, directors, and language
- **Intelligent Scoring**: Weighted hybrid approach for accurate recommendations

### Advanced Features
- **Trending Analysis**: Track and recommend movies trending in different periods
- **Social Recommendations**: Get movie suggestions from friends' activity
- **Mood-Based Filtering**: Get recommendations matching your current emotional state
- **Watchlist Management**: Save movies to watch later
- **Friend Connections**: Build a social network and see friend recommendations

### User Features
- User authentication with JWT tokens
- Secure password hashing with bcrypt
- Detailed user profiles with preferences
- Rating and review system
- Multi-mood rating tracking

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── security.py        # JWT & password handling
│   ├── models/
│   │   └── __init__.py        # SQLAlchemy models
│   ├── schemas/
│   │   └── __init__.py        # Pydantic schemas
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── movies.py          # Movie endpoints
│   │   ├── recommendations.py # Recommendation endpoints
│   │   └── users.py           # User endpoints
│   ├── services/
│   │   ├── recommendation_engine.py    # Hybrid algorithm
│   │   └── advanced_recommendations.py # Mood, trending, social
│   └── utils/
│       └── dependencies.py    # Dependency injection
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip/venv

### Setup

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Set up database**
```bash
# The database tables are created automatically on app startup
python main.py
```

6. **Access API**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Movies
- `GET /api/v1/movies/` - List all movies
- `GET /api/v1/movies/{movie_id}` - Get movie details
- `POST /api/v1/movies/{movie_id}/rate` - Rate a movie
- `GET /api/v1/movies/{movie_id}/ratings` - Get movie ratings
- `POST /api/v1/movies/search` - Search movies

### Recommendations
- `GET /api/v1/recommendations/` - Get personalized recommendations
- `GET /api/v1/recommendations/trending` - Get trending movies
- `GET /api/v1/recommendations/friends` - Get friend recommendations
- `GET /api/v1/recommendations/mood/{mood}` - Get mood-based recommendations

Supported moods: `happy`, `sad`, `excited`, `relaxed`, `thoughtful`, `scared`

### Users
- `GET /api/v1/users/{user_id}` - Get user profile
- `PUT /api/v1/users/me` - Update profile
- `GET /api/v1/users/{user_id}/friends` - Get friends list
- `POST /api/v1/users/{friend_id}/add-friend` - Add friend
- `POST /api/v1/users/{movie_id}/add-to-watchlist` - Add to watchlist
- `DELETE /api/v1/users/{movie_id}/remove-from-watchlist` - Remove from watchlist
- `GET /api/v1/users/me/watchlist` - Get watchlist

## Database Schema

### Users
- User authentication and profile information
- Friend connections (self-referential relationship)
- Watchlist management

### Movies
- Movie metadata (title, overview, genres, directors, cast)
- Ratings and reviews
- Trending indicators
- Popularity scores

### Ratings
- User ratings (1-5 scale)
- Written reviews
- Mood tagging (happy, sad, excited, etc.)

### Recommendations
- Generated recommendations with confidence scores
- Algorithm attribution (collaborative, content-based, hybrid)
- Click tracking for A/B testing

### Trending
- Trending movies by period (daily, weekly, monthly)
- Trend scores based on recent activity
- Ranking information

## Configuration

Key settings in `app/core/config.py`:

```python
COLLABORATIVE_WEIGHT = 0.6      # Weight for collaborative filtering
CONTENT_BASED_WEIGHT = 0.4      # Weight for content-based filtering
MIN_COMMON_RATINGS = 3          # Minimum common ratings for similarity
RECOMMENDATION_COUNT = 10        # Default recommendations per request
```

## Recommendation Algorithm

### Hybrid Approach
The system uses a weighted combination of two algorithms:

**1. Collaborative Filtering (60%)**
- Finds users with similar rating patterns using cosine similarity
- Recommends movies rated highly by similar users
- Works best with extensive user data

**2. Content-Based Filtering (40%)**
- Analyzes movie attributes (genres, directors, language)
- Recommends movies similar to ones user has rated
- Works well for new users with few ratings

**Final Score = 0.6 × Collaborative + 0.4 × Content-Based**

## Advanced Features Details

### Trending Analysis
- Tracks rating frequency and average ratings
- Calculates trend scores based on recent activity
- Updates trending indicators periodically
- Supports multiple time periods (daily, weekly, monthly)

### Mood-Based Recommendations
- Maps emotions to movie genres
- Recommends highly-rated movies in mood-appropriate genres
- Personalized based on user preferences

### Social Discovery
- Aggregates ratings from user's friends
- Recommends movies rated highly by friend group
- Shows social proof ("3 friends recommend this")

## Future Enhancements

- [ ] Deep learning models (Neural Collaborative Filtering)
- [ ] Content-based image analysis for poster similarity
- [ ] Real-time recommendation updates
- [ ] Explainable AI features with detailed reasoning
- [ ] A/B testing framework
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Integration with external movie databases (TMDB, IMDb)
- [ ] Recommendation diversity optimization
- [ ] Serendipity recommendations (surprising but relevant)

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
Currently using SQLAlchemy auto-creation. For production, consider using Alembic:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Performance Tips

1. **Indexing**: All foreign keys and commonly queried fields are indexed
2. **Caching**: Implement Redis caching for trending movies
3. **Batch Processing**: Use celery for background recommendation updates
4. **Database Query Optimization**: Use eager loading for related data

## Security Considerations

- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS configured (update in production)
- ✅ Input validation with Pydantic
- ⚠️ Change SECRET_KEY in production
- ⚠️ Enable HTTPS in production
- ⚠️ Use environment variables for secrets

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.

---

**Built with FastAPI, SQLAlchemy, and scikit-learn**
