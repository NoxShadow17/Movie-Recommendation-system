import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

export default function MovieDetailPage() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [rating, setRating] = useState(0);
  const [mood, setMood] = useState('RELAXED');
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [explanation, setExplanation] = useState(null);
  const token = localStorage.getItem('token');

  const moods = [
    { label: 'HAPPY', icon: 'fa-smile' },
    { label: 'SAD', icon: 'fa-droplet' },
    { label: 'EXCITED', icon: 'fa-bolt' },
    { label: 'RELAXED', icon: 'fa-couch' },
    { label: 'THOUGHTFUL', icon: 'fa-brain' },
    { label: 'SCARED', icon: 'fa-ghost' },
  ];

  useEffect(() => {
    fetchMovie();
    fetchUserRating();
    fetchWatchlist();
    fetchExplanation();
    window.scrollTo(0, 0);
  }, [id]);

  const fetchMovie = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/movies/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        if (data && typeof data === 'object' && !Array.isArray(data) && !data.detail) {
          setMovie(data);
        }
      }
    } catch (err) {
      console.error('Error fetching movie:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserRating = async () => {
    if (!token) return;
    const userId = localStorage.getItem('user_id');
    if (!userId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/movies/${id}/ratings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const ratings = await response.json();
        const userRating = ratings.find(r => r.user_id === parseInt(userId));
        if (userRating) {
          setRating(userRating.rating);
          setMood(userRating.mood || 'RELAXED');
        }
      }
    } catch (err) {
      console.error('Error fetching user rating:', err);
    }
  };

  const fetchWatchlist = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/watchlist`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWatchlist(data.watchlist || []);
      }
    } catch (err) {
      console.error('Error fetching watchlist:', err);
    }
  };

  const fetchExplanation = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/movies/${id}/explanation`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setExplanation(data);
      }
    } catch (err) {
      console.error('Error fetching explanation:', err);
    }
  };

  const toggleWatchlist = async () => {
    if (!movie) return;
    const movieId = movie.id;
    const isInWatchlist = watchlist.some(m => m.id === movieId);

    const url = `${API_BASE_URL}/api/v1/users/${movieId}/${isInWatchlist ? 'remove-from-watchlist' : 'add-to-watchlist'}`;
    const method = isInWatchlist ? 'DELETE' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        if (isInWatchlist) {
          setWatchlist(prev => prev.filter(m => m.id !== movieId));
        } else {
          setWatchlist(prev => [...prev, movie]);
        }
      }
    } catch (err) {
      console.error('Error toggling watchlist:', err);
    }
  };

  const handleRate = async () => {
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    try {
      await fetch(`${API_BASE_URL}/api/v1/movies/${id}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          movie_id: parseInt(id),
          rating,
          mood: mood || 'RELAXED'
        })
      });
      alert('Neural link updated. Your preference has been cached.');
      fetchUserRating();
    } catch (err) {
      console.error('Error rating movie:', err);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
    </div>
  );

  if (!movie) return (
    <div className="min-h-screen bg-gray-950 pt-32 px-4 text-center">
      <h2 className="text-3xl font-bold text-white mb-4">Transmission Lost</h2>
      <Link to="/" className="text-indigo-400 font-bold hover:underline">Return to Dashboard</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white pb-24">
      {/* Immersive Hero Backdrop */}
      <div className="relative h-[60vh] sm:h-[75vh] w-full overflow-hidden">
        <img
          src={movie.backdrop_path ? (movie.backdrop_path.startsWith('/') ? `https://image.tmdb.org/t/p/original${movie.backdrop_path}` : movie.backdrop_path) : (movie.poster_path?.startsWith('/') ? `https://image.tmdb.org/t/p/original${movie.poster_path}` : movie.poster_path)}
          alt={movie.title}
          className="w-full h-full object-cover scale-105 blur-[1px] opacity-40 animate-fade-in"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/40 to-transparent"></div>
        <div className="absolute inset-x-0 bottom-0 h-96 bg-gradient-to-t from-gray-950 to-transparent"></div>

        <div className="absolute inset-0 flex items-end">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 sm:pb-16 w-full">
            <div className="flex flex-col md:flex-row gap-8 sm:gap-12 items-center md:items-end text-center md:text-left">
              {/* Floating Poster - Hidden on very small screens or resized */}
              <div className="w-40 sm:w-64 lg:w-72 rounded-[2rem] sm:rounded-[3rem] overflow-hidden shadow-[0_30px_60px_rgba(0,0,0,0.8)] border border-white/10 flex-shrink-0 relative group animate-float">
                <img
                  src={movie.poster_path?.startsWith('/') ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : movie.poster_path}
                  alt={movie.title}
                  className="w-full h-auto transition-transform duration-700 group-hover:scale-110"
                />
              </div>

              {/* Title & Info */}
              <div className="flex-grow animate-fade-in [animation-delay:0.3s]">
                <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 sm:gap-4 mb-4 sm:mb-6">
                  {movie.genre?.split(',').slice(0, 2).map(g => (
                    <span key={g} className="bg-indigo-500/10 text-indigo-400 px-3 py-1 rounded-full text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] border border-indigo-500/20">{g.trim()}</span>
                  ))}
                  <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">{new Date(movie.release_date).getFullYear()}</span>
                </div>

                <h1 className="text-clamp-title font-black mb-4 sm:mb-8 tracking-tighter leading-[0.85] text-white">
                  {movie.title}
                </h1>

                <div className="flex flex-wrap gap-6 sm:gap-8 items-center justify-center md:justify-start border-t border-white/5 pt-6 sm:pt-8">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-yellow-500/10 border border-yellow-500/20 flex flex-col items-center justify-center">
                      <i className="fas fa-star text-yellow-500 text-[10px] mb-0.5"></i>
                      <span className="text-xs font-black text-white leading-none">{movie.vote_average ? movie.vote_average.toFixed(1) : 'NR'}</span>
                    </div>
                    <div className="text-left">
                      <p className="text-[9px] sm:text-[10px] font-black text-gray-500 uppercase tracking-widest leading-none mb-1">Sentiment</p>
                      <p className="text-[10px] sm:text-xs text-gray-400">{movie.vote_count} Neural Logs</p>
                    </div>
                  </div>

                  <div
                    onClick={toggleWatchlist}
                    className={`ml-auto flex items-center gap-4 px-5 py-2.5 rounded-2xl cursor-pointer transition-all duration-500 border group ${watchlist.some(m => m.id === movie.id)
                      ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.15)]'
                      : 'bg-white/5 border-white/10 text-gray-500 hover:text-white hover:bg-white/10'
                      }`}
                  >
                    <div className="flex flex-col items-end mr-1">
                      <p className="text-[8px] font-black uppercase tracking-[0.3em] leading-none mb-1 opacity-60">Neural Queue</p>
                      <p className="text-[10px] font-bold uppercase tracking-widest leading-none">
                        {watchlist.some(m => m.id === movie.id) ? 'Locked In' : 'Ready to Save'}
                      </p>
                    </div>
                    <div className={`w-10 h-5 rounded-full relative transition-all duration-500 overflow-hidden ${watchlist.some(m => m.id === movie.id) ? 'bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.4)]' : 'bg-gray-800'
                      }`}>
                      <div className={`absolute top-1 w-3 h-3 rounded-full bg-white transition-all duration-500 shadow-sm ${watchlist.some(m => m.id === movie.id) ? 'left-[23px]' : 'left-1'
                        }`}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
          {/* Synopsis & Details */}
          <div className="lg:col-span-2 space-y-16">
            <section className="animate-fade-in [animation-delay:0.5s]">
              <h2 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-6">Story Arc</h2>
              <p className="text-2xl text-gray-300 leading-relaxed font-light">
                {movie.overview}
              </p>
            </section>

            <section className="grid grid-cols-2 sm:grid-cols-4 gap-8">
              <div>
                <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-2">Director</h3>
                <p className="text-white font-bold">{movie.director || 'Classified'}</p>
              </div>
              <div>
                <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-2">Original Audio</h3>
                <p className="text-white font-bold">{movie.language || 'Multi-stream'}</p>
              </div>
              <div>
                <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-2">Production</h3>
                <p className="text-white font-bold">{movie.country || 'Global'}</p>
              </div>
            </section>

            <section>
              <h2 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-8">Cast Breakdown</h2>
              <div className="flex flex-wrap gap-4">
                {movie.cast?.split(',').slice(0, 8).map(person => (
                  <div key={person} className="px-6 py-3 bg-white/5 border border-white/5 rounded-2xl text-gray-300 font-bold hover:bg-white/10 transition-colors">
                    {person.trim()}
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* AI Intelligence Sidebar */}
          <div className="space-y-8 animate-fade-in [animation-delay:0.7s]">
            {/* Explainability Panel */}
            <div className="glass-panel-mobile shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 hidden sm:block">
                <i className="fas fa-microchip text-indigo-500/20 text-6xl"></i>
              </div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6 sm:mb-8">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                    <i className="fas fa-sparkles text-white text-sm"></i>
                  </div>
                  <h3 className="font-bold text-white tracking-tight text-xl">AI Logic Breakdown</h3>
                </div>

                <h4 className="text-gray-500 text-[10px] font-black uppercase tracking-widest mb-4">The Reason</h4>
                <p className="text-lg text-gray-300 italic mb-10 leading-relaxed font-light" dangerouslySetInnerHTML={{
                  __html: explanation?.reason || "CineAI is analyzing your neural profile to generate personalized insights..."
                }}>
                </p>

                <div className="p-6 bg-black/40 rounded-3xl border border-white/5">
                  <h5 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 text-center">Neural Preference</h5>
                  <div className="flex justify-around items-center">
                    <div className="text-center">
                      <p className="text-3xl font-black text-indigo-400">{explanation?.similarity || '0.00'}</p>
                      <p className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Similarity</p>
                    </div>
                    <div className="w-px h-8 bg-white/5"></div>
                    <div className="text-center group relative">
                      <p className="text-3xl font-black text-purple-400">{explanation?.latent_zone || 'V?'}</p>
                      <p className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Latent Zone</p>

                      {/* Tooltip */}
                      {explanation?.zone_description && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 border border-indigo-500/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-10">
                          <p className="text-xs text-indigo-300 font-bold">{explanation.zone_description}</p>
                          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Rating System */}
            <div className="glass-panel-mobile">
              <h3 className="text-xl font-bold text-white mb-8 px-2">Update Preference</h3>

              <div className="mb-10 px-2 text-center">
                <div className="flex justify-center gap-2 mb-4">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      className="transition-all duration-300 hover:scale-125"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill={star <= rating ? '#6366f1' : 'rgba(255,255,255,0.1)'}
                        className="w-10 h-10"
                        style={{
                          filter: star <= rating ? 'drop-shadow(0 0 8px rgba(99,102,241,0.6))' : 'none'
                        }}
                      >
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                      </svg>
                    </button>
                  ))}
                </div>
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Neural Intensity: {rating}/5</p>
              </div>

              <div className="mb-10">
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-6 text-center">Biological State (Mood)</h4>
                <div className="grid grid-cols-2 gap-3">
                  {moods.map(m => (
                    <button
                      key={m.label}
                      onClick={() => setMood(m.label)}
                      className={`px-4 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 flex items-center justify-center gap-2 border ${mood === m.label
                        ? 'bg-indigo-500 border-indigo-400 text-white shadow-lg'
                        : 'bg-white/5 border-white/5 text-gray-500 hover:text-gray-300'
                        }`}
                    >
                      <i className={`fas ${m.icon}`}></i>
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleRate}
                className="w-full btn-cinematic py-4"
                disabled={rating === 0}
              >
                Sync Neural Preference
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
