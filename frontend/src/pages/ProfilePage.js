import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import EditProfileModal from '../components/EditProfileModal';

export default function ProfilePage({ user, onLogout }) {
  const navigate = useNavigate();
  const [ratings, setRatings] = useState([]);
  const [preferences, setPreferences] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [watchlistPage, setWatchlistPage] = useState(1);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const ratingsPerPage = 12;
  const watchlistPerPage = 8;
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchUserData();
    if (window.location.hash === '#watchlist') {
      setTimeout(() => {
        const element = document.getElementById('watchlist');
        if (element) element.scrollIntoView({ behavior: 'smooth' });
      }, 500);
    } else {
      window.scrollTo(0, 0);
    }
  }, []);

  const fetchUserData = async () => {
    try {
      const ratingsResponse = await fetch('http://localhost:8000/api/v1/users/me/ratings', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const preferencesResponse = await fetch('http://localhost:8000/api/v1/users/me/preferences/detailed', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const watchlistResponse = await fetch('http://localhost:8000/api/v1/users/me/watchlist', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (ratingsResponse.ok) {
        const ratingsData = await ratingsResponse.json();
        if (Array.isArray(ratingsData)) {
          const formattedRatings = ratingsData.map(rating => ({
            id: rating.movie_id,
            title: rating.movie_title,
            genre: rating.movie_genre,
            userRating: rating.rating,
            userMood: rating.mood
          }));
          setRatings(formattedRatings);
        }
      }

      if (preferencesResponse.ok) {
        const preferencesData = await preferencesResponse.json();
        setPreferences(preferencesData);
      }

      if (watchlistResponse.ok) {
        const watchlistData = await watchlistResponse.json();
        setWatchlist(watchlistData.watchlist || []);
      }
    } catch (err) {
      console.error('Error fetching user data:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(ratings.length / ratingsPerPage);
  const indexOfLastRating = currentPage * ratingsPerPage;
  const indexOfFirstRating = indexOfLastRating - ratingsPerPage;
  const currentRatings = ratings.slice(indexOfFirstRating, indexOfLastRating);

  const totalWatchlistPages = Math.ceil(watchlist.length / watchlistPerPage);
  const indexOfLastWatchlist = watchlistPage * watchlistPerPage;
  const indexOfFirstWatchlist = indexOfLastWatchlist - watchlistPerPage;
  const currentWatchlist = watchlist.slice(indexOfFirstWatchlist, indexOfLastWatchlist);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 pt-32 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto mb-6"></div>
          <p className="text-indigo-400 font-black uppercase tracking-[0.3em] animate-pulse">Synchronizing Neural Profile</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white pb-24">
      {/* Profile Hero Header */}
      <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-full bg-gradient-to-b from-indigo-500/10 via-transparent to-transparent pointer-events-none"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.05),transparent_70%)] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col md:flex-row items-center md:items-end gap-12">
            {/* Visual Avatar */}
            <div className="relative group">
              <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/20 to-purple-600/20 rounded-full blur-2xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative w-40 h-40 sm:w-56 sm:h-56 rounded-full glass-panel border-white/10 flex items-center justify-center shadow-2xl overflow-hidden">
                {user?.profile_picture ? (
                  <img
                    src={user.profile_picture}
                    alt={user.username}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                ) : null}
                <span
                  className="text-7xl sm:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-indigo-200 to-indigo-500 absolute inset-0 flex items-center justify-center"
                  style={{ display: user?.profile_picture ? 'none' : 'flex' }}
                >
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
                <div className="absolute bottom-0 left-0 right-0 bg-white/5 backdrop-blur-md py-4 text-center border-t border-white/5">
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">User Verified</span>
                </div>
              </div>
            </div>

            <div className="text-center md:text-left flex-grow">
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mb-6">
                <span className="bg-indigo-500/10 text-indigo-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-indigo-500/20">System ID: {user?.id}</span>
                <span className="bg-white/5 text-gray-500 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-white/10">Member since {new Date(user?.created_at).getFullYear()}</span>
              </div>
              <h1 className="text-5xl sm:text-7xl font-black text-white mb-4 tracking-tighter leading-none animate-fade-in">
                {user?.full_name || user?.username}
              </h1>
              <p className="text-xl text-gray-500 font-light max-w-xl animate-fade-in [animation-delay:0.2s] mb-6">
                Cinematic Identity {preferences?.insights?.diversity_score > 70 ? 'Visionary' : 'Purist'}. Mapping neural pathways through {ratings.length} analyzed productions.
              </p>

              {user?.bio && (
                <div className="bg-white/5 border border-white/5 rounded-2xl p-6 max-w-xl animate-fade-in [animation-delay:0.3s]">
                  <p className="text-indigo-400 text-[10px] font-black uppercase tracking-widest mb-2">Neural Bio</p>
                  <p className="text-gray-300 italic font-light leading-relaxed">"{user.bio}"</p>
                </div>
              )}

              <div className="mt-10 flex flex-wrap gap-4 justify-center md:justify-start animate-fade-in [animation-delay:0.4s]">
                <button
                  onClick={() => setIsEditModalOpen(true)}
                  className="px-8 py-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all"
                >
                  Edit Profile
                </button>
                <button onClick={onLogout} className="px-8 py-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-red-500 hover:text-white transition-all">
                  Terminate Session
                </button>
              </div>

              <EditProfileModal
                user={user}
                isOpen={isEditModalOpen}
                onClose={() => setIsEditModalOpen(false)}
                onUpdate={(updatedUser) => {
                  // Reload page to reflect changes since user prop comes from parent
                  window.location.reload();
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Core Analytics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mb-24">
          {/* Taste DNA (Genres) */}
          <div className="lg:col-span-2 glass-panel p-10 rounded-[3rem] border-white/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 text-indigo-500/10 text-9xl font-black pointer-events-none">DNA</div>
            <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-12">Taste DNA: Genre Distribution</h3>

            {preferences?.genres?.length > 0 ? (
              <div className="space-y-8">
                {preferences.genres.slice(0, 6).map((genre, idx) => (
                  <div key={idx} className="relative group/item">
                    <div className="flex justify-between items-end mb-3">
                      <span className="text-xl font-bold text-white tracking-tight">{genre.genre}</span>
                      <span className="text-xs font-black text-indigo-400 uppercase tracking-widest">{Math.round(genre.score)}% Resonance</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 via-indigo-400 to-indigo-600 rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(99,102,241,0.3)]"
                        style={{ width: `${Math.min((genre.score / 60) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-gray-500">
                Insufficient data to map DNA. Initialize by rating units.
              </div>
            )}
          </div>

          {/* Neural Insights */}
          <div className="space-y-8">
            <div className="glass-panel p-10 rounded-[3rem] border-white/5 bg-gradient-to-br from-white/5 to-transparent">
              <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-8">Neural Consistency</h3>
              <div className="flex items-center gap-8">
                <div className="relative w-24 h-24">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" className="stroke-white/5" strokeWidth="3"></circle>
                    <circle cx="18" cy="18" r="16" fill="none" className="stroke-indigo-500 shadow-xl" strokeWidth="3"
                      strokeDasharray={`${Math.round((preferences?.insights?.rating_patterns?.consistency || 0) * 100)}, 100`}>
                    </circle>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center font-black text-xl">
                    {Math.round((preferences?.insights?.rating_patterns?.consistency || 0) * 100)}%
                  </div>
                </div>
                <div>
                  <p className="text-white font-bold leading-tight mb-1">Pattern Stability</p>
                  <p className="text-xs text-gray-500 font-light">Your rating logic is {preferences?.insights?.rating_patterns?.consistency > 0.7 ? 'highly predictable' : 'eclectic'}.</p>
                </div>
              </div>
            </div>

            <div className="glass-panel p-10 rounded-[3rem] border-white/5">
              <h3 className="text-[10px] font-black text-pink-400 uppercase tracking-[0.3em] mb-8">Diversity Quotient</h3>
              <div className="space-y-4">
                <div className="flex justify-between mb-2">
                  <span className="text-xs font-black text-gray-400 uppercase tracking-widest">Global Exposure</span>
                  <span className="text-xs font-black text-white">{preferences?.insights?.diversity_score || 0}/100</span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-pink-500 to-indigo-500"
                    style={{ width: `${preferences?.insights?.diversity_score || 0}%` }}
                  ></div>
                </div>
                <p className="text-[10px] text-gray-600 font-light leading-relaxed italic">
                  Calculated based on your interaction with non-mainstream genres and foreign productions.
                </p>
              </div>
            </div>

            <div className="glass-panel p-10 rounded-[3rem] border-white/5 bg-indigo-500">
              <p className="text-[10px] font-black text-white/50 uppercase tracking-[0.3em] mb-2">Neural Balance</p>
              <p className="text-2xl font-black text-white leading-tight">
                Rating Style: <span className="opacity-70">{preferences?.insights?.rating_patterns?.rating_style || 'Calibrating...'}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Global Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-24">
          {[
            { label: 'Total Syncs', value: ratings.length, icon: 'fa-star', color: 'text-indigo-400' },
            { label: 'Avg Feedback', value: preferences?.stats?.average_rating?.toFixed(1) || '0.0', icon: 'fa-chart-simple', color: 'text-purple-400' },
            { label: 'Primary Genre', value: preferences?.stats?.favorite_genre || 'N/A', icon: 'fa-masks-theater', color: 'text-pink-400' },
            { label: 'Dominant Mood', value: preferences?.stats?.favorite_mood || 'N/A', icon: 'fa-face-smile', color: 'text-yellow-400' },
          ].map((stat, i) => (
            <div key={i} className="glass-panel p-8 rounded-[2.5rem] border-white/5 text-center group transition-all hover:bg-white/5">
              <i className={`fas ${stat.icon} ${stat.color} text-2xl mb-4`}></i>
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">{stat.label}</p>
              <p className="text-3xl font-black text-white tracking-tighter">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Neural Queue (Watchlist) */}
        <section id="watchlist" className="mb-24 animate-fade-in">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-1">Mission Log</h3>
              <h2 className="text-4xl font-black text-white tracking-tighter">Neural Queue</h2>
            </div>
          </div>

          {watchlist.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                {currentWatchlist.map((movie, idx) => (
                  <div key={idx} className="group relative">
                    <div className="absolute -inset-2 bg-gradient-to-r from-indigo-500/0 to-purple-600/0 rounded-[2.5rem] blur-xl group-hover:from-indigo-500/10 group-hover:to-purple-600/10 transition-all duration-700"></div>
                    <div className="relative glass-panel rounded-[2rem] overflow-hidden border-white/5 h-full transition-all duration-700 hover:-translate-y-2 hover:border-indigo-500/50">
                      <div className="relative h-48 overflow-hidden">
                        <img
                          src={movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 'https://via.placeholder.com/500x750?text=No+Poster'}
                          alt={movie.title}
                          className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-70 group-hover:opacity-100"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent"></div>
                        <button
                          onClick={async (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            try {
                              const response = await fetch(`http://localhost:8000/api/v1/users/${movie.id}/remove-from-watchlist`, {
                                method: 'DELETE',
                                headers: { 'Authorization': `Bearer ${token}` }
                              });
                              if (response.ok) {
                                setWatchlist(prev => prev.filter(m => m.id !== movie.id));
                                // If last item on page removed, go back a page
                                if (currentWatchlist.length === 1 && watchlistPage > 1) {
                                  setWatchlistPage(prev => prev - 1);
                                }
                              }
                            } catch (err) {
                              console.error('Error removing from watchlist:', err);
                            }
                          }}
                          className="absolute top-4 right-4 w-10 h-10 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-center text-red-500 hover:bg-red-500 hover:text-white transition-all z-20"
                        >
                          <i className="fas fa-trash-can text-xs"></i>
                        </button>
                      </div>
                      <div className="p-6">
                        <h3 className="text-lg font-bold text-white mb-2 line-clamp-1 group-hover:text-indigo-400 transition-colors uppercase tracking-tight">{movie.title}</h3>
                        <button
                          onClick={() => navigate(`/movies/${movie.id}`)}
                          className="mt-4 w-full py-3 bg-white/5 hover:bg-indigo-500 text-white rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all border border-white/5 hover:border-indigo-400"
                        >
                          Load Mission
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Watchlist Pagination */}
              {totalWatchlistPages > 1 && (
                <div className="mt-12 flex justify-center items-center gap-8">
                  <button
                    onClick={() => setWatchlistPage(prev => Math.max(1, prev - 1))}
                    disabled={watchlistPage === 1}
                    className="w-12 h-12 rounded-full glass-panel flex items-center justify-center hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none transition-all"
                  >
                    <i className="fas fa-chevron-left"></i>
                  </button>
                  <div className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">
                    Archive <span className="text-white">{watchlistPage}</span> of {totalWatchlistPages}
                  </div>
                  <button
                    onClick={() => setWatchlistPage(prev => Math.min(totalWatchlistPages, prev + 1))}
                    disabled={watchlistPage === totalWatchlistPages}
                    className="w-12 h-12 rounded-full glass-panel flex items-center justify-center hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none transition-all"
                  >
                    <i className="fas fa-chevron-right"></i>
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-20 glass-panel rounded-[3rem] border-white/5 bg-white/5 border-dashed border-2">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-6 text-gray-600">
                <i className="far fa-bookmark text-2xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-400 mb-2 uppercase tracking-widest">Queue Status: Idle</h3>
              <p className="text-xs text-gray-500 font-light max-w-xs mx-auto">No pending cinematic missions. Initialize queue by marking productions for later.</p>
            </div>
          )}
        </section>

        {/* Chronological Log (Ratings) */}
        <section className="mb-24">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-1">Chronological Manifest</h3>
              <h2 className="text-4xl font-black text-white tracking-tighter">Interaction History</h2>
            </div>
          </div>

          {ratings.length > 0 ? (
            <div className="overflow-x-auto scroller-hide">
              <table className="w-full text-left border-separate border-spacing-y-4">
                <thead>
                  <tr className="text-[10px] font-black text-gray-600 uppercase tracking-widest">
                    <th className="px-8 pb-4">Production Unit</th>
                    <th className="px-8 pb-4">Classification</th>
                    <th className="px-8 pb-4">Neural Feedback</th>
                    <th className="px-8 pb-4">Recorded Mood</th>
                    <th className="px-8 pb-4 text-right">Access</th>
                  </tr>
                </thead>
                <tbody>
                  {currentRatings.map((movie, idx) => (
                    <tr key={idx} className="glass-panel group hover:bg-white/5 transition-all">
                      <td className="px-8 py-6 rounded-l-[2rem] border-r border-white/5">
                        <p className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-1">{movie.title}</p>
                      </td>
                      <td className="px-8 py-6 border-r border-white/5">
                        <span className="text-xs text-gray-500 font-medium">{movie.genre}</span>
                      </td>
                      <td className="px-8 py-6 border-r border-white/5">
                        <div className="flex items-center gap-2">
                          {[...Array(5)].map((_, i) => (
                            <div key={i} className={`w-2 h-2 rounded-full ${i < movie.userRating ? 'bg-indigo-500' : 'bg-white/5'}`}></div>
                          ))}
                          <span className="text-xs font-black text-white ml-2">{movie.userRating}/5</span>
                        </div>
                      </td>
                      <td className="px-8 py-6 border-r border-white/5">
                        <span className="bg-white/5 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest text-indigo-300">
                          {movie.userMood || 'Neutral'}
                        </span>
                      </td>
                      <td className="px-8 py-6 rounded-r-[2rem] text-right">
                        <button
                          onClick={() => navigate(`/movies/${movie.id}`)}
                          className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-indigo-500 transition-colors group/btn"
                        >
                          <i className="fas fa-arrow-right text-[10px] group-hover/btn:translate-x-1 transition-transform"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-32 glass-panel rounded-[4rem] border-white/5 max-w-2xl mx-auto">
              <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-8 text-gray-700">
                <i className="fas fa-box-open text-3xl"></i>
              </div>
              <h3 className="text-3xl font-black text-white mb-2">History Manifest Empty</h3>
              <p className="text-gray-500 font-light">The archive is empty. Begin synchronization by engaging with cinematic units.</p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-12 flex justify-center items-center gap-8">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="w-12 h-12 rounded-full glass-panel flex items-center justify-center hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none transition-all"
              >
                <i className="fas fa-chevron-left"></i>
              </button>
              <div className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">
                Sector <span className="text-white">{currentPage}</span> of {totalPages}
              </div>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="w-12 h-12 rounded-full glass-panel flex items-center justify-center hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none transition-all"
              >
                <i className="fas fa-chevron-right"></i>
              </button>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
