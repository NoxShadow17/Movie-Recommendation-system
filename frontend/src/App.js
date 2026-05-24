import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import MoviesPage from './pages/MoviesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import ProfilePage from './pages/ProfilePage';
import MovieDetailPage from './pages/MovieDetailPage';
import FriendsPage from './pages/FriendsPage';
import WatchPartyPage from './pages/WatchPartyPage';
import UpcomingMoviesPage from './pages/UpcomingMoviesPage';
import UpcomingMovieDetailPage from './pages/UpcomingMovieDetailPage';
import UserProfilePage from './pages/UserProfilePage';
import Navbar from './components/Navbar';
import AIAssistant from './components/AIAssistant';
import { API_BASE_URL } from './config';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      fetchUser();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        if (data && typeof data === 'object' && !Array.isArray(data) && !data.detail) {
          setUser(data);
        }
      } else {
        logout();
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const login = async (newToken) => {
    console.log('🔑 Login function called with token:', newToken);
    localStorage.setItem('token', newToken);
    setToken(newToken);

    // Fetch user data to get user_id synchronously
    try {
      console.log('🔍 Fetching user data...');
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('👤 User data received:', data);
        if (data && data.id) {
          localStorage.setItem('user_id', data.id);
          console.log('✅ User ID stored in localStorage:', data.id);
          setUser(data);
        } else {
          console.log('❌ No user ID in response');
        }
      } else {
        console.log('❌ Failed to fetch user data, status:', response.status);
      }
    } catch (error) {
      console.error('❌ Error fetching user data:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[var(--cinematic-bg)] text-white relative">
        <div className="cinematic-overlay"></div>
        {token && <Navbar user={user} onLogout={logout} />}

        {token && <AIAssistant />}

        <Routes>
          <Route path="/login" element={!token ? <LoginPage onLogin={login} /> : <Navigate to="/" />} />
          <Route path="/register" element={!token ? <RegisterPage onLogin={login} /> : <Navigate to="/" />} />

          <Route path="/" element={token ? <DashboardPage /> : <Navigate to="/login" />} />
          <Route path="/movies" element={token ? <MoviesPage /> : <Navigate to="/login" />} />
          <Route path="/movies/:id" element={token ? <MovieDetailPage /> : <Navigate to="/login" />} />
          <Route path="/recommendations" element={token ? <RecommendationsPage /> : <Navigate to="/login" />} />
          <Route path="/profile" element={token ? <ProfilePage user={user} onLogout={logout} /> : <Navigate to="/login" />} />
          <Route path="/profile/:userId" element={token ? <UserProfilePage /> : <Navigate to="/login" />} />
          <Route path="/friends" element={token ? <FriendsPage /> : <Navigate to="/login" />} />
          <Route path="/watch-party" element={token ? <WatchPartyPage /> : <Navigate to="/login" />} />
          <Route path="/upcoming" element={token ? <UpcomingMoviesPage /> : <Navigate to="/login" />} />
          <Route path="/upcoming/:tmdbId" element={token ? <UpcomingMovieDetailPage /> : <Navigate to="/login" />} />

          <Route path="*" element={<Navigate to={token ? "/" : "/login"} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
