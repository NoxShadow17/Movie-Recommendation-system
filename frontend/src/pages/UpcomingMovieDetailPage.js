import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

export default function UpcomingMovieDetailPage() {
    const { tmdbId } = useParams();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchMovieDetail();
        window.scrollTo(0, 0);
    }, [tmdbId]);

    const fetchMovieDetail = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/recommendations/upcoming/${tmdbId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setMovie(data);
            }
        } catch (error) {
            console.error('Error fetching upcoming movie details:', error);
        } finally {
            setLoading(false);
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
            <Link to="/upcoming" className="text-indigo-400 font-bold hover:underline">Return to Feed</Link>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-950 text-white pb-24">
            {/* Immersive Hero Backdrop */}
            <div className="relative h-[75vh] w-full overflow-hidden">
                <img
                    src={`https://image.tmdb.org/t/p/original${movie.backdrop_path || movie.poster_path}`}
                    alt={movie.title}
                    className="w-full h-full object-cover scale-105 blur-[1px] opacity-40 animate-fade-in"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/40 to-transparent"></div>

                <div className="absolute inset-0 flex items-end">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 w-full">
                        <div className="flex flex-col md:flex-row gap-12 items-start md:items-end">
                            {/* Floating Poster */}
                            <div className="w-48 sm:w-72 rounded-[3rem] overflow-hidden shadow-[0_30px_60px_rgba(0,0,0,0.8)] border border-white/10 flex-shrink-0 relative group animate-float">
                                <img
                                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                    alt={movie.title}
                                    className="w-full h-auto transition-transform duration-700 group-hover:scale-110"
                                />
                            </div>

                            {/* Title & Info */}
                            <div className="flex-grow animate-fade-in [animation-delay:0.3s]">
                                <div className="flex flex-wrap items-center gap-4 mb-6">
                                    <span className="bg-pink-500/10 text-pink-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-pink-500/20">Upcoming discovery</span>
                                    <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">{new Date(movie.release_date).getFullYear()}</span>
                                    <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                                    <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">{movie.runtime ? `${movie.runtime} MINUTES` : 'TBA'}</span>
                                </div>

                                <h1 className="text-6xl sm:text-8xl font-black mb-8 tracking-tighter leading-[0.85] text-white">
                                    {movie.title}
                                </h1>

                                <div className="flex flex-wrap items-center gap-10 border-t border-white/5 pt-8">
                                    <div className="flex flex-wrap gap-4">
                                        {movie.genres.map(genre => (
                                            <span key={genre} className="bg-white/5 px-5 py-2 rounded-2xl text-xs font-bold text-gray-400 border border-white/5">{genre}</span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content Sidebar Layout */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-16">
                        <section className="animate-fade-in [animation-delay:0.5s]">
                            <h2 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-6">Synopsis</h2>
                            <p className="text-2xl text-gray-300 leading-relaxed font-light">
                                {movie.overview || "Plot details for this upcoming release are currently under encryption. Check back as we decode more data."}
                            </p>
                        </section>

                        <section className="animate-fade-in [animation-delay:0.6s]">
                            <h2 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-8">Cast Members</h2>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
                                {movie.cast && movie.cast.length > 0 ? movie.cast.map(person => (
                                    <div key={person.id} className="group">
                                        <div className="aspect-[3/4] rounded-3xl overflow-hidden mb-4 border border-white/5 grayscale group-hover:grayscale-0 transition-all duration-700 hover:border-indigo-500/50">
                                            {person.profile_path ? (
                                                <img
                                                    src={`https://image.tmdb.org/t/p/w185${person.profile_path}`}
                                                    alt={person.name}
                                                    className="w-full h-full object-cover transition-transform group-hover:scale-110"
                                                />
                                            ) : (
                                                <div className="w-full h-full bg-white/5 flex items-center justify-center text-gray-700">
                                                    <i className="fas fa-user text-3xl"></i>
                                                </div>
                                            )}
                                        </div>
                                        <p className="text-sm font-bold text-white mb-1">{person.name}</p>
                                        <p className="text-[10px] text-gray-600 uppercase font-black tracking-widest">{person.character}</p>
                                    </div>
                                )) : (
                                    <p className="text-gray-500 italic">Personnel manifest pending.</p>
                                )}
                            </div>
                        </section>
                    </div>

                    {/* Hype Sidebar */}
                    <div className="space-y-8 animate-fade-in [animation-delay:0.7s]">
                        <div className="glass-panel p-10 rounded-[4rem] border-white/10 shadow-2xl sticky top-24 overflow-hidden">
                            <div className="absolute top-0 right-0 p-8">
                                <i className="fas fa-chart-line text-pink-500/10 text-8xl"></i>
                            </div>

                            <div className="relative z-10">
                                <div className="text-center mb-12">
                                    <div className="inline-flex items-center gap-2 bg-pink-500/10 px-4 py-2 rounded-full border border-pink-500/10 mb-6">
                                        <span className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-ping"></span>
                                        <span className="text-pink-500 text-[10px] font-black uppercase tracking-[0.2em]">Real-time Engagement</span>
                                    </div>
                                    <h3 className="text-4xl font-black text-white tracking-tighter mb-2">Neural Hype</h3>
                                    <p className="text-gray-500 text-xs font-bold tracking-widest uppercase">Based on {movie.comment_count} Logs</p>
                                </div>

                                {/* Circular Hype Meter */}
                                <div className="relative h-64 flex items-center justify-center mb-12">
                                    <div className="absolute inset-0 flex flex-col items-center justify-center z-10 transition-transform hover:scale-110 transition-duration-500">
                                        <span className="text-6xl font-black text-white tracking-tighter">{movie.hype_score}%</span>
                                        <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mt-2">Excitement Velocity</span>
                                    </div>
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle
                                            cx="50%" cy="50%" r="45%"
                                            className="stroke-white/5 fill-none"
                                            strokeWidth="6"
                                        />
                                        <circle
                                            cx="50%" cy="50%" r="45%"
                                            className={`stroke-indigo-500 fill-none transition-all duration-1000 ease-out ${movie.hype_score > 75 ? 'stroke-pink-500' : ''}`}
                                            strokeWidth="10"
                                            strokeDasharray="283%"
                                            strokeDashoffset={`${283 - (283 * movie.hype_score / 100)}%`}
                                            strokeLinecap="round"
                                            style={{ filter: `drop-shadow(0 0 15px ${movie.hype_score > 75 ? 'rgba(244,114,182,0.5)' : 'rgba(99,102,241,0.5)'})` }}
                                        />
                                    </svg>
                                </div>

                                <div className="space-y-6">
                                    <div className="p-8 bg-black/40 rounded-[2.5rem] border border-white/5 transition-all hover:border-white/10">
                                        <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Sentiment Verdict</h4>
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${movie.hype_summary.includes('Positive') ? 'bg-green-500/10 text-green-400' : (movie.hype_summary.includes('Simulated') ? 'bg-indigo-500/10 text-indigo-400' : 'bg-yellow-500/10 text-yellow-400')}`}>
                                                <i className={`fas ${movie.hype_summary.includes('Positive') ? 'fa-face-smile-beam' : (movie.hype_summary.includes('Simulated') ? 'fa-microchip' : 'fa-face-meh')} text-xl`}></i>
                                            </div>
                                            <span className="text-2xl font-black text-gray-200 tracking-tight">{movie.hype_summary}</span>
                                        </div>
                                    </div>

                                    <div className="p-8 border border-white/5 rounded-[2.5rem]">
                                        <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4">Neural Analysis</h4>
                                        <p className="text-lg text-gray-400 italic leading-relaxed font-light">
                                            "{movie.hype_reason}"
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
