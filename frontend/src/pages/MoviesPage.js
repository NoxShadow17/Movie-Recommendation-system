import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

const GENRES = [
  'All', 'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
  'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
  'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
  'TV Movie', 'Thriller', 'War', 'Western'
];

export default function MoviesPage() {
  const [movies, setMovies] = useState([]);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const token = localStorage.getItem('token');
  const limit = 24;

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    setPage(0);
    setMovies([]);
    setHasMore(true);
    setInitialLoading(true);
  }, [debouncedSearch, selectedGenres]);

  const fetchMovies = useCallback(async (pageNum) => {
    if (loading) return;
    setLoading(true);

    try {
      const skip = pageNum * limit;
      let url = `http://localhost:8000/api/v1/movies/?skip=${skip}&limit=${limit}`;

      if (debouncedSearch) {
        url += `&search=${encodeURIComponent(debouncedSearch)}`;
      }

      if (selectedGenres.length > 0) {
        url += `&genre=${encodeURIComponent(selectedGenres.join(','))}`;
      }

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          if (pageNum === 0) {
            setMovies(data);
          } else {
            setMovies(prev => [...prev, ...data]);
          }
          setHasMore(data.length === limit);
        }
      }
    } catch (err) {
      console.error('Error fetching movies:', err);
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  }, [debouncedSearch, selectedGenres, token]);

  useEffect(() => {
    fetchMovies(page);
  }, [page, fetchMovies]);

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      setPage(prev => prev + 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white pb-24">
      {/* Immersive Header */}
      <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-full bg-gradient-to-b from-indigo-500/10 via-transparent to-transparent pointer-events-none"></div>
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto relative z-10 text-center">
          <div className="flex justify-center mb-6">
            <span className="bg-indigo-500/10 text-indigo-400 px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.3em] border border-indigo-500/20">The Collective Library</span>
          </div>

          <h1 className="text-6xl sm:text-8xl font-black mb-12 tracking-tighter leading-none animate-fade-in">
            Everything <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-indigo-500">Ever Made.</span>
          </h1>

          {/* Futuristic Search */}
          <div className="max-w-3xl mx-auto relative group animate-fade-in [animation-delay:0.2s]">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-600/20 rounded-[2.5rem] blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-700"></div>
            <div className="relative glass-panel rounded-[2.5rem] border-white/5 overflow-hidden flex items-center px-8 transition-all hover:border-white/10 group-focus-within:border-indigo-500/50">
              <i className="fas fa-search text-gray-500 text-lg mr-6"></i>
              <input
                type="text"
                placeholder="Scan library for titles, directors, or genres..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full py-6 bg-transparent border-none focus:ring-0 text-xl font-light placeholder-gray-600 text-white"
              />
              {search && (
                <button onClick={() => setSearch('')} className="text-gray-500 hover:text-white transition-colors">
                  <i className="fas fa-times"></i>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Genre Selector */}
        <div className="mb-16 animate-fade-in [animation-delay:0.3s]">
          <div className="relative group">
            {/* Left Scroll Arrow */}
            <button
              onClick={() => {
                const container = document.getElementById('genre-scroll');
                container.scrollBy({ left: -300, behavior: 'smooth' });
              }}
              className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-indigo-500/80 backdrop-blur-sm border border-indigo-400/50 flex items-center justify-center text-white hover:bg-indigo-400 hover:border-indigo-300 transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
              </svg>
            </button>

            {/* Scrollable Container */}
            <div
              id="genre-scroll"
              className="overflow-x-auto scroller-hide py-4 px-16"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              <div className="flex gap-4 min-w-max justify-center">
                {/* Clear All Button */}
                {selectedGenres.length > 0 && (
                  <button
                    onClick={() => setSelectedGenres([])}
                    className="px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 border bg-red-500/20 border-red-500/40 text-red-400 hover:bg-red-500 hover:text-white hover:border-red-400 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
                  >
                    <i className="fas fa-times mr-2"></i>
                    Clear All
                  </button>
                )}

                {GENRES.filter(g => g !== 'All').map(genre => (
                  <button
                    key={genre}
                    onClick={() => {
                      setSelectedGenres(prev =>
                        prev.includes(genre)
                          ? prev.filter(g => g !== genre)
                          : [...prev, genre]
                      );
                    }}
                    className={`px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 border ${selectedGenres.includes(genre)
                      ? 'bg-indigo-500 border-indigo-400 text-white shadow-[0_0_30px_rgba(99,102,241,0.3)] scale-110'
                      : 'bg-white/5 border-white/5 text-gray-500 hover:text-gray-300 hover:border-white/10'
                      }`}
                  >
                    {genre}
                    {selectedGenres.includes(genre) && (
                      <i className="fas fa-check ml-2 text-[8px]"></i>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Right Scroll Arrow */}
            <button
              onClick={() => {
                const container = document.getElementById('genre-scroll');
                container.scrollBy({ left: 300, behavior: 'smooth' });
              }}
              className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-indigo-500/80 backdrop-blur-sm border border-indigo-400/50 flex items-center justify-center text-white hover:bg-indigo-400 hover:border-indigo-300 transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          </div>

          {/* Selected Genres Display */}
          {selectedGenres.length > 0 && (
            <div className="mt-6 text-center">
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Active Filters</p>
              <p className="text-sm text-indigo-400 font-bold">
                {selectedGenres.join(' + ')}
              </p>
            </div>
          )}
        </div>

        {initialLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="aspect-[2/3] bg-white/5 animate-pulse rounded-[3rem] border border-white/5"></div>
            ))}
          </div>
        ) : (
          <>
            <div className="flex justify-between items-end mb-12 animate-fade-in [animation-delay:0.4s]">
              <div>
                <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Results Manifest</h3>
                <p className="text-2xl font-black text-white">{movies.length} Units Indexed</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 animate-fade-in [animation-delay:0.5s]">
              {movies.map(movie => (
                <LibraryMovieCard key={movie.id} movie={movie} />
              ))}
            </div>

            {hasMore && (
              <div className="mt-24 flex justify-center animate-fade-in [animation-delay:0.6s]">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="group btn-cinematic px-12 py-5"
                >
                  <span className="flex items-center gap-3">
                    {loading ? 'Syncing...' : 'Load Additional Manifests'}
                    {!loading && <i className="fas fa-chevron-down group-hover:translate-y-1 transition-transform"></i>}
                  </span>
                </button>
              </div>
            )}

            {movies.length === 0 && !loading && (
              <div className="text-center py-32 glass-panel rounded-[4rem] border-white/5 max-w-2xl mx-auto">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-8">
                  <i className="fas fa-face-frown text-3xl text-gray-600"></i>
                </div>
                <h3 className="text-3xl font-black text-white mb-2">No Matching Patterns</h3>
                <p className="text-gray-500 font-light">Your search parameters did not yield any neural matches. Try broadening your criteria.</p>
                <button
                  onClick={() => { setSearch(''); setSelectedGenres([]); }}
                  className="mt-10 text-indigo-400 font-black uppercase text-[10px] tracking-widest hover:text-white transition-colors"
                >
                  Reset Search Filters
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function LibraryMovieCard({ movie }) {
  return (
    <Link to={`/movies/${movie.id}`} className="group block">
      <div className="relative aspect-[2/3] glass-panel rounded-[3rem] overflow-hidden border-white/5 transition-all duration-700 hover:border-indigo-500/40 group-hover:-translate-y-3 shadow-2xl">
        {/* Image */}
        <img
          src={movie.poster_path?.startsWith('/') ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : movie.poster_path}
          alt={movie.title}
          className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-70 group-hover:opacity-100"
        />

        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/20 to-transparent"></div>

        {/* Info */}
        <div className="absolute bottom-8 left-8 right-8">
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="bg-indigo-500 text-white text-[8px] font-black uppercase tracking-widest px-3 py-1 rounded-full">
              {movie.genre?.split(',')[0]}
            </span>
            <span className="bg-black/50 backdrop-blur-md text-[8px] font-black uppercase tracking-widest px-3 py-1 rounded-full text-gray-300">
              {new Date(movie.release_date).getFullYear()}
            </span>
          </div>
          <h3 className="text-2xl font-black text-white tracking-tighter mb-2 line-clamp-2 leading-none group-hover:text-indigo-400 transition-colors">
            {movie.title}
          </h3>
          <div className="flex items-center gap-1 text-yellow-500">
            <i className="fas fa-star text-[10px]"></i>
            <span className="text-xs font-black">{movie.vote_average?.toFixed(1) || '0.0'}</span>
          </div>
        </div>

        {/* Hover Reveal Details */}
        <div className="absolute inset-0 bg-indigo-600/10 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all duration-500 p-10 flex flex-col justify-center text-center pointer-events-none">
          <div className="border border-white/20 p-6 rounded-3xl">
            <h4 className="text-[10px] font-black text-white uppercase tracking-[0.3em] mb-4">Meta Analysis</h4>
            <p className="text-xs text-white/80 font-light leading-relaxed mb-6 line-clamp-4 italic">
              {movie.overview}
            </p>
            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Access Neural File</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
