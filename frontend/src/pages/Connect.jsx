import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api';

const PlatformConnectCard = ({ platform, title, description, icon, onConnect, loading, connectedAccount }) => {
    const isConnected = !!connectedAccount;
    
    return (
        <div className={`p-8 rounded-[2rem] border transition-all duration-500 group relative overflow-hidden ${
            isConnected 
            ? 'bg-emerald-500/5 border-emerald-500/20 shadow-[0_0_50px_-12px_rgba(16,185,129,0.1)]' 
            : 'bg-white/5 border-white/10 hover:border-white/20'
        }`}>
            {/* Connection Glow */}
            {isConnected && (
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-[60px] -mr-16 -mt-16 animate-pulse" />
            )}

            <div className="flex items-center justify-between mb-8">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110 ${
                    isConnected ? 'bg-emerald-500 text-black' : 'bg-white/10 text-white'
                }`}>
                    {icon}
                </div>
                {isConnected && (
                    <span className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase tracking-widest">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                        Live Node
                    </span>
                )}
            </div>

            <h3 className="text-white text-xl font-bold mb-3 tracking-tight">{title}</h3>
            <p className="text-brand-muted text-sm font-bold leading-relaxed mb-6 min-h-[48px]">
                {isConnected 
                    ? `Currently synchronizing with ${connectedAccount.account_name || 'authorized stream'}.` 
                    : description
                }
            </p>

            <button 
                onClick={onConnect}
                disabled={loading}
                className={`w-full py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.3em] transition-all relative overflow-hidden ${
                    isConnected 
                    ? 'bg-transparent text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/10' 
                    : 'bg-white text-gray-900 shadow-xl shadow-white/5 hover:scale-[1.02] active:scale-100'
                }`}
            >
                {loading ? 'Processing...' : isConnected ? 'Node Re-sync' : 'Establish Handshake'}
                {isConnected && <div className="absolute inset-0 bg-emerald-500/5 animate-pulse" />}
            </button>
        </div>
    );
};

const SocialConnect = () => {
    const [loadingPlatform, setLoadingPlatform] = useState(null);
    const [connectedAccounts, setConnectedAccounts] = useState([]);
    const [user, setUser] = useState(null);

    useEffect(() => {
        let isMounted = true;
        const fetchStatus = async () => {
            try {
                const [userRes, accountsRes] = await Promise.all([
                    api.get('/api/users/me/info'),
                    api.get('/api/oauth/accounts')
                ]);
                if (isMounted) {
                    setUser(userRes.data);
                    setConnectedAccounts(accountsRes.data);
                }
            } catch (error) {
                console.error('Handshake status check failed:', error);
            }
        };

        fetchStatus();
        return () => { isMounted = false; };
    }, []);

    const handleConnect = async (platform) => {
        setLoadingPlatform(platform);
        try {
            const res = await api.get(`/api/oauth/auth/${platform}/init`);
            window.location.href = res.data.auth_url;
        } catch (error) {
            alert(`Protocol initialization failed for ${platform}.`);
        } finally {
            setLoadingPlatform(null);
        }
    };

    const getConnectedData = (platform) => {
        return connectedAccounts.find(acc => acc.platform === platform);
    };

    return (
        <Layout user={user}>
            <div className="mb-12">
                <h1 className="text-4xl font-black text-white mb-4 tracking-tighter uppercase">Infrastructure Nodes</h1>
                <p className="text-brand-muted font-bold">Establish high-frequency handshakes with your global social clusters.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <PlatformConnectCard 
                    platform="facebook"
                    title="Meta Strategy"
                    description="Broadcast long-form narrative assets to authorized Facebook Page clusters."
                    icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>}
                    loading={loadingPlatform === 'facebook'}
                    connectedAccount={getConnectedData('facebook')}
                    onConnect={() => handleConnect('facebook')}
                />
                
                <PlatformConnectCard 
                    platform="instagram"
                    title="Instagram Pulse"
                    description="Synthesize visual nodes directly to high-engagement Instagram Boxes."
                    icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.162 6.162 6.162 6.162-2.759 6.162-6.162-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>}
                    loading={loadingPlatform === 'instagram'}
                    connectedAccount={getConnectedData('instagram')}
                    onConnect={() => handleConnect('instagram')}
                />

            </div>
        </Layout>
    );
};

export default SocialConnect;