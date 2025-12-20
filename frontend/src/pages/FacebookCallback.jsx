// src/pages/FacebookCallback.jsx
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api';
import LoadingIndicator from '../components/LoadingIndicator';

export default function FacebookCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('Connecting Facebook...');
    const [error, setError] = useState(null);

    useEffect(() => {
        const connectFacebook = async () => {
            try {
                // Extract parameters from URL
                const code = searchParams.get('code');
                const state = searchParams.get('state');
                const errorParam = searchParams.get('error');
                const errorDescription = searchParams.get('error_description');

                // Check for OAuth errors
                if (errorParam) {
                    setError(`Facebook OAuth Error: ${errorParam} - ${errorDescription}`);
                    setTimeout(() => navigate('/connect?error=facebook_oauth_failed'), 3000);
                    return;
                }

                if (!code) {
                    setError('No authorization code received from Facebook');
                    setTimeout(() => navigate('/connect?error=no_code'), 3000);
                    return;
                }

                setStatus('Exchanging code for access token...');

                // Send the code to your backend
                const response = await api.get('/api/social/auth/facebook/callback', {
                    params: { code, state }
                });

                console.log('Facebook callback response:', response.data);

                // Success - redirect to dashboard
                setTimeout(() => {
                    navigate('/dashboard?social_linked=facebook&success=true');
                }, 2000);

            } catch (err) {
                console.error('Facebook callback error:', err);
                setError(err.response?.data?.detail || err.message || 'Unknown error');
                
                // Redirect to connect page with error
                setTimeout(() => {
                    navigate('/connect?error=facebook_connection_failed');
                }, 3000);
            }
        };

        connectFacebook();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen bg-black flex items-center justify-center">
            <div className="text-center p-8 bg-gray-900/80 backdrop-blur-sm rounded-2xl border border-gray-800 max-w-md w-full mx-4">
                <div className="mb-6">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-600 to-blue-800 flex items-center justify-center">
                        <span className="text-white text-3xl font-bold">f</span>
                    </div>
                    
                    {error ? (
                        <div className="text-red-400">
                            <h2 className="text-xl font-semibold mb-2">Connection Failed</h2>
                            <p className="text-gray-300">{error}</p>
                            <div className="mt-6">
                                <div className="w-8 h-8 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                            </div>
                        </div>
                    ) : (
                        <>
                            <h2 className="text-white text-xl font-semibold mb-2">{status}</h2>
                            <p className="text-gray-400">Please wait while we connect your Facebook account...</p>
                            <div className="mt-6">
                                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                            </div>
                        </>
                    )}
                </div>
                
                <div className="text-sm text-gray-500 mt-6">
                    <p>You'll be redirected automatically in a few seconds...</p>
                    <button 
                        onClick={() => navigate('/connect')}
                        className="mt-4 px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors"
                    >
                        Go back to Connect page
                    </button>
                </div>
            </div>
        </div>
    );
}