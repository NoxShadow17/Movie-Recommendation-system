import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const UpcomingMovies = () => {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchUpcoming();
    }, []);

    const fetchUpcoming = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/recommendations/upcoming?limit=6', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setMovies(data);
            }
        } catch (error) {
            console.error('Error fetching upcoming movies:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="h-64 bg-gray-800/40 animate-pulse rounded-3xl border border-gray-700/50"></div>
                ))}
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Trailer Sentiment Engine</h2>
                    <p className="text-gray-400 text-sm italic">Predicting hype via real-time YouTube social analysis</p>
                </div>
                <div className="flex items-center gap-4">
                    <Link
                        to="/upcoming"
                        className="text-indigo-400 hover:text-indigo-300 text-sm font-bold flex items-center gap-1 group/link"
                    >
                        View All
                        <i className="fas fa-arrow-right text-[10px] transition-transform group-hover/link:translate-x-1"></i>
                    </Link>
                    <div className="hidden sm:flex items-center gap-2 bg-indigo-500/10 px-3 py-1.5 rounded-full border border-indigo-500/20">
                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-ping"></div>
                        <span className="text-indigo-400 text-xs font-bold uppercase tracking-widest">Live Feed</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {movies.map((movie) => (
                    <Link
                        key={movie.id}
                        to={`/upcoming/${movie.id}`}
                        className="group relative bg-gray-800/20 backdrop-blur-xl border border-gray-700/30 rounded-[2.5rem] overflow-hidden transition-all duration-500 hover:bg-gray-800/40 hover:border-indigo-500/40 hover:-translate-y-2 hover:shadow-[0_20px_50px_rgba(79,70,229,0.15)] block"
                    >
                        {/* Poster Section */}
                        <div className="relative h-48 overflow-hidden">
                            {movie.poster_path ? (
                                <img
                                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                    alt={movie.title}
                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-60 group-hover:opacity-100"
                                />
                            ) : (
                                <div className="w-full h-full bg-gray-900 flex items-center justify-center text-gray-700">
                                    <i className="fas fa-image text-4xl"></i>
                                </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent"></div>

                            <div className="absolute top-4 left-4">
                                <span className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-bold text-gray-300 border border-white/10 uppercase tracking-widest">
                                    {movie.release_date ? `Release: ${new Date(movie.release_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}` : 'Coming Soon'}
                                </span>
                            </div>
                        </div>

                        {/* Info Section */}
                        <div className="p-6">
                            <h3 className="text-xl font-bold text-white mb-4 line-clamp-1 group-hover:text-indigo-400 transition-colors">
                                {movie.title}
                            </h3>

                            {/* Hype Meter */}
                            <div className="mb-6 space-y-3">
                                <div className="flex justify-between items-end">
                                    <span className="text-xs font-bold text-gray-400 uppercase tracking-tighter">Community Hype</span>
                                    <span className={`text-lg font-black ${movie.hype_score > 75 ? 'text-pink-500' :
                                            movie.hype_score > 50 ? 'text-indigo-400' : 'text-yellow-500'
                                        }`}>
                                        {movie.hype_score}%
                                    </span>
                                </div>
                                <div className="h-3 bg-gray-900/60 rounded-full overflow-hidden p-0.5 border border-white/5">
                                    <div
                                        className={`h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(99,102,241,0.5)] ${movie.hype_score > 75 ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500' :
                                                'bg-gradient-to-r from-indigo-600 to-indigo-400'
                                            }`}
                                        style={{ width: `${movie.hype_score}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Sentiment Summary */}
                            <div className="bg-gray-900/40 rounded-2xl p-4 border border-white/5">
                                <div className="flex items-start gap-3">
                                    <div className={`mt-1 w-2 h-2 rounded-full ${movie.summary.includes('Positive') ? 'bg-green-400' :
                                            movie.summary.includes('Mixed') ? 'bg-yellow-400' : 'bg-gray-400'
                                        }`}></div>
                                    <div>
                                        <p className="text-[10px] text-gray-500 uppercase font-black leading-none mb-1">Sentiment Verdict</p>
                                        <p className="text-sm text-gray-300 font-medium">{movie.summary}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default UpcomingMovies;
