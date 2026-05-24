import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import UpcomingMovies from '../components/UpcomingMovies';
import { API_BASE_URL } from '../config';

export default function DashboardPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [moodRecommendations, setMoodRecommendations] = useState([]);
  const [trending, setTrending] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMoodLoading, setIsMoodLoading] = useState(false);
  const [mood, setMood] = useState('Neutral');
  const [heroIndex, setHeroIndex] = useState(0);
  const token = localStorage.getItem('token');

  // Carousel timer: rotate every 8 seconds
  useEffect(() => {
    if (recommendations.length > 0) {
      const interval = setInterval(() => {
        setHeroIndex((prev) => (prev + 1) % Math.min(recommendations.length, 9));
      }, 8000);
      return () => clearInterval(interval);
    }
  }, [recommendations]);

  const moodOptions = [
    { label: 'Neutral', icon: 'fa-star', color: 'from-gray-600 to-gray-800', value: 'neutral' },
    { label: 'Happy', icon: 'fa-smile', color: 'from-yellow-400 to-orange-500', value: 'happy' },
    { label: 'Dark', icon: 'fa-ghost', color: 'from-purple-600 to-indigo-900', value: 'scared' },
    { label: 'Chill', icon: 'fa-couch', color: 'from-teal-400 to-blue-500', value: 'relaxed' },
    { label: 'Mind-bending', icon: 'fa-brain', color: 'from-pink-500 to-rose-700', value: 'thoughtful' },
  ];

  const fetchData = async () => {
    try {
      const [recResponse, trendingResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/recommendations/?limit=8`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/v1/recommendations/trending?limit=8`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (recResponse.ok) {
        const data = await recResponse.json();
        if (Array.isArray(data)) setRecommendations(data);
      }
      if (trendingResponse.ok) {
        const data = await trendingResponse.json();
        if (Array.isArray(data)) setTrending(data);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchWatchlist = async () => {
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

  const toggleQueue = async (movie) => {
    if (!movie) return;
    const movieId = movie.id || movie.movie_id;
    const isInQueue = watchlist.some(m => (m.id || m.movie_id) === movieId);

    const url = `${API_BASE_URL}/api/v1/users/${movieId}/${isInQueue ? 'remove-from-watchlist' : 'add-to-watchlist'}`;
    const method = isInQueue ? 'DELETE' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        // Optimistic UI update or refetch
        if (isInQueue) {
          setWatchlist(prev => prev.filter(m => (m.id || m.movie_id) !== movieId));
        } else {
          setWatchlist(prev => [...prev, movie.movie || movie]);
        }
      }
    } catch (err) {
      console.error('Error toggling queue:', err);
    }
  };

  const fetchMoodData = async (selectedMood) => {
    if (selectedMood === 'Neutral') {
      setMoodRecommendations([]);
      return;
    }

    const moodValue = moodOptions.find(m => m.label === selectedMood)?.value;
    if (!moodValue) return;

    setIsMoodLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/mood/${moodValue}?limit=8`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMoodRecommendations(data);
      }
    } catch (err) {
      console.error('Error fetching mood data:', err);
    } finally {
      setIsMoodLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchWatchlist();
  }, []);

  useEffect(() => {
    fetchMoodData(mood);
  }, [mood]);

  const featuredMovies = recommendations.length > 0 ? recommendations.slice(0, 9) : (trending.length > 0 ? trending.slice(0, 9) : []);
  const heroMovie = featuredMovies[heroIndex];


  return (
    <div className="min-h-screen pb-24">
      <div className="cinematic-overlay"></div>

      {/* Immersive Dynamic Hero Section */}
      <section className="relative h-[85vh] w-full flex items-center overflow-hidden border-b border-white/5">
        {heroMovie ? (
          <div key={heroMovie.movie_id} className="absolute inset-0 w-full h-full animate-fade-in transition-all duration-1000">
            <img
              src={`https://image.tmdb.org/t/p/original${heroMovie.poster_path}`}
              className="absolute inset-0 w-full h-full object-cover scale-110 blur-[2px] opacity-40 transition-transform duration-[12000ms] ease-out transform scale-125"
              alt=""
            />
            <div className="absolute inset-0 bg-gradient-to-r from-gray-950 via-gray-950/60 to-transparent"></div>
            <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent"></div>
          </div>
        ) : (
          <div className="absolute inset-0 bg-gray-900 animate-pulse"></div>
        )}

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20">
          <div className="max-w-3xl">
            {heroMovie && (
              <div key={heroMovie.movie_id} className="animate-fade-in">
                <div className="flex items-center gap-3 mb-6">
                  <div className="flex items-center gap-2 bg-indigo-500/20 border border-indigo-500/30 px-3 py-1 rounded-full shadow-[0_0_15px_rgba(99,102,241,0.2)]">
                    <i className="fas fa-shield-halved text-indigo-400 text-[10px]"></i>
                    <span className="text-white text-[9px] font-black uppercase tracking-widest">AI Verified</span>
                  </div>
                  <span className="bg-white/5 text-gray-400 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-[0.2em] border border-white/5">
                    Neural Match #{heroIndex + 1}
                  </span>
                </div>

                <h1 className="text-clamp-title font-black text-white mb-6 leading-[0.85] tracking-tighter">
                  {heroMovie.title}
                </h1>

                <p className="text-xl sm:text-2xl text-gray-400 font-light mb-4 line-clamp-3 leading-tight max-w-4xl tracking-tight">
                  {heroMovie.overview}
                </p>

                <p className="text-sm sm:text-base text-indigo-400/80 mb-10 leading-relaxed font-bold max-w-2xl italic border-l-2 border-indigo-500/40 pl-6 uppercase tracking-widest">
                  AI Logic: "{heroMovie.reason || `Handpicked ${heroMovie.movie?.genre?.split(',')[0] || 'Cinematic'} journey tailored for your neural profile.`}"
                </p>

                <div className="flex flex-wrap items-center gap-4">
                  <Link
                    to={`/movies/${heroMovie.movie_id}`}
                    className="btn-cinematic px-8 sm:px-12 flex items-center justify-center gap-3 group"
                  >
                    Experience Now
                    <i className="fas fa-sparkles text-[10px] transition-transform group-hover:rotate-45"></i>
                  </Link>
                  <button
                    onClick={() => toggleQueue(heroMovie)}
                    className={`px-8 py-4 rounded-2xl transition-all backdrop-blur-md flex-grow sm:flex-grow-0 group flex items-center justify-center gap-2 border ${watchlist.some(m => (m.id || m.movie_id) === (heroMovie.id || heroMovie.movie_id))
                      ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-400'
                      : 'bg-white/5 hover:bg-white/10 border-white/10 text-white'
                      }`}
                  >
                    <i className={`${watchlist.some(m => (m.id || m.movie_id) === (heroMovie.id || heroMovie.movie_id))
                      ? 'fas fa-check-circle'
                      : 'far fa-bookmark group-hover:fas'
                      } transition-all`}></i>
                    {watchlist.some(m => (m.id || m.movie_id) === (heroMovie.id || heroMovie.movie_id))
                      ? 'In Queue'
                      : 'Queue for Later'}
                  </button>
                </div>

                {/* Carousel Indicators */}
                <div className="flex gap-2 mt-12">
                  {featuredMovies.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setHeroIndex(i)}
                      className={`h-1.5 rounded-full transition-all duration-500 ${i === heroIndex ? 'w-12 bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]' : 'w-2 bg-white/10'}`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Floating Reason Badge - Desktop only */}
        {heroMovie && (
          <div key={`reason-${heroMovie.movie_id}`} className="absolute bottom-20 right-20 hidden lg:block animate-float animation-delay-500">
            <div className="glass-panel p-6 rounded-[2.5rem] border-white/10 max-w-[300px] shadow-2xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center">
                  <i className="fas fa-sparkles text-white text-xs"></i>
                </div>
                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">AI Intelligence</span>
              </div>
              <h4 className="text-white font-bold mb-2">Why this pick?</h4>
              <p className="text-sm text-gray-400 leading-relaxed italic">
                "{heroMovie.reason || `Matches your ${heroMovie.movie?.genre?.split(',')[0] || 'Cinematic'} interest.`}"
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Mood-Based Swatcher */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-30 mb-20 mt-10">
        <div className="glass-panel-mobile p-4 sm:p-8 shadow-2xl">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
            <div className="text-center lg:text-left">
              <h3 className="text-2xl font-black text-white mb-1">Set your Vibe.</h3>
              <p className="text-gray-500 text-sm italic">Adjusting recommendations in real-time</p>
            </div>
            <div className="flex flex-wrap lg:flex-nowrap items-center justify-center gap-3 p-2 bg-black/30 rounded-3xl lg:rounded-full border border-white/5 w-full lg:w-auto overflow-x-auto scroller-hide">
              {moodOptions.map(m => (
                <button
                  key={m.label}
                  onClick={() => setMood(m.label)}
                  className={`px-6 sm:px-8 py-3 rounded-2xl lg:rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-500 flex items-center gap-2 flex-shrink-0 ${mood === m.label
                    ? `bg-gradient-to-r ${m.color} text-white shadow-lg scale-105`
                    : 'text-gray-500 hover:text-gray-300'
                    }`}
                >
                  <i className={`fas ${m.icon}`}></i>
                  {m.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Trailer Sentiment Engine */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-24">
        <UpcomingMovies />
      </section>

      {/* Horizontal Carousels */}
      <div className="space-y-24">
        {/* Mood-Specific Recommendations (Vibe Discovery) */}
        {mood !== 'Neutral' && (
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in">
            <header className="flex items-end justify-between mb-10">
              <div>
                <h2 className="text-4xl font-black text-white tracking-tighter mb-2">
                  The <span className={`bg-clip-text text-transparent bg-gradient-to-r ${moodOptions.find(m => m.label === mood)?.color}`}>{mood}</span> Edit.
                </h2>
                <p className="text-gray-500 tracking-widest uppercase text-[10px] font-black">Filtered by your current vibe</p>
              </div>
              <button
                onClick={() => setMood('Neutral')}
                className="text-gray-500 hover:text-white text-xs font-bold uppercase tracking-widest transition-colors flex items-center gap-2"
              >
                <i className="fas fa-undo-alt"></i> Reset
              </button>
            </header>

            {isMoodLoading ? (
              <div className="flex gap-8 overflow-hidden">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="w-80 h-96 rounded-3xl bg-white/5 animate-pulse flex-shrink-0"></div>
                ))}
              </div>
            ) : moodRecommendations.length > 0 ? (
              <div className="flex overflow-x-auto pb-8 gap-8 scrollbar-hide snap-x">
                {moodRecommendations.map(movie => (
                  <div key={movie.movie_id} className="snap-start flex-shrink-0 w-80">
                    <MoviePreviewCard movie={movie} variant="mood" moodColor={moodOptions.find(m => m.label === mood)?.color} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-20 text-center glass-panel rounded-[3rem] border-dashed border-white/10">
                <i className="fas fa-film text-gray-700 text-4xl mb-4"></i>
                <p className="text-gray-500">No {mood} matches found in your immediate neural network.</p>
              </div>
            )}
          </section>
        )}

        {/* Personalized Picks */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <header className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-4xl font-black text-white tracking-tighter mb-2">Designed for <span className="text-indigo-400">You.</span></h2>
              <p className="text-gray-500 tracking-widest uppercase text-[10px] font-black">Neural Network Selections</p>
            </div>
            <Link to="/recommendations" className="text-gray-500 hover:text-indigo-400 text-sm font-bold uppercase tracking-widest transition-colors">
              Explore All
            </Link>
          </header>

          <div className="flex overflow-x-auto pb-8 gap-8 scrollbar-hide snap-x">
            {recommendations.map(movie => (
              <div key={movie.movie_id} className="snap-start flex-shrink-0 w-80">
                <MoviePreviewCard movie={movie} />
              </div>
            ))}
          </div>
        </section>

        {/* Trending */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
          <header className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-4xl font-black text-white tracking-tighter mb-2">Global <span className="text-pink-500">Momentum.</span></h2>
              <p className="text-gray-500 tracking-widest uppercase text-[10px] font-black">Real-time engagement analysis</p>
            </div>
          </header>

          <div className="flex overflow-x-auto pb-8 gap-8 scrollbar-hide snap-x">
            {trending.map(movie => (
              <div key={movie.movie_id} className="snap-start flex-shrink-0 w-80">
                <MoviePreviewCard movie={movie} variant="trending" />
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function MoviePreviewCard({ movie, variant, moodColor }) {
  const score = Math.round(movie.score * 100);

  return (
    <Link to={`/movies/${movie.movie_id}`} className="group block h-full">
      <div className={`relative glass-panel rounded-[2.5rem] overflow-hidden border-white/5 h-full transition-all duration-700 group-hover:-translate-y-2 shadow-xl ${variant === 'mood' ? `hover:border-transparent cursor-pointer` : 'hover:border-indigo-500/50'
        }`}
        style={variant === 'mood' ? {
          '--mood-glow': `var(--tw-gradient-stops)`,
          borderImage: `linear-gradient(to right, ${moodColor}) 1`
        } : {}}>
        {/* Using a simpler approach for the border glow to avoid border-image complexity */}
        <div className={`absolute inset-0 rounded-[2.5rem] transition-opacity duration-700 opacity-0 group-hover:opacity-100 pointer-events-none ${variant === 'mood' ? `bg-gradient-to-r ${moodColor} blur-xl opacity-10` : ''
          }`}></div>

        <div className={`relative z-10 h-full flex flex-col ${variant === 'mood' ? 'border-2 border-transparent' : 'border border-transparent'}`}>
          {/* Poster */}
          <div className="relative h-64 overflow-hidden">
            <img
              src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
              alt={movie.title}
              className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-70 group-hover:opacity-100"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent"></div>

            {/* Quick Badge */}
            <div className="absolute top-6 left-6 flex items-center gap-2">
              <div className={`w-10 h-10 rounded-xl backdrop-blur-xl border border-white/10 flex items-center justify-center font-black text-xs ${variant === 'trending' ? 'text-pink-500 bg-pink-500/10' :
                variant === 'mood' ? 'text-white bg-white/10' :
                  'text-indigo-400 bg-indigo-500/10'
                }`}>
                {score}%
              </div>
              <div className={`px-3 py-1 rounded-full backdrop-blur-md border border-white/10 text-[10px] font-black uppercase tracking-widest ${variant === 'mood' ? 'text-white bg-white/5' : 'text-gray-400 bg-black/60'
                }`}>
                {variant === 'trending' ? 'Hot' : variant === 'mood' ? 'Vibe Match' : 'Smart Pick'}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            <h3 className="text-xl font-bold text-white mb-2 line-clamp-1 group-hover:text-indigo-400 transition-colors">
              {movie.title}
            </h3>
            <p className="text-[10px] text-gray-500 mb-6 line-clamp-3 leading-relaxed font-medium uppercase tracking-[0.1em]">
              {movie.overview || (movie.movie?.overview) || "Deep narrative exploration awaits in this handpicked selection."}
            </p>

            <div className="flex items-center justify-between pt-4 border-t border-white/5">
              <span className="text-[10px] font-black uppercase tracking-widest text-gray-600">Cinema Grade</span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className={`w-1 h-1 rounded-full ${i <= 4 ? 'bg-indigo-500 shadow-[0_0_5px_rgba(99,102,241,0.5)]' : 'bg-gray-800'}`}></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
