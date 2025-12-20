// components/SocialConnect.jsx
import { useState, useEffect } from 'react';
import api from '../api';
import Navbar from '../components/Navbar';

export default function SocialConnect() {
    const [loading, setLoading] = useState(false);
    const [facebookLoading, setFacebookLoading] = useState(false);
    const [instagramLoading, setInstagramLoading] = useState(false);
    const [oauthStatus, setOauthStatus] = useState(null);

    // Check OAuth status on component mount
    useEffect(() => {
        checkOAuthStatus();
    }, []);

    const checkOAuthStatus = async () => {
        try {
            // Check if OAuth endpoints are available
            const response = await api.get('/api/oauth/status');
            console.log('OAuth Status:', response.data);
            setOauthStatus(response.data);
        } catch (error) {
            console.error('Failed to check OAuth status:', error);
            setOauthStatus({
                error: 'OAuth endpoints not available',
                details: error.message
            });
        }
    };

    const connectFacebook = async () => {
        setFacebookLoading(true);
        try {
            // CORRECT ENDPOINT: /api/oauth/social/auth/facebook/init
            const response = await api.get('/api/oauth/social/auth/facebook/init');
            console.log('Facebook OAuth Response:', response.data);
            
            if (response.data.auth_url) {
                // Redirect user to Facebook OAuth
                window.location.href = response.data.auth_url;
            } else {
                alert('Facebook OAuth URL not returned. Check backend configuration.');
            }
        } catch (error) {
            console.error('Failed to initiate Facebook OAuth:', error);
            console.error('Error details:', error.response?.data);
            
            let errorMessage = 'Failed to connect Facebook';
            if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            alert('Error: ' + errorMessage);
        } finally {
            setFacebookLoading(false);
        }
    };

    const connectInstagram = async () => {
        setInstagramLoading(true);
        try {
            // CORRECT ENDPOINT: /api/oauth/social/auth/instagram/init
            const response = await api.get('/api/oauth/social/auth/instagram/init');
            console.log('Instagram OAuth Response:', response.data);
            
            if (response.data.auth_url) {
                // Redirect user to Instagram OAuth
                window.location.href = response.data.auth_url;
            } else {
                alert('Instagram OAuth URL not returned. Check backend configuration.');
            }
        } catch (error) {
            console.error('Failed to initiate Instagram OAuth:', error);
            console.error('Error details:', error.response?.data);
            
            let errorMessage = 'Failed to connect Instagram';
            if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            alert('Error: ' + errorMessage);
        } finally {
            setInstagramLoading(false);
        }
    };

    // Test all possible endpoints
    const testEndpoints = async () => {
        const endpoints = [
            '/api/oauth/status',
            '/api/oauth/social/auth/facebook/init',
            '/api/oauth/social/auth/instagram/init',
            '/social/auth/facebook/init',  // Your current call
            '/social/auth/instagram/init'  // Your current call
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await api.get(endpoint);
                console.log(`✅ ${endpoint}:`, response.status, response.data);
            } catch (error) {
                console.log(`❌ ${endpoint}:`, error.response?.status || error.message);
            }
        }
    };

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
                <Navbar />

                <main className="container mx-auto px-4 py-8">
                    {/* Debug Panel - Remove in production */}
                    <div className="mb-6 p-4 bg-gray-800 rounded-lg">
                        <button 
                            onClick={testEndpoints}
                            className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 mb-2"
                        >
                            Test All Endpoints
                        </button>
                        {oauthStatus && (
                            <div className="text-sm text-gray-300 mt-2">
                                <p>OAuth Status: {JSON.stringify(oauthStatus)}</p>
                            </div>
                        )}
                    </div>

                    <div className="max-w-2xl mx-auto">
                        <div className="p-6 bg-gray-900 rounded-lg border border-gray-800">
                            <h2 className="text-2xl font-bold text-white mb-4">Connect Social Accounts</h2>
                            <p className="text-gray-400 mb-6">
                                Connect your social media accounts to enable AI-powered automatic posting.
                            </p>

                            <div className="space-y-4">
                                {/* Facebook Card */}
                                <div className="p-4 border border-gray-700 rounded-lg hover:border-blue-500 transition-colors">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">f</span>
                                            </div>
                                            <div>
                                                <h3 className="text-white font-semibold">Facebook</h3>
                                                <p className="text-gray-400 text-sm">Post to Facebook Pages and Groups</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={connectFacebook}
                                            disabled={facebookLoading}
                                            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition-colors"
                                        >
                                            {facebookLoading ? 'Connecting...' : 'Connect Facebook'}
                                        </button>
                                    </div>
                                    <div className="mt-3 text-xs text-gray-500">
                                        Endpoint: <code>/api/oauth/social/auth/facebook/init</code>
                                    </div>
                                </div>

                                {/* Instagram Card */}
                                <div className="p-4 border border-gray-700 rounded-lg hover:border-pink-500 transition-colors">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">IG</span>
                                            </div>
                                            <div>
                                                <h3 className="text-white font-semibold">Instagram</h3>
                                                <p className="text-gray-400 text-sm">Post to Instagram Feed and Stories</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={connectInstagram}
                                            disabled={instagramLoading}
                                            className="px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-lg disabled:opacity-50 transition-colors"
                                        >
                                            {instagramLoading ? 'Connecting...' : 'Connect Instagram'}
                                        </button>
                                    </div>
                                    <div className="mt-3 text-xs text-gray-500">
                                        Endpoint: <code>/api/oauth/social/auth/instagram/init</code>
                                    </div>
                                </div>
                            </div>

                            {/* Instructions */}
                            <div className="mt-8 p-4 bg-gray-800 rounded-lg">
                                <h4 className="text-white font-semibold mb-2">ℹ️ How it works:</h4>
                                <ul className="text-gray-400 text-sm space-y-1">
                                    <li>1. Click "Connect" button for the platform</li>
                                    <li>2. You'll be redirected to Facebook/Instagram login</li>
                                    <li>3. Grant permissions for posting</li>
                                    <li>4. You'll be redirected back to the app</li>
                                    <li>5. Your AI agent will then be able to post automatically</li>
                                </ul>
                            </div>

                            {/* Troubleshooting */}
                            <div className="mt-4 p-4 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
                                <h4 className="text-yellow-300 font-semibold mb-2">⚠️ Getting 404 Error?</h4>
                                <p className="text-yellow-200/80 text-sm">
                                    Make sure your backend is running and OAuth routes are registered.
                                    Check browser console for detailed error information.
                                </p>
                                <p className="text-gray-400 text-xs mt-2">
                                    Current API Base URL: <code>{api.defaults.baseURL}</code>
                                </p>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}