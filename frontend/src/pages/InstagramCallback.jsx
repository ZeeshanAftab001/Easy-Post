// src/pages/InstagramCallback.jsx
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api';

export default function InstagramCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('Connecting Instagram...');

    useEffect(() => {
        const connectInstagram = async () => {
            try {
                const code = searchParams.get('code');
                const state = searchParams.get('state');
                const error = searchParams.get('error');

                if (error) {
                    setStatus(`Error: ${error}`);
                    setTimeout(() => navigate('/connect?error=instagram_oauth_failed'), 3000);
                    return;
                }

                if (!code) {
                    setStatus('No authorization code received');
                    setTimeout(() => navigate('/connect?error=no_code'), 3000);
                    return;
                }

                setStatus('Processing Instagram connection...');

                // Send to backend
                const response = await api.get('/api/social/auth/instagram/callback', {
                    params: { code, state }
                });

                console.log('Instagram callback response:', response.data);

                // Success
                setTimeout(() => {
                    navigate('/dashboard?social_linked=instagram&success=true');
                }, 2000);

            } catch (err) {
                console.error('Instagram callback error:', err);
                setStatus('Error connecting Instagram');
                setTimeout(() => navigate('/connect?error=instagram_connection_failed'), 3000);
            }
        };

        connectInstagram();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen bg-black flex items-center justify-center">
            <div className="text-center">
                <div className="w-16 h-16 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <h2 className="text-white text-xl mb-2">{status}</h2>
                <p className="text-gray-400">Please wait...</p>
            </div>
        </div>
    );
}