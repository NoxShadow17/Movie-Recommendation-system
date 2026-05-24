import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

export default function MovieCard({ movie, token }) {
  const [rating, setRating] = useState(0);

  useEffect(() => {
    fetchUserRating();
  }, [token]);

  const fetchUserRating = async () => {
    if (!token) return;

    const userId = localStorage.getItem('user_id');
    if (!userId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/movies/${movie.id}/ratings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const ratings = await response.json();
        // Find the user's rating for this movie
        const userRating = ratings.find(r => r.user_id === parseInt(userId));

        if (userRating) {
          setRating(userRating.rating);
        }
      }
    } catch (err) {
      console.error('Error fetching user rating:', err);
    }
  };

  return (
    <div className="card p-4 overflow-hidden bg-gray-800 border border-gray-700 hover:border-indigo-500">
      <Link to={`/movies/${movie.id}`} className="block">
        <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-900 rounded-lg mb-4 overflow-hidden">
          {movie.poster_path ? (
            <img
              src={movie.poster_path.startsWith('/') ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : movie.poster_path}
              alt={movie.title}
              className="w-full h-full object-cover hover:scale-105 transition-transform"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-6xl">🎬</span>
            </div>
          )}
        </div>
      </Link>

      <Link to={`/movies/${movie.id}`}>
        <h3 className="text-white font-bold text-lg mb-2 line-clamp-2 hover:text-indigo-400 transition">
          {movie.title}
        </h3>
      </Link>

      <div className="flex gap-2 mb-3">
        <span className="inline-block bg-indigo-600 text-white text-xs px-2 py-1 rounded">
          {movie.genre}
        </span>
        {movie.release_date && (
          <span className="inline-block text-gray-400 text-xs">
            {new Date(movie.release_date).getFullYear()}
          </span>
        )}
      </div>

      <p className="text-gray-400 text-sm mb-4 line-clamp-2">{movie.overview}</p>

      {/* Ratings Section */}
      <div className="flex items-end justify-between mb-3">
        {/* Global Rating */}
        <div>
          <span className="text-gray-500 text-xs block mb-1">Global</span>
          <div className="flex items-center gap-1 bg-gray-700 rounded px-2 py-1" title={`Based on ${movie.vote_count} votes`}>
            <span className="text-yellow-400 text-xs">⭐</span>
            <span className="text-white text-xs font-bold">{movie.vote_average ? movie.vote_average.toFixed(1) : 'NR'}</span>
          </div>
        </div>

        {/* User Rating */}
        <div className="flex flex-col items-end">
          <span className="text-gray-500 text-xs uppercase tracking-wide mb-1">Your Rating</span>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <span
                key={star}
                className="text-lg leading-none"
                style={{
                  color: star <= rating ? '#fbbf24' : '#4b5563', // gold vs dark gray
                  textShadow: star <= rating ? '0 0 4px #fbbf24' : 'none'
                }}
              >
                {star <= rating ? '⭐' : '★'}
              </span>
            ))}
          </div>
        </div>
      </div>

      <Link
        to={`/movies/${movie.id}`}
        className="text-indigo-400 text-sm hover:text-indigo-300 transition"
      >
        View Details →
      </Link>
    </div>
  );
}
