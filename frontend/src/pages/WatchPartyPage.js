import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const WatchPartyPage = () => {
    const [friends, setFriends] = useState([]);
    const [selectedFriends, setSelectedFriends] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchFriends();
        window.scrollTo(0, 0);
    }, []);

    const fetchFriends = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/friends/list`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setFriends(data);
            }
        } catch (error) {
            console.error('Error fetching friends:', error);
        }
    };

    const toggleFriend = (friendId) => {
        setSelectedFriends(prev =>
            prev.includes(friendId)
                ? prev.filter(id => id !== friendId)
                : prev.length < 4 ? [...prev, friendId] : prev
        );
    };

    const findMatch = async () => {
        if (selectedFriends.length === 0) return;

        setSearching(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/watch-party`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ user_ids: selectedFriends })
            });

            if (response.ok) {
                const data = await response.json();
                setRecommendations(data);
            }
        } catch (error) {
            console.error('Error finding group match:', error);
        } finally {
            setSearching(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 text-white pb-24">
            {/* Cinematic Header */}
            <div className="relative pt-32 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden text-center">
                <div className="absolute top-0 left-0 right-0 h-full bg-gradient-to-b from-purple-500/10 to-transparent pointer-events-none"></div>

                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="flex justify-center mb-6">
                        <span className="bg-purple-500/10 text-purple-400 px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.3em] border border-purple-500/20">Collective Intelligence</span>
                    </div>

                    <h1 className="text-6xl sm:text-8xl font-black mb-12 tracking-tighter leading-none animate-fade-in">
                        Neural <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-purple-500">Watch Party.</span>
                    </h1>

                    <p className="text-xl text-gray-500 max-w-2xl mx-auto font-light leading-relaxed animate-fade-in [animation-delay:0.2s]">
                        Terminate the group selection paradox. Our AI synthesizes the latent preferences of up to 4 individuals to calculate the mathematical optimum for your viewing session.
                    </p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    {/* Neural Input Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="glass-panel p-10 rounded-[3rem] border-white/5 sticky top-32 animate-fade-in [animation-delay:0.3s]">
                            <h2 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-10">Neural Node Selection</h2>

                            <div className="space-y-4 mb-10 max-h-[400px] overflow-y-auto scroller-hide">
                                {friends.length === 0 ? (
                                    <div className="py-12 text-center bg-white/5 rounded-3xl border border-dashed border-white/10">
                                        <p className="text-gray-500 text-xs font-black uppercase tracking-widest">No Node Detected</p>
                                        <Link to="/friends" className="text-indigo-400 text-[10px] mt-4 inline-block hover:underline font-black uppercase tracking-[0.2em]">Initialize Network</Link>
                                    </div>
                                ) : (
                                    friends.map(friend => (
                                        <div
                                            key={friend.id}
                                            onClick={() => toggleFriend(friend.id)}
                                            className={`flex items-center gap-6 p-4 rounded-2xl cursor-pointer transition-all duration-500 border ${selectedFriends.includes(friend.id)
                                                ? 'bg-indigo-500/20 border-indigo-500/50 scale-[1.05]'
                                                : 'bg-white/5 border-white/5 hover:border-white/20'
                                                }`}
                                        >
                                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-xl shadow-lg border border-white/10">
                                                {friend.username[0].toUpperCase()}
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-white font-bold tracking-tight">{friend.username}</p>
                                                <p className="text-gray-500 text-[8px] font-black uppercase tracking-widest">Active Node</p>
                                            </div>
                                            {selectedFriends.includes(friend.id) && (
                                                <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-[10px] text-white shadow-xl animate-fade-in">
                                                    <i className="fas fa-check"></i>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>

                            <button
                                onClick={findMatch}
                                disabled={selectedFriends.length === 0 || searching}
                                className={`w-full py-6 rounded-3xl font-black uppercase tracking-[0.3em] text-[10px] flex items-center justify-center gap-4 transition-all duration-700 shadow-2xl ${selectedFriends.length > 0 && !searching
                                    ? 'bg-indigo-500 text-white shadow-indigo-500/30 hover:scale-105 active:scale-95'
                                    : 'bg-white/5 text-gray-500 cursor-not-allowed border border-white/5'
                                    }`}
                            >
                                {searching ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        Processing Tastes...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-wand-magic-sparkles text-lg"></i>
                                        Synthesize Collective Best
                                    </>
                                )}
                            </button>

                            <p className="mt-6 text-center text-[9px] font-black text-gray-600 uppercase tracking-widest leading-loose">
                                Selected: {selectedFriends.length}/4 Nodes Active
                            </p>
                        </div>
                    </div>

                    {/* Meta-Results Area */}
                    <div className="lg:col-span-2">
                        {!recommendations.length && !searching ? (
                            <div className="glass-panel border-white/5 rounded-[4rem] p-24 flex flex-col items-center justify-center text-center animate-fade-in [animation-delay:0.4s]">
                                <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center text-4xl text-gray-700 mb-10 shadow-inner">
                                    <i className="fas fa-brain-circuit"></i>
                                </div>
                                <h3 className="text-3xl font-black text-white mb-4 tracking-tighter">Manifest Idle</h3>
                                <p className="text-gray-500 font-light max-w-sm leading-relaxed">The collective brain is waiting for input. Select active nodes from the sidebar to beginTaste DNA synthesis.</p>
                            </div>
                        ) : searching ? (
                            <div className="space-y-12">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="h-64 bg-white/5 animate-pulse rounded-[3rem] border border-white/5"></div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-12 animate-fade-in">
                                <header className="flex items-center justify-between mb-8 px-4">
                                    <div>
                                        <h3 className="text-[10px] font-black text-purple-400 uppercase tracking-[0.3em] mb-1">Synthesis Result</h3>
                                        <h2 className="text-4xl font-black text-white tracking-tighter">Optimized Matches</h2>
                                    </div>
                                    <span className="bg-purple-500 text-white px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg animate-pulse">
                                        Collective Intelligence Active
                                    </span>
                                </header>

                                {recommendations.map((rec, index) => (
                                    <Link
                                        key={index}
                                        to={`/movies/${rec.movie_id}`}
                                        className="group block"
                                    >
                                        <div className="relative glass-panel rounded-[3rem] p-10 border-white/5 transition-all duration-700 hover:border-purple-500/50 group-hover:-translate-y-3 shadow-2xl overflow-hidden flex flex-col md:flex-row gap-12">
                                            <div className="absolute top-0 right-0 p-8 text-white/5 text-8xl font-black pointer-events-none tracking-tighter">#{index + 1}</div>

                                            <div className="w-full md:w-56 h-80 md:h-auto rounded-[2.5rem] overflow-hidden flex-shrink-0 shadow-2xl border border-white/10 relative group-hover:border-purple-500/30 transition-colors">
                                                <img
                                                    src={rec.poster_path ? `https://image.tmdb.org/t/p/w500${rec.poster_path}` : 'https://via.placeholder.com/500x750?text=Manifest+Missing'}
                                                    alt={rec.title}
                                                    className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-80 group-hover:opacity-100"
                                                />
                                            </div>

                                            <div className="flex-1 flex flex-col justify-center py-4">
                                                <div className="flex items-start justify-between mb-8">
                                                    <div>
                                                        <h3 className="text-4xl font-black text-white group-hover:text-purple-400 transition-colors tracking-tighter leading-none mb-3">{rec.title}</h3>
                                                        <div className="flex flex-wrap gap-2">
                                                            {rec.movie.genre.split(',').slice(0, 3).map(g => (
                                                                <span key={g} className="text-[8px] font-black uppercase tracking-widest text-purple-400/80 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20">
                                                                    {g.trim()}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col items-center justify-center w-16 h-16 rounded-2xl bg-white/5 border border-white/5">
                                                        <span className="text-xl font-black text-white">{rec.movie.vote_average?.toFixed(1) || '0.0'}</span>
                                                        <span className="text-[7px] font-black uppercase text-gray-600 tracking-widest">Global</span>
                                                    </div>
                                                </div>

                                                <div className="bg-black/40 p-6 rounded-3xl border border-white/5 transition-all group-hover:border-white/10 mb-8 border-l-4 border-l-purple-500">
                                                    <p className="text-xs text-gray-400 font-light leading-relaxed italic">
                                                        <i className="fas fa-sparkles text-[10px] text-purple-400 mr-2"></i>
                                                        {rec.reason}
                                                    </p>
                                                </div>

                                                <button className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400 group-hover:text-white transition-colors">
                                                    Initialize Neural File <i className="fas fa-arrow-right text-[8px] group-hover:translate-x-2 transition-transform"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WatchPartyPage;
