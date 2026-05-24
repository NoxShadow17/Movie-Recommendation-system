import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

export default function AIAssistant() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I'm your AI cinema guide. What's your vibe today? I can find movies based on your mood or past favorites." }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);
    const token = localStorage.getItem('token');

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isTyping) return;

        const userMsg = input.trim();
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setIsTyping(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ message: userMsg })
            });

            if (response.ok) {
                const data = await response.json();
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.content,
                    movies: data.movies
                }]);
            } else {
                throw new Error("Neural link disruption.");
            }
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm having a bit of trouble connecting to my central brain. Try again in a moment?"
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="fixed bottom-8 right-8 z-[1000]">
            {/* Chat Window */}
            {isOpen && (
                <div className="absolute bottom-20 right-0 w-[calc(100vw-2rem)] sm:w-[400px] h-[500px] max-h-[70vh] glass-panel rounded-[2.5rem] shadow-[0_20px_60px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden border border-indigo-500/20 animate-float">
                    {/* Header */}
                    <div className="p-6 bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border-b border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.5)] overflow-hidden">
                                <img src="/bot_logo.png" alt="CineBot AI" className="w-full h-full object-cover" />
                            </div>
                            <div>
                                <h3 className="font-bold text-white leading-none">CineBot AI</h3>
                                <span className="text-[10px] text-indigo-400 font-black uppercase tracking-widest">Neural Link Active</span>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-white transition-colors">
                            <i className="fas fa-times"></i>
                        </button>
                    </div>

                    {/* Messages */}
                    <div ref={scrollRef} className="flex-grow overflow-y-auto p-6 space-y-6 scrollbar-hide">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className={`max-w-[85%] p-4 rounded-2xl text-sm ${msg.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-tr-none shadow-[0_5px_15px_rgba(79,70,229,0.3)]'
                                    : 'bg-white/5 border border-white/10 text-gray-300 rounded-tl-none'
                                    }`}>
                                    {msg.content}
                                </div>

                                {msg.movies && msg.movies.length > 0 && (
                                    <div className="mt-4 flex flex-col gap-3 w-full">
                                        <span className="text-[9px] font-black uppercase tracking-[0.2em] text-indigo-400 ml-2">Neural Attachments</span>
                                        <div className="grid grid-cols-1 gap-3">
                                            {msg.movies.map(movie => (
                                                <Link
                                                    key={movie.id}
                                                    to={`/movies/${movie.id}`}
                                                    className="flex items-center gap-4 p-3 rounded-2xl bg-white/5 border border-white/5 hover:border-indigo-500/30 hover:bg-white/10 transition-all group"
                                                >
                                                    <div className="w-12 h-16 rounded-lg overflow-hidden flex-shrink-0 border border-white/10">
                                                        <img
                                                            src={`https://image.tmdb.org/t/p/w200${movie.poster_path}`}
                                                            className="w-full h-full object-cover"
                                                            alt={movie.title}
                                                        />
                                                    </div>
                                                    <div className="flex-grow overflow-hidden">
                                                        <div className="text-xs font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-1">{movie.title}</div>
                                                        <div className="text-[10px] text-gray-500 line-clamp-1">{movie.genre.split(',')[0]}</div>
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <div className="text-[9px] font-black text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded">
                                                                {movie.vote_average ? (movie.vote_average * 10).toFixed(0) : 0}% Match
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <i className="fas fa-arrow-right text-[10px] text-gray-600 group-hover:text-indigo-400 pr-2"></i>
                                                </Link>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl rounded-tl-none flex gap-1 items-center">
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSend} className="p-6 border-t border-white/5 bg-black/20">
                        <div className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Tell me what you're looking for..."
                                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 pl-4 pr-12 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 transition-all"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || isTyping}
                                className="absolute right-2 top-1.5 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center hover:from-indigo-400 hover:to-purple-500 transition-all shadow-lg hover:shadow-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                                    <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                                </svg>
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Float Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-16 h-16 rounded-full flex items-center justify-center text-white shadow-[0_10px_30px_rgba(99,102,241,0.4)] transition-all duration-500 hover:scale-110 active:scale-95 z-[1001] relative overflow-hidden group ${isOpen ? 'bg-gray-800 border border-white/10' : 'bg-gradient-to-br from-indigo-500 to-purple-600'
                    }`}
            >
                {isOpen ? (
                    <i className="fas fa-times text-xl"></i>
                ) : (
                    <>
                        <img src="/bot_logo.png" alt="CineBot" className="w-full h-full object-cover z-10 p-2" />
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]"></div>
                    </>
                )}
            </button>
        </div>
    );
}

// Add these keyframes to index.css if not present
// @keyframes shimmer { 100% { transform: translateX(100%); } }
