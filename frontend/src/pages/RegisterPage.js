import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function RegisterPage({ onLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        // Login with the new account
        const loginResponse = await fetch(`http://localhost:8000/api/v1/auth/login?username=${encodeURIComponent(formData.username)}&password=${encodeURIComponent(formData.password)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (loginResponse.ok) {
          const loginData = await loginResponse.json();
          onLogin(loginData.access_token);
          navigate('/');
        }
      } else {
        try {
          const data = await response.json();
          let errorMsg = 'Registration failed';

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
          setError('Registration failed: Invalid response format');
        }
      }
    } catch (err) {
      setError('Connection error');
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
          <h2 className="text-2xl font-bold text-white mb-6">Register</h2>

          {error && (
            <div className="bg-red-500 bg-opacity-10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-300 mb-2">Full Name</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="Your full name"
                required
              />
            </div>

            <div>
              <label className="block text-gray-300 mb-2">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="Choose a username"
                required
              />
            </div>

            <div>
              <label className="block text-gray-300 mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="your@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-gray-300 mb-2">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
                placeholder="Choose a password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary font-semibold py-3 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Register'}
            </button>
          </form>

          <p className="text-center text-gray-400 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
