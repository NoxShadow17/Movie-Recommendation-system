# MovieFlix Frontend

Modern React frontend for the Advanced Movie Recommendation System.

## Features

✨ **User Authentication**
- Login and registration
- JWT token-based authentication
- Session persistence

🎬 **Movie Browsing**
- Browse all available movies
- Search by title and genre
- View detailed movie information
- Rate movies with mood tracking

🤖 **Smart Recommendations**
- Personalized recommendations based on your ratings
- Trending movies
- Mood-based recommendations
- Friend recommendations

👤 **User Profile**
- View your ratings history
- Manage preferences
- Account settings

## Setup Instructions

### 1. Install Node.js
Download from https://nodejs.org/ (LTS version recommended)

### 2. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- React 18.2.0
- React Router for navigation
- Axios for API calls
- Tailwind CSS for styling

### 3. Start the Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

**Important:** Make sure the backend API is running at `http://localhost:8000`

### 4. Login

Use the demo account:
- **Username:** demo_user1
- **Password:** password123

Or create a new account by clicking "Register"

## Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML file
├── src/
│   ├── components/         # Reusable React components
│   │   ├── Navbar.js      # Navigation bar
│   │   └── MovieCard.js   # Movie card component
│   ├── pages/             # Page components
│   │   ├── LoginPage.js
│   │   ├── RegisterPage.js
│   │   ├── DashboardPage.js
│   │   ├── MoviesPage.js
│   │   ├── RecommendationsPage.js
│   │   ├── ProfilePage.js
│   │   └── MovieDetailPage.js
│   ├── App.js             # Main app component with routing
│   ├── index.js           # Entry point
│   └── index.css          # Global styles
├── package.json           # Project dependencies
├── tailwind.config.js     # Tailwind CSS configuration
└── postcss.config.js      # PostCSS configuration
```

## Available Pages

- **Dashboard** (`/`) - Home page with personalized recommendations
- **Movies** (`/movies`) - Browse all movies with search
- **Movie Details** (`/movies/:id`) - View movie details and rate
- **Recommendations** (`/recommendations`) - View different recommendation types
- **Profile** (`/profile`) - View your ratings and preferences
- **Login** (`/login`) - Authentication
- **Register** (`/register`) - New account creation

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`

Key endpoints used:
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/users/profile` - Get current user
- `GET /api/v1/movies/` - List all movies
- `GET /api/v1/movies/{id}` - Get movie details
- `POST /api/v1/movies/{id}/rate` - Rate a movie
- `GET /api/v1/recommendations/` - Get personalized recommendations
- `GET /api/v1/recommendations/trending` - Get trending movies
- `GET /api/v1/recommendations/mood/{mood}` - Get mood-based recommendations

## Styling

The project uses **Tailwind CSS** for styling. Configuration:
- Dark theme with gradient accents
- Primary color: Indigo (6366f1)
- Secondary color: Purple (8b5cf6)
- Custom utility classes in `src/index.css`

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Troubleshooting

**Issue:** "Can't connect to API"
- **Solution:** Ensure backend is running on `http://localhost:8000`
- Check if CORS is enabled in backend

**Issue:** "Module not found"
- **Solution:** Run `npm install` to install all dependencies

**Issue:** Port 3000 already in use
- **Solution:** Kill the process using port 3000 or set `PORT=3001 npm start`

## Next Steps

- Deploy frontend to Vercel, Netlify, or AWS
- Add more features (watchlist, favorites, user reviews)
- Implement real movie database integration
- Add advanced filters and sorting
- Create mobile app with React Native

## License

This project is part of the Advanced Movie Recommendation System.
