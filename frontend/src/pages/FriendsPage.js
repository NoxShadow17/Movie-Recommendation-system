import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const FriendsPage = () => {
  const [friends, setFriends] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [friendStats, setFriendStats] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const PAGE_SIZE = 10;

  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchFriendData();
  }, [token, navigate]);

  const fetchFriendData = async (pageNum = 0) => {
    try {
      if (pageNum === 0) setLoading(true);
      else setLoadingMore(true);

      setError('');

      const skip = pageNum * PAGE_SIZE;

      if (pageNum === 0) {
        // Fetch everything on initial load
        const [friendsRes, sentRes, receivedRes, statsRes] = await Promise.all([
          api.get(`/friends/list?skip=${skip}&limit=${PAGE_SIZE}`),
          api.get('/friends/requests/sent'),
          api.get('/friends/requests/received'),
          api.get('/friends/stats')
        ]);

        setFriends(friendsRes.data);
        setSentRequests(sentRes.data);
        setReceivedRequests(receivedRes.data);
        setFriendStats(statsRes.data);
        setHasMore(friendsRes.data.length === PAGE_SIZE);
      } else {
        // Fetch only friends for Load More
        const friendsRes = await api.get(`/friends/list?skip=${skip}&limit=${PAGE_SIZE}`);

        setFriends(prev => [...prev, ...friendsRes.data]);
        setHasMore(friendsRes.data.length === PAGE_SIZE);
      }

    } catch (err) {
      console.error('Error fetching friend data:', err);
      setError('Failed to load friend data');
    } finally {
      if (pageNum === 0) setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchFriendData(nextPage);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.length < 3) return;

    try {
      setLoading(true);
      const response = await api.get(`/friends/search?query=${searchQuery}`);
      setSearchResults(response.data);
    } catch (err) {
      console.error('Error searching users:', err);
      setError('Failed to search users');
    } finally {
      setLoading(false);
    }
  };

  const sendFriendRequest = async (userId) => {
    try {
      await api.post(`/friends/requests/send/${userId}`);
      setError('');
      fetchFriendData(); // Refresh data
    } catch (err) {
      console.error('Error sending friend request:', err);
      setError('Failed to send friend request');
    }
  };

  const acceptFriendRequest = async (requestId) => {
    try {
      await api.post(`/friends/requests/accept/${requestId}`);
      setError('');
      // Force refresh all friend data to update sent/received lists
      fetchFriendData();
    } catch (err) {
      console.error('Error accepting friend request:', err);
      setError('Failed to accept friend request');
    }
  };

  const rejectFriendRequest = async (requestId) => {
    try {
      await api.post(`/friends/requests/reject/${requestId}`);
      setError('');
      // Force refresh all friend data to update sent/received lists
      fetchFriendData();
    } catch (err) {
      console.error('Error rejecting friend request:', err);
      setError('Failed to reject friend request');
    }
  };

  const removeFriend = async (friendId) => {
    try {
      // Optimistically remove from UI
      setFriends(prev => prev.filter(f => f.id !== friendId));
      setFriendStats(prev => ({
        ...prev,
        total_friends: Math.max(0, (prev.total_friends || 0) - 1)
      }));

      await api.delete(`/friends/remove/${friendId}`);
      setError('');
    } catch (err) {
      console.error('Error removing friend:', err);
      setError('Failed to remove friend');
      // Revert/Refetch if failed
      fetchFriendData();
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'friends': return 'bg-green-600 text-white';
      case 'request_sent': return 'bg-yellow-600 text-white';
      case 'request_received': return 'bg-blue-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'friends': return 'Friends';
      case 'request_sent': return 'Request Sent';
      case 'request_received': return 'Request Received';
      default: return 'Available';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Friends 🤝</h1>
        <p className="text-gray-400">Manage your friends and social connections</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-600 border border-red-500 text-white px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Friend Statistics */}
      {friendStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <StatCard label="Total Friends" value={friendStats.total_friends || 0} icon="👥" />
          <StatCard label="Sent Requests" value={friendStats.pending_sent_requests || 0} icon="📤" />
          <StatCard label="Received Requests" value={friendStats.pending_received_requests || 0} icon="📥" />
          <StatCard label="Total Pending" value={friendStats.total_pending_requests || 0} icon="⏳" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Search and Add Friends */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Find Friends</h2>

            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by username, email, or name..."
                  className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  minLength="3"
                />
              </div>
              <button
                type="submit"
                disabled={loading || searchQuery.length < 3}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-105"
              >
                {loading ? 'Searching...' : 'Search Users'}
              </button>
            </form>

            {searchResults.length > 0 && (
              <div className="mt-8 space-y-4">
                <h3 className="text-lg font-semibold text-white mb-4">Search Results</h3>
                {searchResults.map((user) => (
                  <div key={user.id} className="bg-gray-700 border border-gray-600 rounded-lg p-4 hover:border-gray-500 transition">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-bold text-white">{user.username}</h4>
                        <p className="text-gray-400 text-sm">{user.email}</p>
                        {user.full_name && (
                          <p className="text-gray-400 text-sm">{user.full_name}</p>
                        )}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                          {getStatusText(user.status)}
                        </span>
                        {user.status === 'available' && (
                          <button
                            onClick={() => sendFriendRequest(user.id)}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition transform hover:scale-105"
                          >
                            Add Friend
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Friends List */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Your Friends</h2>

            {friends.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🤝</div>
                <p className="text-gray-400 text-lg mb-6">No friends yet</p>
                <p className="text-gray-500 mb-8">Search for users above to add them as friends!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {friends.map((friend) => (
                  <div
                    key={friend.id}
                    className="p-4 bg-gray-900 rounded-xl border border-gray-800 flex items-center justify-between group hover:border-indigo-500/50 transition-all cursor-pointer"
                    onClick={() => navigate(`/profile/${friend.id}`)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg overflow-hidden relative">
                        {friend.profile_picture ? (
                          <img
                            src={friend.profile_picture}
                            alt={friend.username}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              // Show fallback initials by making the span visible
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                        ) : null}
                        <span
                          className="absolute inset-0 flex items-center justify-center"
                          style={{ display: friend.profile_picture ? 'none' : 'flex' }}
                        >
                          {friend.username.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-bold text-white group-hover:text-indigo-400 transition-colors">{friend.username}</h3>
                        <p className="text-gray-500 text-xs">{friend.email}</p>
                        {friend.full_name && (
                          <p className="text-gray-500 text-xs">{friend.full_name}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="px-3 py-1 bg-green-600 text-white rounded-full text-xs font-medium">
                        Friends
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFriend(friend.id);
                        }}
                        className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Remove Friend"
                      >
                        <i className="fas fa-user-minus"></i>
                      </button>
                    </div>
                  </div>
                ))}

                {hasMore && (
                  <div className="pt-4 text-center">
                    <button
                      onClick={handleLoadMore}
                      disabled={loadingMore}
                      className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
                    >
                      {loadingMore ? (
                        <span className="flex items-center gap-2">
                          <i className="fas fa-spinner fa-spin"></i> Loading...
                        </span>
                      ) : (
                        'Load More Friends'
                      )}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Friend Requests */}
      <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Received Requests */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Friend Requests</h2>

          {receivedRequests.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No pending friend requests
            </div>
          ) : (
            <div className="space-y-4">
              {receivedRequests.map((request) => (
                <div key={request.id} className="flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg p-4 hover:border-gray-500 transition">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      {request.sender_username?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-bold text-white">{request.sender_username}</h4>
                      <p className="text-gray-400 text-sm">{request.sender_email}</p>
                    </div>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => acceptFriendRequest(request.id)}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition transform hover:scale-105"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => rejectFriendRequest(request.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition transform hover:scale-105"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sent Requests */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Sent Requests</h2>

          {sentRequests.filter(req => req.status === 'pending').length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No pending sent requests
            </div>
          ) : (
            <div className="space-y-4">
              {sentRequests.filter(req => req.status === 'pending').map((request) => (
                <div key={request.id} className="flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg p-4 hover:border-gray-500 transition">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-yellow-600 rounded-full flex items-center justify-center text-white font-bold">
                      {request.receiver_username?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-bold text-white">{request.receiver_username}</h4>
                      <p className="text-gray-400 text-sm">{request.receiver_email}</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 bg-yellow-600 text-white rounded-full text-xs font-medium">
                    Pending
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function StatCard({ label, value, icon }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center">
      <div className="text-4xl mb-3">{icon}</div>
      <p className="text-gray-400 text-sm mb-2">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

export default FriendsPage;
