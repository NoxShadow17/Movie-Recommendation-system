import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function RecommendationDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/recommendations/profile/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/recommendations/profile/update', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Profile updated successfully!');
        fetchStats(); // Refresh stats
      }
    } catch (err) {
      console.error('Error updating profile:', err);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center text-gray-400">Loading dashboard...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center text-gray-400">No data available</div>
      </div>
    );
  }

  // Chart configurations
  const moodChartData = {
    labels: Object.keys(stats.mood_distribution || {}),
    datasets: [{
      label: 'Mood Distribution',
      data: Object.values(stats.mood_distribution || {}),
      backgroundColor: [
        '#3b82f6', // happy - blue
        '#ef4444', // sad - red
        '#10b981', // excited - green
        '#f59e0b', // relaxed - orange
        '#8b5cf6', // thoughtful - purple
        '#6366f1'  // scared - indigo
      ],
      borderWidth: 2,
      borderColor: '#1f2937'
    }]
  };

  const genreChartData = {
    labels: stats.top_genres.map(([genre]) => genre),
    datasets: [{
      label: 'Genre Preferences',
      data: stats.top_genres.map(([, count]) => count),
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#9ca3af'
        }
      },
      title: {
        display: true,
        text: '',
        color: '#e5e7eb'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: '#374151'
        },
        ticks: {
          color: '#9ca3af'
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#9ca3af'
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#9ca3af'
        }
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Recommendation Dashboard</h1>
        <p className="text-gray-400">Advanced insights into your movie preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8 overflow-x-auto">
        {['overview', 'mood-analysis', 'genre-preferences', 'advanced-stats'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${
              activeTab === tab
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {tab.replace('-', ' ').charAt(0).toUpperCase() + tab.replace('-', ' ').slice(1)}
          </button>
        ))}
        <button
          onClick={updateProfile}
          className="ml-auto px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          Update Profile
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Ratings"
            value={stats.total_ratings}
            icon="⭐"
            color="blue"
          />
          <StatCard
            title="Favorite Mood"
            value={stats.favorite_mood || 'Not set'}
            icon="😊"
            color="purple"
          />
          <StatCard
            title="Preferred Genre"
            value={stats.preferred_genres?.split(',')[0] || 'Not set'}
            icon="🎬"
            color="green"
          />
          <StatCard
            title="Preferred Language"
            value={stats.preferred_language || 'Not set'}
            icon="🌍"
            color="orange"
          />
        </div>
      )}

      {/* Mood Analysis Tab */}
      {activeTab === 'mood-analysis' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Mood Distribution</h3>
            <Pie data={moodChartData} options={pieOptions} />
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Mood Insights</h3>
            <div className="space-y-4">
              {Object.entries(stats.mood_distribution || {}).map(([mood, count]) => (
                <div key={mood} className="flex justify-between items-center bg-gray-700 p-3 rounded">
                  <span className="text-white">{mood}</span>
                  <span className="text-indigo-400 font-bold">{count} ratings</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Genre Preferences Tab */}
      {activeTab === 'genre-preferences' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Top Genres</h3>
            <Bar data={genreChartData} options={options} />
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Genre Preferences</h3>
            <div className="space-y-4">
              {stats.top_genres.map(([genre, count], idx) => (
                <div key={idx} className="flex justify-between items-center bg-gray-700 p-3 rounded">
                  <span className="text-white">{genre}</span>
                  <span className="text-indigo-400 font-bold">{count} ratings</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Advanced Stats Tab */}
      {activeTab === 'advanced-stats' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Profile Information</h3>
            <div className="space-y-4">
              <InfoRow label="User ID" value={stats.user_id} />
              <InfoRow label="Preferred Directors" value={stats.preferred_directors || 'Not set'} />
              <InfoRow label="Last Updated" value={stats.last_updated ? new Date(stats.last_updated).toLocaleDateString() : 'Never'} />
            </div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Recommendation Quality</h3>
            <div className="space-y-4">
              <div className="bg-gray-700 p-4 rounded">
                <h4 className="text-white font-semibold mb-2">Rating Patterns</h4>
                <p className="text-gray-300 text-sm">
                  You have rated {stats.total_ratings} movies. Your preferences are being analyzed to improve recommendations.
                </p>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <h4 className="text-white font-semibold mb-2">Mood Consistency</h4>
                <p className="text-gray-300 text-sm">
                  {Object.keys(stats.mood_distribution).length} different moods detected in your ratings.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-white font-bold mb-4">Personalized Recommendations</h3>
          <p className="text-gray-400 text-sm mb-4">Get recommendations based on your complete profile</p>
          <button className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
            View Personalized Recs
          </button>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-white font-bold mb-4">Mood-Based Recs</h3>
          <p className="text-gray-400 text-sm mb-4">Get recommendations for your current mood</p>
          <div className="flex gap-2">
            {['happy', 'sad', 'excited', 'relaxed', 'thoughtful', 'scared'].map(mood => (
              <button
                key={mood}
                className="flex-1 bg-gray-700 text-white py-2 rounded-lg hover:bg-gray-600 transition text-sm"
              >
                {mood}
              </button>
            ))}
          </div>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-white font-bold mb-4">Trending Now</h3>
          <p className="text-gray-400 text-sm mb-4">See what's trending this week</p>
          <button className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition">
            View Trending
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-white text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between items-center bg-gray-700 p-3 rounded">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
