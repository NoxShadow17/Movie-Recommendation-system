import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function UpcomingMoviesPage() {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchUpcoming();
        window.scrollTo(0, 0);
    }, []);

    const fetchUpcoming = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/recommendations/upcoming?limit=20', {
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

    return (
        <div className="min-h-screen bg-gray-950 pt-32 pb-24 px-4 sm:px-6 lg:px-8">
            <div className="absolute top-0 left-0 right-0 h-96 bg-gradient-to-b from-indigo-500/10 to-transparent pointer-events-none"></div>

            <div className="max-w-7xl mx-auto relative z-10">
                <header className="mb-20">
                    <div className="flex items-center gap-3 mb-6">
                        <span className="bg-pink-500/10 text-pink-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-pink-500/20">Temporal Stream</span>
                        <span className="text-gray-500 text-xs font-bold tracking-widest uppercase">Upcoming Discovery</span>
                    </div>

                    <h1 className="text-6xl sm:text-8xl font-black text-white mb-8 tracking-tighter leading-none animate-fade-in">
                        The <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">Anticipation</span> Feed
                    </h1>

                    <p className="text-xl text-gray-500 max-w-2xl font-light leading-relaxed animate-fade-in [animation-delay:0.2s]">
                        Real-time neural analysis of global engagement data. We decode crowd sentiment to predict the cultural impact of future releases.
                    </p>
                </header>

                {loading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12">
                        {[...Array(8)].map((_, i) => (
                            <div key={i} className="h-[450px] bg-white/5 animate-pulse rounded-[3rem] border border-white/5"></div>
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 animate-fade-in [animation-delay:0.4s]">
                        {movies.map((movie) => (
                            <UpcomingMovieCard key={movie.id} movie={movie} />
                        ))}
                    </div>
                )}

                {!loading && movies.length === 0 && (
                    <div className="text-center py-32 glass-panel rounded-[4rem] border-white/5">
                        <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-8">
                            <i className="fas fa-calendar-xmark text-3xl text-gray-600"></i>
                        </div>
                        <h3 className="text-3xl font-black text-white mb-2">Manifest Empty</h3>
                        <p className="text-gray-500 font-light">The anticipation stream is currently quiet. Check back as new transmissions arrive.</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function UpcomingMovieCard({ movie }) {
    return (
        <Link
            to={`/upcoming/${movie.id}`}
            className="group block h-full"
        >
            <div className="relative glass-panel rounded-[3rem] overflow-hidden border-white/5 h-full transition-all duration-700 hover:border-pink-500/50 group-hover:-translate-y-3 shadow-2xl">
                {/* Poster Container */}
                <div className="relative h-64 overflow-hidden">
                    {movie.poster_path ? (
                        <img
                            src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                            alt={movie.title}
                            className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-70 group-hover:opacity-100"
                        />
                    ) : (
                        <div className="w-full h-full bg-gray-900 flex items-center justify-center text-gray-700">
                            <i className="fas fa-image text-4xl"></i>
                        </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/20 to-transparent"></div>

                    {/* Hype Score Circle */}
                    <div className="absolute top-6 right-6">
                        <div className={`w-14 h-14 rounded-2xl backdrop-blur-xl border border-white/10 flex flex-col items-center justify-center shadow-lg ${movie.hype_score > 75 ? 'bg-pink-500/20 border-pink-500/30' : 'bg-indigo-500/20 border-indigo-500/30'
                            }`}>
                            <span className={`text-lg font-black leading-none ${movie.hype_score > 75 ? 'text-pink-400' : 'text-indigo-400'}`}>
                                {movie.hype_score}%
                            </span>
                            <span className="text-[7px] font-black uppercase tracking-widest text-gray-500">Hype</span>
                        </div>
                    </div>

                    <div className="absolute bottom-6 left-8 right-8">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-[10px] font-black uppercase tracking-widest text-pink-500/80">Arrival Date</span>
                            <div className="flex-grow h-px bg-pink-500/20"></div>
                        </div>
                        <p className="text-xs font-black text-gray-300 uppercase tracking-widest">
                            {movie.release_date ? new Date(movie.release_date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : 'Temporal TBD'}
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="p-8 pt-6">
                    <h3 className="text-xl font-bold text-white mb-6 line-clamp-1 group-hover:text-pink-400 transition-colors">
                        {movie.title}
                    </h3>

                    <div className="space-y-4">
                        <div className="flex items-center gap-4 p-4 bg-black/40 rounded-2xl border border-white/5 transition-all group-hover:border-white/10">
                            <div className={`w-3 h-3 rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)] ${movie.summary.includes('Positive') ? 'bg-green-400 animate-pulse' :
                                    movie.summary.includes('Mixed') ? 'bg-yellow-400' : 'bg-gray-400'
                                }`}></div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">{movie.summary}</span>
                        </div>

                        <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-[0.2em] text-gray-600 px-1">
                            <span>Manifest ID</span>
                            <span className="text-white/40">#{movie.id}</span>
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}
