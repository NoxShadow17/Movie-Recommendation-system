import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [activeTab, setActiveTab] = useState('personalized');
  const [mood, setMood] = useState('happy');
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const token = localStorage.getItem('token');

  const moods = [
    { label: 'happy', icon: 'fa-smile' },
    { label: 'sad', icon: 'fa-droplet' },
    { label: 'excited', icon: 'fa-bolt' },
    { label: 'relaxed', icon: 'fa-couch' },
    { label: 'thoughtful', icon: 'fa-brain' },
    { label: 'scared', icon: 'fa-ghost' },
  ];
  const LIMIT = 20;

  useEffect(() => {
    setRecommendations([]);
    setPage(0);
    setHasMore(true);
    fetchRecommendations(0, true);
  }, [activeTab, mood]);

  const fetchRecommendations = async (pageIndex = page, isReset = false) => {
    setLoading(true);
    try {
      const skip = pageIndex * LIMIT;
      let url = '';
      if (activeTab === 'personalized') {
        url = `http://localhost:8000/api/v1/recommendations/?limit=${LIMIT}&skip=${skip}`;
      } else if (activeTab === 'trending') {
        url = `http://localhost:8000/api/v1/recommendations/trending?limit=${LIMIT}&skip=${skip}`;
      } else if (activeTab === 'mood') {
        url = `http://localhost:8000/api/v1/recommendations/mood/${mood}?limit=${LIMIT}&skip=${skip}`;
      } else if (activeTab === 'friends') {
        url = `http://localhost:8000/api/v1/recommendations/friends?limit=${LIMIT}&skip=${skip}`;
      }

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          if (data.length < LIMIT) {
            setHasMore(false);
          }

          if (isReset) {
            setRecommendations(data);
          } else {
            setRecommendations(prev => [...prev, ...data]);
          }
        } else {
          setHasMore(false);
        }
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchRecommendations(nextPage, false);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white pb-24">
      {/* Cinematic Header */}
      <div className="relative pt-32 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-full bg-gradient-to-b from-indigo-500/10 to-transparent pointer-events-none"></div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex items-center gap-3 mb-6">
            <span className="bg-indigo-500/10 text-indigo-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-indigo-500/20">Synthesized Feed</span>
            <span className="text-gray-500 text-xs font-bold tracking-widest uppercase">Neural Recommendations</span>
          </div>

          <h1 className="text-6xl sm:text-8xl font-black text-white mb-12 tracking-tighter leading-none animate-fade-in">
            Calculated for <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-indigo-500">Your Identity.</span>
          </h1>

          {/* Futuristic Tabs */}
          <div className="flex flex-wrap gap-4 mb-8 bg-white/5 p-2 rounded-[2rem] w-fit border border-white/5 animate-fade-in [animation-delay:0.2s]">
            {['personalized', 'trending', 'mood', 'friends'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-8 py-3 rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${activeTab === tab
                  ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                  }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Mood Swatcher */}
          {activeTab === 'mood' && (
            <div className="animate-fade-in">
              <div className="flex flex-wrap gap-3">
                {moods.map(m => (
                  <button
                    key={m.label}
                    onClick={() => setMood(m.label)}
                    className={`px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 flex items-center gap-2 border ${mood === m.label
                      ? 'bg-purple-500 border-purple-400 text-white shadow-lg'
                      : 'bg-white/5 border-white/5 text-gray-500 hover:text-gray-300'
                      }`}
                  >
                    <i className={`fas ${m.icon}`}></i>
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {loading && recommendations.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-96 bg-white/5 animate-pulse rounded-[3rem] border border-white/5"></div>
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 animate-fade-in [animation-delay:0.3s]">
              {recommendations.map((rec, idx) => (
                <RecommendationCard key={idx} rec={rec} />
              ))}
            </div>

            {!loading && recommendations.length === 0 && (
              <div className="text-center py-32 glass-panel rounded-[4rem] border-white/5 max-w-2xl mx-auto">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-8">
                  <i className="fas fa-brain-circuit text-3xl text-gray-600"></i>
                </div>
                <h3 className="text-3xl font-black text-white mb-2">Neural Link Idle</h3>
                <p className="text-gray-500 font-light">Rate more cinematic units to initialize your personalized recommendation stream.</p>
              </div>
            )}

            {hasMore && recommendations.length > 0 && (
              <div className="mt-24 flex justify-center">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="group btn-cinematic px-12 py-5"
                >
                  <span className="flex items-center gap-3">
                    {loading ? 'Synthesizing...' : 'Expand Neural Stream'}
                    {!loading && <i className="fas fa-chevron-down group-hover:translate-y-1 transition-transform"></i>}
                  </span>
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function RecommendationCard({ rec }) {
  return (
    <Link
      to={`/movies/${rec.movie_id}`}
      className="group block h-full"
    >
      <div className="relative glass-panel rounded-[3rem] overflow-hidden border-white/5 h-full transition-all duration-700 hover:border-indigo-500/40 group-hover:-translate-y-3 shadow-2xl flex flex-col">
        <div className="relative h-56 overflow-hidden">
          {rec.poster_path ? (
            <img
              src={rec.poster_path.startsWith('/') ? `https://image.tmdb.org/t/p/w500${rec.poster_path}` : rec.poster_path}
              alt={rec.title}
              className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-70 group-hover:opacity-100"
            />
          ) : (
            <div className="w-full h-full bg-gray-900 flex items-center justify-center text-gray-700">
              <i className="fas fa-image text-4xl"></i>
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/20 to-transparent"></div>

          {/* Neural Match Badge */}
          <div className="absolute top-6 right-6">
            <div className="bg-black/60 backdrop-blur-xl border border-white/10 px-4 py-2 rounded-2xl shadow-xl">
              <p className="text-[8px] font-black text-indigo-400 uppercase tracking-widest leading-none mb-1 text-center">Neural Match</p>
              <p className="text-xl font-black text-white leading-none text-center">
                {Math.min(Math.round(rec.score * 100), 100)}%
              </p>
            </div>
          </div>

          {rec.friend_count > 0 && (
            <div className="absolute top-6 left-6 flex -space-x-3">
              {/* Use top_friends if available, otherwise fallback to mock counting array */}
              {(rec.top_friends && rec.top_friends.length > 0 ? rec.top_friends : [...Array(Math.min(rec.friend_count, 3))]).map((friend, i) => (
                <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 border-2 border-gray-950 flex items-center justify-center text-[10px] text-white font-black shadow-lg overflow-hidden relative group/avatar cursor-help" title={friend?.username || `Friend ${String.fromCharCode(65 + i)}`}>
                  {friend?.profile_picture ? (
                    <img
                      src={friend.profile_picture}
                      alt={friend.username}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span
                    className="absolute inset-0 flex items-center justify-center"
                    style={{ display: friend?.profile_picture ? 'none' : 'flex' }}
                  >
                    {friend?.username ? friend.username.charAt(0).toUpperCase() : String.fromCharCode(65 + i)}
                  </span>
                </div>
              ))}
              {rec.friend_count > (rec.top_friends ? rec.top_friends.length : 3) && (
                <div className="w-8 h-8 rounded-full bg-gray-800 border-2 border-gray-950 flex items-center justify-center text-[8px] text-gray-400 font-black shadow-lg">
                  +{rec.friend_count - (rec.top_friends ? rec.top_friends.length : 3)}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-8 flex flex-col flex-grow">
          <h3 className="text-2xl font-black text-white tracking-tighter mb-6 line-clamp-1 group-hover:text-indigo-400 transition-colors">
            {rec.title}
          </h3>

          <div className="mt-auto space-y-4">
            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-indigo-400 to-purple-600 shadow-[0_0_10px_rgba(99,102,241,0.5)] transition-all duration-1000"
                style={{ width: `${Math.min(rec.score * 100, 100)}%` }}
              ></div>
            </div>

            {rec.reason && (
              <div className="p-4 bg-black/40 rounded-2xl border border-white/5 transition-all group-hover:border-white/10">
                <p className="text-xs text-gray-500 italic leading-relaxed font-light">
                  <i className="fas fa-sparkles text-[10px] text-indigo-400 mr-2"></i>
                  {rec.reason}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
