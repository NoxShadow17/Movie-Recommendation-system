import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    onLogout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const navLinks = [
    { name: 'Discover', path: '/' },
    { name: 'Movies', path: '/movies' },
    { name: 'Feed', path: '/upcoming' },
    { name: 'Friends', path: '/friends' },
  ];

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 ${scrolled ? 'py-4 bg-black/40 backdrop-blur-xl border-b border-white/5' : 'py-8 bg-transparent'
        }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <Link to="/" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 group shrink-0">
              <div className="w-10 h-10 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(99,102,241,0.3)] group-hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] transition-all duration-500">
                <img src="/logo.png" alt="CineAI Logo" className="w-full h-full object-cover" />
              </div>
              <span className="text-xl font-cinematic font-black tracking-tighter text-white">
                CINE<span className="text-indigo-400">AI</span>
              </span>
            </Link>

            {/* Center Links - Desktop */}
            <div className="hidden lg:flex items-center gap-1 bg-white/5 backdrop-blur-md rounded-full px-2 py-1.5 border border-white/10">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-5 py-2 rounded-full text-sm font-bold tracking-tight transition-all duration-300 ${location.pathname === link.path
                    ? 'bg-indigo-500 text-white shadow-[0_4px_15px_rgba(99,102,241,0.3)]'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-3 sm:gap-6">
              <Link to="/watch-party" className="hidden sm:flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400 hover:text-indigo-300 transition-colors">
                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping"></span>
                Watch Party
              </Link>

              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center gap-3 p-1 sm:pr-4 rounded-full bg-white/5 hover:bg-white/10 border border-white/5 transition-all group"
                >
                  {user?.profile_picture ? (
                    <img 
                      src={user.profile_picture} 
                      alt={user.username}
                      className="w-8 h-8 rounded-full border-2 border-white/20 object-cover shadow-[0_0_10px_rgba(99,102,241,0.2)] group-hover:border-indigo-500/50 transition-all"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 border border-white/10 flex items-center justify-center text-xs font-black text-gray-300 group-hover:border-indigo-500/50 transition-all">
                      {user?.username?.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="hidden sm:inline text-xs font-bold text-gray-400 group-hover:text-white transition-colors">{user?.username}</span>
                  <i className={`fas fa-chevron-down text-[10px] text-gray-600 transition-transform duration-300 ${menuOpen ? 'rotate-180' : ''}`}></i>
                </button>

                {menuOpen && (
                  <div className="absolute right-0 mt-4 w-56 glass-panel rounded-3xl p-2 shadow-[0_20px_50px_rgba(0,0,0,0.5)] animate-in fade-in slide-in-from-top-4 duration-300">
                    <Link
                      to="/profile"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-2xl transition-all"
                    >
                      <i className="fas fa-user-circle text-lg"></i>
                      Taste Profile
                    </Link>
                    <Link
                      to="/recommendations"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-2xl transition-all"
                    >
                      <i className="fas fa-sparkles text-lg"></i>
                      Personal Picks
                    </Link>
                    <div className="h-px bg-white/5 my-2"></div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-pink-500 hover:bg-pink-500/10 rounded-2xl transition-all"
                    >
                      <i className="fas fa-sign-out-alt text-lg"></i>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-white border border-white/10"
              >
                {mobileMenuOpen ? (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation Drawer */}
      <div className={`fixed inset-0 z-[150] lg:hidden transition-all duration-700 ${mobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
        <div className="absolute inset-0 bg-black/90 backdrop-blur-2xl transition-all duration-500" onClick={() => setMobileMenuOpen(false)}></div>
        <div className={`absolute top-0 right-0 bottom-0 w-[80%] max-w-sm glass-panel border-l border-white/10 shadow-2xl p-8 pt-24 transition-transform duration-700 ease-out z-[160] ${mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className="flex flex-col gap-4">
            <p className="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-4">Neural Navigation</p>
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`px-8 py-5 rounded-[2rem] text-lg font-black tracking-tight transition-all duration-300 border ${location.pathname === link.path
                  ? 'bg-indigo-500 text-white border-indigo-400 shadow-[0_10px_30px_rgba(99,102,241,0.3)]'
                  : 'text-gray-400 border-white/5 hover:text-white hover:bg-white/5'
                  }`}
              >
                {link.name}
              </Link>
            ))}

            <div className="h-px bg-white/5 my-8"></div>

            <Link
              to="/watch-party"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-between p-6 rounded-[2rem] bg-indigo-500/10 border border-indigo-500/20 text-indigo-400"
            >
              <div className="flex items-center gap-3">
                <i className="fas fa-users"></i>
                <span className="font-black uppercase tracking-widest text-xs">Watch Party</span>
              </div>
              <span className="w-2 h-2 bg-indigo-500 rounded-full animate-ping"></span>
            </Link>
          </div>

          <div className="absolute bottom-12 left-8 right-8 text-center">
            <p className="text-[8px] font-black text-gray-700 uppercase tracking-widest">CineAI Experience v2.0</p>
          </div>
        </div>
      </div>
    </>
  );
}
