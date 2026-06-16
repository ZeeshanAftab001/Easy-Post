import { useState, useEffect } from 'react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar
} from 'recharts';
import { useSelector, useDispatch } from 'react-redux';
import { fetchDashboardSummary } from '../store/slices/dashboardSlice';
import Layout from '../components/Layout';

const StatCard = ({ title, value, unit, icon, color }) => (
    <div className="bg-brand-card p-6 rounded-2xl border border-white/5 glow-primary transition-all group border-glow-hover">
        <div className="flex items-center gap-4 mb-4">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-white/5 text-brand-primary`}>
                {icon}
            </div>
            <p className="text-[10px] font-black text-brand-muted uppercase tracking-[0.2em]">{title}</p>
        </div>
        <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black text-white tracking-tighter">{value}</span>
            {unit && <span className="text-[10px] font-bold text-brand-primary ml-1">{unit}</span>}
        </div>
    </div>
);

export default function Dashboard() {
    const dispatch = useDispatch();
    const { summary, loading: summaryLoading } = useSelector(state => state.dashboard);
    
    // Fallback data structure for initial load safety
    const user = summary?.user || {};
    const accounts = summary?.accounts || [];
    const analytics = summary?.analytics || { summary: {}, trends: [] };

    const [range, setRange] = useState('30D');
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        dispatch(fetchDashboardSummary());
        
        const timer = setTimeout(() => setIsMounted(true), 100);
        return () => clearTimeout(timer);
    }, [dispatch]);

    const platformData = [
        { name: 'INSTAGRAM', value: accounts.some(a => a.platform === 'instagram') ? (analytics?.summary?.instagram || 1) : 0 },
        { name: 'METAFEED', value: accounts.some(a => a.platform === 'facebook') ? (analytics?.summary?.facebook || 1) : 0 },
        { name: 'WHATSAPP', value: 1 },
    ].sort((a, b) => b.value - a.value);

    if (summaryLoading && !summary) {
        return (
            <Layout user={user}>
                <div className="min-h-[60vh] flex flex-col items-center justify-center">
                    <div className="relative w-24 h-24 mb-8">
                        <div className="absolute inset-0 border-4 border-brand-primary/20 rounded-full" />
                        <div className="absolute inset-0 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
                        <div className="absolute inset-4 border-2 border-brand-primary/40 border-b-transparent rounded-full animate-spin-slow" />
                    </div>
                    <h2 className="text-white text-xl font-black uppercase tracking-[0.5em] mb-2 animate-pulse">Initializing System</h2>
                    <p className="text-brand-primary text-[10px] font-black uppercase tracking-[0.3em] opacity-60">Synchronizing Global Social Clusters...</p>
                    
                    <div className="mt-12 grid grid-cols-3 gap-4 w-full max-w-md">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-1 bg-white/5 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-brand-primary animate-progress" 
                                    style={{ animationDelay: `${i * 200}ms` }} 
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout user={user}>
            <div className="flex justify-between items-end mb-12">
                <div className="reveal">
                    <h1 className="text-5xl font-black text-white tracking-tighter uppercase mb-1">Infrastructure Control</h1>
                    <p className="text-brand-primary text-[10px] font-black uppercase tracking-[0.5em] glow-text">Real-time Node Monitoring Status: Online</p>
                </div>
                <div className="bg-brand-card p-1 rounded-xl flex gap-1 border border-white/5">
                    {['7D', '30D', '90D'].map(t => (
                        <button
                            key={t}
                            onClick={() => setRange(t)}
                            className={`px-6 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${(range === t)
                                    ? 'bg-brand-primary text-black'
                                    : 'text-gray-500 hover:text-white'
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-12 reveal" style={{ animationDelay: '100ms' }}>
                <StatCard title="Active Nodes" value={accounts.length + 1} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4.5 4.5 0 00-5.656 0l-4 4a4.5 4.5 0 105.656 5.656l1.102-1.101m-.758-4.899a4.5 4.5 0 005.656 0l4-4a4.5 4.5 0 00-5.656-5.656l-1.1 1.1" /></svg>} />
                <StatCard title="Deployments" value={analytics?.summary?.total || 0} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>} />
                <StatCard title="Sync Queue" value={analytics?.summary?.scheduled || 0} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
                <StatCard title="Impressions" value="0.0K" icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>} />
                <StatCard title="Uptime" value="100" unit="%" icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 reveal" style={{ animationDelay: '200ms' }}>
                {/* Chart 1 - Area Chart */}
                <div className="lg:col-span-2 bg-brand-card p-8 rounded-3xl border border-white/5 relative overflow-hidden group">
                    <div className="flex items-center justify-between mb-10">
                        <div className="flex items-center gap-3">
                            <div className="w-1 h-4 bg-brand-primary rounded-full shadow-[0_0_10px_#ccff00]" />
                            <h3 className="text-[10px] font-black text-white uppercase tracking-[0.4em]">Broadcast Velocity</h3>
                        </div>
                        <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded-md">Live Stream</span>
                    </div>

                    {/* Fixed: Added explicit min-height and conditional rendering */}
                    <div className="h-[350px] w-full min-h-[350px]">
                        {isMounted && analytics.trends.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={analytics.trends}>
                                    <defs>
                                        <linearGradient id="colorLime" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#ccff00" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#ccff00" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                    <XAxis dataKey="name" stroke="#525252" fontSize={10} fontWeight="900" tickLine={false} axisLine={false} dy={10} />
                                    <YAxis stroke="#525252" fontSize={10} fontWeight="900" tickLine={false} axisLine={false} />
                                    <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #1a1a1a', borderRadius: '8px', color: '#ccff00' }} />
                                    <Area type="stepAfter" dataKey="posts" stroke="#ccff00" strokeWidth={3} fillOpacity={1} fill="url(#colorLime)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full w-full flex items-center justify-center border border-white/5 rounded-2xl bg-white/[0.01]">
                                <p className="text-brand-muted font-black text-[10px] uppercase tracking-widest italic opacity-50">
                                    {isMounted ? "Awaiting Signal Ignition..." : "Loading..."}
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Chart 2 - Bar Chart */}
                <div className="bg-brand-card p-8 rounded-3xl border border-white/5 relative overflow-hidden">
                    <h3 className="text-[10px] font-black text-white mb-10 uppercase tracking-[0.4em]">Node Allocation</h3>
                    <div className="h-[250px] w-full min-h-[250px]">
                        {isMounted && platformData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={platformData} layout="vertical">
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="name" type="category" stroke="#525252" fontSize={9} fontWeight="900" tickLine={false} axisLine={false} width={80} />
                                    <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: '#000', border: '1px solid #1a1a1a', borderRadius: '8px' }} />
                                    <Bar dataKey="value" fill="#ccff00" radius={[0, 4, 4, 0]} barSize={10} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full w-full flex items-center justify-center border border-white/5 rounded-2xl bg-white/[0.01]">
                                <p className="text-brand-muted font-black text-[10px] uppercase tracking-widest italic opacity-50">Loading data...</p>
                            </div>
                        )}
                    </div>

                    <div className="mt-8 space-y-4">
                        <h4 className="text-[9px] font-black text-brand-muted uppercase tracking-[0.4em]">Operational Status</h4>
                        <div className="grid grid-cols-1 gap-2">
                            {accounts.map(acc => (
                                <div key={acc.id} className="flex justify-between items-center bg-white/5 px-4 py-3 rounded-lg border border-white/5 hover:border-brand-primary/30 transition-all group">
                                    <div className="flex flex-col gap-1">
                                        <span className="text-[10px] font-black text-white uppercase tracking-widest">{acc.platform} Node</span>
                                        <div className="flex gap-2">
                                            <span className="text-[8px] font-black text-brand-muted uppercase tracking-widest">Lat: <span className="text-brand-secondary">{(Math.random() * 50 + 10).toFixed(0)}ms</span></span>
                                            <span className="text-[8px] font-black text-brand-muted uppercase tracking-widest">Status: <span className="text-brand-primary">Synchronized</span></span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 bg-brand-primary rounded-full shadow-[0_0_8px_#ccff00] animate-pulse" />
                                        <span className="text-[9px] font-black text-brand-primary uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Operational</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}