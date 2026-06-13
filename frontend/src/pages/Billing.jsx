import React, { useState, useEffect } from 'react';
import api from '../api';
import Layout from '../components/Layout';

const PlanCard = ({ name, price, features, current, recommended, onUpgrade }) => (
    <div className={`p-10 rounded-[48px] border reveal ${current ? 'border-brand-primary bg-brand-primary/5' : 'border-white/5 bg-brand-card'} relative overflow-hidden group transition-all hover:shadow-2xl`}>
        {recommended && (
            <div className="absolute top-8 right-8 brand-gradient text-black text-[10px] font-black px-4 py-1.5 rounded-full uppercase tracking-widest shadow-lg shadow-brand-primary/20">
                Strategic Choice
            </div>
        )}
        <h3 className="text-[10px] font-black text-brand-muted uppercase tracking-[0.3em] mb-6">{name}</h3>
        <div className="flex items-baseline gap-1 mb-8">
            <span className="text-4xl font-black text-white tracking-tighter">Rs. {price.toLocaleString()}</span>
            <span className="text-brand-muted font-bold text-sm">/mo</span>
        </div>
        <ul className="space-y-5 mb-10">
            {features.map((f, i) => (
                <li key={i} className="flex items-center gap-3 text-sm font-bold text-white">
                    <svg className="w-5 h-5 text-brand-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" d="M5 13l4 4L19 7"/></svg>
                    {f}
                </li>
            ))}
        </ul>
        <button 
            onClick={() => !current && onUpgrade(name, price)}
            className={`w-full py-5 rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] transition-all ${
                current 
                ? 'bg-white/5 text-brand-primary border border-brand-primary/30 cursor-default' 
                : 'bg-white text-gray-900 hover:scale-[1.02] shadow-xl shadow-white/5'
            }`}
        >
            {current ? 'Active Subscription' : 'Upgrade via Easypaisa'}
        </button>
    </div>
);

export default function Billing() {
    const [user, setUser] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showWalletModal, setShowWalletModal] = useState(false);
    const [walletNumber, setWalletNumber] = useState('');
    const [linking, setLinking] = useState(false);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const res = await api.get('/api/users/me/info');
            setUser(res.data);
            if (res.data.whatsapp_number) setWalletNumber(res.data.whatsapp_number);
        } catch (err) {
            console.error("Failed to fetch billing manifest", err);
        }
    };

    const handleUpgrade = (plan, price) => {
        if (!user?.whatsapp_number) {
            alert("Protocol Error: Please connect your Easypaisa wallet first.");
            setShowWalletModal(true);
            return;
        }
        setIsProcessing(true);
        setTimeout(() => {
            alert(`Initializing Easypaisa Handshake for ${plan} (Rs. ${price.toLocaleString()}). Redirecting to payment portal...`);
            setIsProcessing(false);
        }, 1500);
    };

    const handleConnectWallet = async () => {
        if (!walletNumber) return;
        setLinking(true);
        try {
            await api.patch('/api/users/me', { whatsapp_number: walletNumber });
            await fetchUser();
            setShowWalletModal(false);
            alert("Easypaisa Wallet Linked Successfully.");
        } catch (err) {
            alert("Wallet Handshake Failed.");
        } finally {
            setLinking(false);
        }
    };

    return (
        <Layout user={user}>
            <div className="mb-16 reveal">
                <div className="flex justify-between items-end">
                    <div>
                        <h1 className="text-5xl font-black text-white tracking-tighter">Financial Infrastructure</h1>
                        <p className="text-brand-muted mt-2 font-bold text-sm uppercase tracking-widest">Resource Allocation (PKR) & Local Payment Nodes</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <PlanCard 
                    name="Operator"
                    price={0}
                    features={['2 Managed Nodes', 'Basic Intelligence', 'WhatsApp Agent', 'Daily Deploy Limit: 5']}
                    current={user?.subscription_tier === 'Free Tier' || !user?.subscription_tier}
                />
                <PlanCard 
                    name="Strategist"
                    price={9999}
                    features={['10 Managed Nodes', 'Advanced Strategy AI', 'Custom Brand Voices', 'Scheduled Assets', 'Priority API Routing']}
                    recommended={true}
                    onUpgrade={handleUpgrade}
                />
                <PlanCard 
                    name="Enterprise"
                    price={39999}
                    features={['Unlimited Nodes', 'Custom Model Fine-tuning', 'White-label Reports', 'Dedicated Support Node', 'API Access']}
                    onUpgrade={handleUpgrade}
                />
            </div>
            
            <div className="mt-12 bg-brand-card p-10 rounded-[48px] border border-white/5 flex flex-col md:flex-row justify-between items-center reveal group overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand-secondary/5 rounded-full blur-3xl -translate-y-32 translate-x-32" />
                
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <img src="https://img.icons8.com/color/48/000000/easypaisa.png" alt="Easypaisa" className="w-8 h-8 rounded-lg" />
                        <h4 className="text-sm font-black text-white uppercase tracking-widest">Easypaisa Verification Active</h4>
                    </div>
                    <p className="text-brand-muted text-sm font-bold">
                        {user?.whatsapp_number 
                            ? `Wallet Linked: ${user.whatsapp_number}` 
                            : 'Local payments optimized for Pakistan. Instant activation via mobile account.'}
                    </p>
                </div>
                
                <div className="flex gap-4 mt-8 md:mt-0 relative z-10">
                    <button className="px-8 py-4 bg-white/5 text-[10px] font-black text-white uppercase tracking-[0.2em] rounded-2xl border border-white/10 hover:bg-white/10 transition-all">
                        Transaction History
                    </button>
                    <button 
                        onClick={() => setShowWalletModal(true)}
                        className={`px-8 py-4 ${user?.whatsapp_number ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'brand-gradient text-black'} text-[10px] font-black uppercase tracking-[0.2em] rounded-2xl shadow-xl shadow-brand-primary/20 hover:scale-105 active:scale-100 transition-all`}
                    >
                        {user?.whatsapp_number ? 'Wallet Connected' : 'Connect Wallet'}
                    </button>
                </div>
            </div>

            {/* Wallet Connection Modal */}
            {showWalletModal && (
                <div className="fixed inset-0 bg-black/90 backdrop-blur-xl flex items-center justify-center z-[110] p-6">
                    <div className="bg-brand-card border border-white/10 p-10 rounded-[48px] max-w-lg w-full reveal shadow-2xl">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-16 h-16 bg-white/5 rounded-3xl flex items-center justify-center">
                                <img src="https://img.icons8.com/color/48/000000/easypaisa.png" alt="Easypaisa" className="w-10 h-10" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Connect Easypaisa</h2>
                                <p className="text-brand-muted text-[10px] font-black uppercase tracking-widest">Mobile Wallet Handshake</p>
                            </div>
                        </div>

                        <div className="space-y-6 mb-10">
                            <div>
                                <label className="text-[10px] font-black text-brand-muted uppercase tracking-widest block mb-3 pl-2">Easypaisa Mobile Number</label>
                                <input 
                                    type="text"
                                    value={walletNumber}
                                    onChange={(e) => setWalletNumber(e.target.value)}
                                    placeholder="e.g., 03001234567"
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-white font-bold focus:outline-none focus:ring-4 focus:ring-brand-primary/20 transition-all"
                                />
                            </div>
                            <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest leading-relaxed opacity-60">
                                By connecting your wallet, you authorize EasyPost to initiate secure payment requests to your Easypaisa account for future upgrades.
                            </p>
                        </div>

                        <div className="flex gap-4">
                            <button 
                                onClick={handleConnectWallet}
                                disabled={linking || !walletNumber}
                                className="flex-1 py-5 brand-gradient text-black font-black text-xs uppercase tracking-[0.2em] rounded-2xl hover:scale-[1.02] active:scale-100 transition-all disabled:opacity-50"
                            >
                                {linking ? 'Handshaking...' : 'Authorize Wallet'}
                            </button>
                            <button 
                                onClick={() => setShowWalletModal(false)}
                                className="px-8 py-5 bg-white/5 text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl hover:bg-white/10 transition-all"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {isProcessing && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[100]">
                    <div className="text-center">
                        <div className="w-20 h-20 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto mb-8 shadow-2xl shadow-brand-primary/20"></div>
                        <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-2">Easypaisa Node Initializing</h2>
                        <p className="text-brand-muted font-bold text-sm uppercase tracking-widest animate-pulse">Requesting secure handshake with payment gateway...</p>
                    </div>
                </div>
            )}
        </Layout>
    );
}
