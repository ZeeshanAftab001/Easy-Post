// components/Dashboard.jsx
import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';

export default function Dashboard() {
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);
    const [accounts, setAccounts] = useState([]);
    const [posts, setPosts] = useState([]);
    const [newPost, setNewPost] = useState({
        content: '',
        platform: 'facebook',
        schedule: 'now'
    });
    const [posting, setPosting] = useState(false);
    const [stats, setStats] = useState({
        totalPosts: 0,
        facebookPosts: 0,
        whatsappPosts: 0,
        scheduledPosts: 0
    });

    const location = useLocation();

    // Check for OAuth success/error in URL params
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const socialLinked = params.get('social_linked');
        const success = params.get('success');
        const error = params.get('error');

        if (socialLinked) {
            if (success === 'true') {
                alert(`✅ ${socialLinked.charAt(0).toUpperCase() + socialLinked.slice(1)} account connected successfully!`);
                // Clean URL
                window.history.replaceState({}, '', '/dashboard');
            } else if (error) {
                alert(`❌ Failed to connect ${socialLinked}: ${decodeURIComponent(error)}`);
                window.history.replaceState({}, '', '/dashboard');
            }
        }
    }, [location]);

    // Fetch user data and accounts on component mount
    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            // Fetch user info
            const userResponse = await api.get('/api/auth/me');
            setUser(userResponse.data);

            // Fetch connected social accounts
            const accountsResponse = await api.get('/api/oauth/social/accounts');
            setAccounts(accountsResponse.data);

            // Fetch post history
            const postsResponse = await api.get('/api/posts');
            setPosts(postsResponse.data);

            // Calculate stats
            calculateStats(postsResponse.data);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const calculateStats = (posts) => {
        const stats = {
            totalPosts: posts.length,
            facebookPosts: posts.filter(p => p.platform === 'facebook').length,
            whatsappPosts: posts.filter(p => p.platform === 'whatsapp').length,
            scheduledPosts: posts.filter(p => p.status === 'scheduled').length
        };
        setStats(stats);
    };

    const handlePostSubmit = async (e) => {
        e.preventDefault();
        if (!newPost.content.trim()) {
            alert('Please enter post content');
            return;
        }

        setPosting(true);
        try {
            const response = await api.post('/api/posts/create', {
                content: newPost.content,
                platform: newPost.platform,
                schedule_time: newPost.schedule === 'now' ? null : newPost.schedule
            });

            alert(`✅ Post ${newPost.schedule === 'now' ? 'published' : 'scheduled'} successfully!`);
            setNewPost({ content: '', platform: 'facebook', schedule: 'now' });
            
            // Refresh posts
            const postsResponse = await api.get('/api/posts');
            setPosts(postsResponse.data);
            calculateStats(postsResponse.data);
        } catch (error) {
            console.error('Failed to create post:', error);
            alert(`❌ Failed to create post: ${error.response?.data?.detail || error.message}`);
        } finally {
            setPosting(false);
        }
    };

    const handlePostNow = async (platform) => {
        const content = newPost.content;
        if (!content.trim()) {
            alert('Please enter post content first');
            return;
        }

        setPosting(true);
        try {
            const response = await api.post('/api/posts/instant', {
                content: content,
                platform: platform
            });

            alert(`✅ Posted to ${platform} successfully!`);
            setNewPost({ ...newPost, content: '' });
            
            // Refresh posts
            const postsResponse = await api.get('/api/posts');
            setPosts(postsResponse.data);
            calculateStats(postsResponse.data);
        } catch (error) {
            console.error('Failed to post:', error);
            alert(`❌ Failed to post to ${platform}: ${error.response?.data?.detail || error.message}`);
        } finally {
            setPosting(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const getPlatformColor = (platform) => {
        switch (platform) {
            case 'facebook': return 'bg-blue-500';
            case 'instagram': return 'bg-gradient-to-r from-purple-500 to-pink-500';
            case 'whatsapp': return 'bg-green-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'published': return 'bg-green-100 text-green-800';
            case 'scheduled': return 'bg-yellow-100 text-yellow-800';
            case 'failed': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-white text-xl">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div className="relative w-full min-h-screen bg-black">
            {/* Grid Background */}
            <div
                className="fixed inset-0 -z-20"
                style={{
                    backgroundImage: `
                        repeating-linear-gradient(0deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px),
                        repeating-linear-gradient(90deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px)
                    `,
                    backgroundSize: '100px 100px',
                    opacity: 0.1,
                }}
            />

            {/* Content container */}
            <div className="relative z-10 min-h-screen">
                <Navbar user={user} />

                <main className="container mx-auto px-4 py-8">
                    {/* Welcome Section */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">
                            Welcome back, {user?.username || 'User'}!
                        </h1>
                        <p className="text-gray-400">
                            Manage your AI-powered social media posting
                        </p>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                            <div className="text-gray-400 text-sm mb-1">Total Posts</div>
                            <div className="text-2xl font-bold text-white">{stats.totalPosts}</div>
                        </div>
                        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                            <div className="text-gray-400 text-sm mb-1">Facebook Posts</div>
                            <div className="text-2xl font-bold text-white">{stats.facebookPosts}</div>
                        </div>
                        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                            <div className="text-gray-400 text-sm mb-1">WhatsApp Posts</div>
                            <div className="text-2xl font-bold text-white">{stats.whatsappPosts}</div>
                        </div>
                        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                            <div className="text-gray-400 text-sm mb-1">Scheduled</div>
                            <div className="text-2xl font-bold text-white">{stats.scheduledPosts}</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column: Create Post & Connected Accounts */}
                        <div className="lg:col-span-2">
                            {/* Create Post Card */}
                            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-8">
                                <h2 className="text-xl font-bold text-white mb-4">Create New Post</h2>
                                
                                <form onSubmit={handlePostSubmit}>
                                    <textarea
                                        value={newPost.content}
                                        onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                                        placeholder="What would you like to post? Your AI agent can help optimize this content..."
                                        className="w-full h-40 bg-gray-800 border border-gray-700 rounded-lg p-4 text-white placeholder-gray-500 mb-4 focus:border-blue-500 focus:outline-none"
                                    />
                                    
                                    <div className="flex flex-wrap gap-4 mb-6">
                                        <div>
                                            <label className="block text-gray-400 text-sm mb-2">Platform</label>
                                            <select
                                                value={newPost.platform}
                                                onChange={(e) => setNewPost({...newPost, platform: e.target.value})}
                                                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                                            >
                                                {accounts.map(acc => (
                                                    <option key={acc.id} value={acc.platform}>
                                                        {acc.platform.charAt(0).toUpperCase() + acc.platform.slice(1)}
                                                    </option>
                                                ))}
                                                {accounts.length === 0 && (
                                                    <option value="">No connected accounts</option>
                                                )}
                                            </select>
                                        </div>
                                        
                                        <div>
                                            <label className="block text-gray-400 text-sm mb-2">Schedule</label>
                                            <select
                                                value={newPost.schedule}
                                                onChange={(e) => setNewPost({...newPost, schedule: e.target.value})}
                                                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                                            >
                                                <option value="now">Post Now</option>
                                                <option value="1 hour">In 1 Hour</option>
                                                <option value="tomorrow 9am">Tomorrow 9 AM</option>
                                                <option value="custom">Custom Time</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="flex gap-3">
                                        <button
                                            type="submit"
                                            disabled={posting || accounts.length === 0}
                                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                        >
                                            {posting ? 'Posting...' : newPost.schedule === 'now' ? 'Post Now' : 'Schedule Post'}
                                        </button>
                                        
                                        <button
                                            type="button"
                                            onClick={() => handlePostNow('facebook')}
                                            disabled={posting || !accounts.find(a => a.platform === 'facebook')}
                                            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                        >
                                            Post to Facebook
                                        </button>
                                        
                                        <button
                                            type="button"
                                            onClick={() => handlePostNow('whatsapp')}
                                            disabled={posting || !accounts.find(a => a.platform === 'whatsapp')}
                                            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                        >
                                            Post to WhatsApp
                                        </button>
                                    </div>
                                </form>
                            </div>

                            {/* Connected Accounts Card */}
                            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-xl font-bold text-white">Connected Accounts</h2>
                                    <Link
                                        to="/connect"
                                        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
                                    >
                                        + Add Account
                                    </Link>
                                </div>
                                
                                {accounts.length > 0 ? (
                                    <div className="space-y-4">
                                        {accounts.map(account => (
                                            <div key={account.id} className="flex items-center justify-between p-4 border border-gray-800 rounded-lg hover:border-gray-700 transition-colors">
                                                <div className="flex items-center space-x-4">
                                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getPlatformColor(account.platform)}`}>
                                                        <span className="text-white font-bold">
                                                            {account.platform === 'facebook' ? 'f' : 
                                                             account.platform === 'instagram' ? 'IG' : 'WA'}
                                                        </span>
                                                    </div>
                                                    <div>
                                                        <h3 className="text-white font-semibold">
                                                            {account.platform.charAt(0).toUpperCase() + account.platform.slice(1)}
                                                        </h3>
                                                        <p className="text-gray-400 text-sm">
                                                            {account.platform_user_id ? `ID: ${account.platform_user_id}` : 'Not connected'}
                                                        </p>
                                                        {account.pages && account.pages.length > 0 && (
                                                            <p className="text-gray-400 text-sm">
                                                                Pages: {account.pages.length}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge('published')}`}>
                                                        Connected
                                                    </span>
                                                    <button className="px-3 py-1 text-red-400 hover:text-red-300 text-sm">
                                                        Disconnect
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <div className="text-gray-400 mb-4">No accounts connected yet</div>
                                        <Link
                                            to="/connect"
                                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                                        >
                                            Connect Your First Account
                                        </Link>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Right Column: Recent Activity */}
                        <div>
                            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                                <h2 className="text-xl font-bold text-white mb-6">Recent Activity</h2>
                                
                                {posts.length > 0 ? (
                                    <div className="space-y-4">
                                        {posts.slice(0, 5).map(post => (
                                            <div key={post.id} className="p-4 border border-gray-800 rounded-lg">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div className="flex items-center space-x-2">
                                                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${getPlatformColor(post.platform)}`}>
                                                            {post.platform === 'facebook' ? 'f' : 'WA'}
                                                        </span>
                                                        <span className="text-white text-sm font-medium">
                                                            {post.platform}
                                                        </span>
                                                    </div>
                                                    <span className={`px-2 py-1 rounded text-xs ${getStatusBadge(post.status)}`}>
                                                        {post.status}
                                                    </span>
                                                </div>
                                                <p className="text-gray-300 text-sm mb-2 line-clamp-2">
                                                    {post.content}
                                                </p>
                                                <div className="text-gray-500 text-xs">
                                                    {formatDate(post.created_at)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <div className="text-gray-400 mb-2">No posts yet</div>
                                        <p className="text-gray-500 text-sm">
                                            Create your first post to see activity here
                                        </p>
                                    </div>
                                )}
                                
                                {posts.length > 5 && (
                                    <div className="mt-6 text-center">
                                        <Link
                                            to="/posts"
                                            className="text-blue-400 hover:text-blue-300 text-sm"
                                        >
                                            View All Activity →
                                        </Link>
                                    </div>
                                )}
                            </div>

                            {/* Quick Stats */}
                            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mt-8">
                                <h2 className="text-xl font-bold text-white mb-4">AI Agent Status</h2>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">Facebook Access</span>
                                        <span className="text-green-400">✅ Active</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">WhatsApp Access</span>
                                        <span className="text-yellow-400">⚠️ Not Connected</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">AI Model</span>
                                        <span className="text-green-400">✅ Ready</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">Auto-posting</span>
                                        <span className="text-blue-400">⏸️ Paused</span>
                                    </div>
                                </div>
                                
                                <button className="w-full mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                                    Configure AI Settings
                                </button>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}