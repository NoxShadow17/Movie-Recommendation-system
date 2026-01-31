import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function UserProfilePage() {
    const { userId } = useParams();
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [friends, setFriends] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const token = localStorage.getItem('token');
    const currentUserId = parseInt(localStorage.getItem('user_id'));

    useEffect(() => {
        // If trying to view own profile, redirect to /profile
        if (userId && currentUserId && parseInt(userId) === currentUserId) {
            navigate('/profile');
            return;
        }

        fetchUserData();
    }, [userId, token]);

    const fetchUserData = async () => {
        try {
            setLoading(true);
            setError('');

            const response = await fetch(`http://localhost:8000/api/v1/users/${userId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) {
                throw new Error('User not found');
            }

            const userData = await response.json();
            setUser(userData);

            // Fetch friends list to check common connections or just context
            // Implementing basic fetch for now
            const friendsRes = await fetch(`http://localhost:8000/api/v1/users/${userId}/friends`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (friendsRes.ok) {
                setFriends(await friendsRes.json());
            }

        } catch (err) {
            console.error('Error fetching user profile:', err);
            setError('Failed to load user profile');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-950 pt-32 px-4 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto mb-6"></div>
                    <p className="text-indigo-400 font-black uppercase tracking-[0.3em] animate-pulse">Scanning Neural ID...</p>
                </div>
            </div>
        );
    }

    if (error || !user) {
        return (
            <div className="min-h-screen bg-gray-950 pt-32 px-4 flex items-center justify-center text-center">
                <div>
                    <h2 className="text-2xl font-bold text-red-500 mb-2">Access Denied</h2>
                    <p className="text-gray-400">{error || 'User not found in the network.'}</p>
                    <button onClick={() => navigate('/friends')} className="mt-6 px-6 py-2 bg-gray-800 rounded-full text-white hover:bg-gray-700">Back to Network</button>
                </div>
            </div>
        );
    }

    // Determine if full access is granted (based on backend redaction)
    const isFullAccess = user.profile_picture !== null || user.bio !== null;

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
                            <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/20 to-purple-600/20 rounded-full blur-2xl opacity-50 transition-opacity"></div>
                            <div className="relative w-40 h-40 sm:w-56 sm:h-56 rounded-full glass-panel border-white/10 flex items-center justify-center shadow-2xl overflow-hidden">
                                {user.profile_picture ? (
                                    <img
                                        src={user.profile_picture}
                                        alt={user.username}
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            e.target.nextSibling.style.display = 'flex';
                                        }}
                                    />
                                ) : null}

                                <span
                                    className={`text-7xl sm:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-indigo-200 to-indigo-500 absolute inset-0 flex items-center justify-center`}
                                    style={{ display: user.profile_picture ? 'none' : 'flex' }}
                                >
                                    {isFullAccess ? user.username.charAt(0).toUpperCase() : <i className="fas fa-lock text-5xl opacity-50"></i>}
                                </span>

                                <div className="absolute bottom-0 left-0 right-0 bg-white/5 backdrop-blur-md py-4 text-center border-t border-white/5">
                                    <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                                        {isFullAccess ? 'Verified Friend' : 'Restricted Access'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="text-center md:text-left flex-grow">
                            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mb-6">
                                <span className="bg-indigo-500/10 text-indigo-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-indigo-500/20">System ID: {user.id}</span>
                                <span className="bg-white/5 text-gray-500 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-white/10">Member since {new Date(user.created_at).getFullYear()}</span>
                            </div>

                            <h1 className="text-5xl sm:text-7xl font-black text-white mb-4 tracking-tighter leading-none animate-fade-in">
                                {user.full_name || user.username}
                            </h1>

                            {!isFullAccess && (
                                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 max-w-xl mb-6 backdrop-blur-sm">
                                    <div className="flex items-center gap-3 text-red-400 mb-1">
                                        <i className="fas fa-eye-slash text-sm"></i>
                                        <span className="text-xs font-black uppercase tracking-widest">Privacy Protocol Active</span>
                                    </div>
                                    <p className="text-gray-400 text-sm font-light">
                                        Add {user.username} as a friend to view their neural bio, avatar, and full profile details.
                                    </p>
                                </div>
                            )}

                            {user.bio && (
                                <div className="bg-white/5 border border-white/5 rounded-2xl p-6 max-w-xl animate-fade-in [animation-delay:0.3s] mb-8">
                                    <p className="text-indigo-400 text-[10px] font-black uppercase tracking-widest mb-2">Neural Bio</p>
                                    <p className="text-gray-300 italic font-light leading-relaxed">"{user.bio}"</p>
                                </div>
                            )}

                            <div className="mt-8 flex flex-wrap gap-4 justify-center md:justify-start">
                                {/* Logic to Add/Remove friend could go here, but focusing on view for now */}
                                <button onClick={() => navigate('/friends')} className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-full text-sm">Return to Network</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Activity Sections (Only enabled if friend/full access) */}
            {isFullAccess && (
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-24 space-y-20">

                    {/* Recent Ratings */}
                    {user.recent_ratings && user.recent_ratings.length > 0 && (
                        <section>
                            <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-8">Recent Transmissions</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                {user.recent_ratings.map(rating => (
                                    <div key={rating.id} className="glass-panel p-4 rounded-2xl flex gap-4 items-center group cursor-pointer hover:bg-white/5 transition" onClick={() => navigate(`/movies/${rating.movie_id}`)}>
                                        <img
                                            src={rating.poster_path ? `https://image.tmdb.org/t/p/w200${rating.poster_path}` : 'https://via.placeholder.com/200x300?text=No+Poster'}
                                            alt={rating.title}
                                            className="w-16 h-24 rounded-lg object-cover shadow-lg group-hover:scale-105 transition-transform"
                                        />
                                        <div>
                                            <h4 className="font-bold text-white text-sm line-clamp-1 mb-1">{rating.title}</h4>
                                            <div className="flex items-center gap-1 mb-2">
                                                <span className="text-yellow-500 text-xs">★</span>
                                                <span className="text-xs font-bold">{rating.rating}/5</span>
                                            </div>
                                            <p className="text-[10px] text-gray-500 uppercase tracking-wider">{new Date(rating.created_at).toLocaleDateString()}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Recent Watchlist */}
                    {user.recent_watchlist && user.recent_watchlist.length > 0 && (
                        <section>
                            <h3 className="text-[10px] font-black text-pink-400 uppercase tracking-[0.3em] mb-8">Neural Queue</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
                                {user.recent_watchlist.map(movie => (
                                    <div key={movie.id} className="group relative cursor-pointer" onClick={() => navigate(`/movies/${movie.id}`)}>
                                        <div className="relative rounded-2xl overflow-hidden aspect-[2/3]">
                                            <img
                                                src={movie.poster_path ? `https://image.tmdb.org/t/p/w300${movie.poster_path}` : 'https://via.placeholder.com/300x450?text=No+Poster'}
                                                alt={movie.title}
                                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                            />
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                                <p className="text-xs font-bold text-white text-center w-full">{movie.title}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}
                </div>
            )}

            {/* Stats / Friends Grid */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {friends.length > 0 && isFullAccess && (
                    <div className="mb-24">
                        <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-8">Known Associates ({friends.length})</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
                            {friends.slice(0, 6).map(friend => (
                                <div key={friend.id} className="glass-panel p-4 rounded-2xl text-center hover:bg-white/5 transition cursor-pointer" onClick={() => navigate(`/profile/${friend.id}`)}>
                                    <div className="w-12 h-12 mx-auto bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold mb-3">
                                        {friend.username.charAt(0).toUpperCase()}
                                    </div>
                                    <p className="text-sm font-bold truncate">{friend.username}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
