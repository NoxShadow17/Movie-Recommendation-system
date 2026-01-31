import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(data.access_token);
        navigate('/');
      } else {
        try {
          const data = await response.json();
          let errorMsg = 'Login failed';

          if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (Array.isArray(data.detail)) {
            errorMsg = data.detail.map(e => e.msg || String(e)).join(', ');
          } else if (data.detail?.msg) {
            errorMsg = data.detail.msg;
          } else if (typeof data.detail === 'object') {
            errorMsg = JSON.stringify(data.detail);
          }

          setError(errorMsg);
        } catch (e) {
          setError('Login failed: Invalid response format');
        }
      }
    } catch (err) {
      setError('Connection error: Make sure the backend server is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-4 group">
            <div className="w-12 h-12 rounded-2xl overflow-hidden shadow-[0_0_20px_rgba(99,102,241,0.3)] group-hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] transition-all duration-500">
              <img src="/logo.png" alt="CineAI Logo" className="w-full h-full object-cover" />
            </div>
            <span className="text-4xl font-cinematic font-black tracking-tighter text-white">
              CINE<span className="text-indigo-400">AI</span>
            </span>
          </Link>
          <p className="text-gray-400 mt-4 font-light tracking-widest uppercase text-[10px]">Neural Cinema Experience</p>
        </div>

        <div className="card bg-gray-800 border border-gray-700 p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Sign In</h2>

          {error && (
            <div className="bg-red-500 bg-opacity-10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-300 mb-2">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="Enter username"
              />
            </div>

            <div>
              <label className="block text-gray-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary font-semibold py-3 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-gray-400 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-indigo-400 hover:text-indigo-300">
              Register here
            </Link>
          </p>

        </div>
      </div>
    </div>
  );
}
