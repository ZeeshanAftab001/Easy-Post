import React, { useState, useEffect, useRef } from 'react';
import api from '../api';
import Layout from '../components/Layout';
import { useAuth } from '@clerk/clerk-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function Chat() {
    const { getToken } = useAuth();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'SYSTEM ONLINE. Identity verified. I am your autonomous social media operator. How can I assist with your orchestration today?', timestamp: new Date() }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [user, setUser] = useState(null);
    const [metrics, setMetrics] = useState({ latency: '0ms', entropy: '0.00', packets: '0000' });
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await api.get('/api/users/me/info');
                setUser(res.data);
            } catch (err) {
                console.error("Failed to fetch operator manifest", err);
            }
        };
        fetchUser();
    }, []);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = { role: 'user', content: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await api.post('/api/ai/chat', { message: input });
            
            const aiResponse = { 
                role: 'assistant', 
                content: res.data.response, 
                status: res.data.status,
                metrics: res.data.metrics,
                timestamp: new Date() 
            };
            
            if (res.data.metrics) setMetrics(res.data.metrics);
            setMessages(prev => [...prev, aiResponse]);
        } catch (err) {
            console.error("Chat Failed:", err);
            setMessages(prev => [...prev, { 
                role: 'assistant', 
                content: '⚠️ SYSTEM ERROR: Communication channel disrupted. Please verify your connection and try again.', 
                isError: true,
                timestamp: new Date() 
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout user={user}>
            <div className="flex flex-col h-[calc(100vh-200px)] reveal">
                {/* Header */}
                <div className="mb-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="w-16 h-16 brand-gradient rounded-3xl flex items-center justify-center text-white shadow-2xl relative overflow-hidden group">
                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                            <svg className="w-8 h-8 relative z-10" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" /></svg>
                        </div>
                        <div>
                            <h1 className="text-4xl font-black text-white tracking-tighter">Operator Terminal.</h1>
                            <div className="flex items-center gap-4 mt-1">
                                <p className="text-brand-muted font-bold text-[10px] uppercase tracking-[0.3em]">ID: NOI-88-ALPHA</p>
                                <span className="w-1 h-1 rounded-full bg-white/20"></span>
                                <p className="text-brand-primary font-bold text-[10px] uppercase tracking-[0.3em]">Neural Encryption: active</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex gap-4">
                        {[
                            { label: 'Latency', value: metrics.latency, color: 'text-brand-secondary' },
                            { label: 'Entropy', value: metrics.entropy, color: 'text-brand-primary' },
                            { label: 'Packets', value: metrics.packets, color: 'text-white' }
                        ].map((stat, i) => (
                            <div key={i} className="bg-white/5 border border-white/5 px-6 py-3 rounded-2xl flex flex-col items-center min-w-[100px]">
                                <span className="text-[8px] font-black text-brand-muted uppercase tracking-widest mb-1">{stat.label}</span>
                                <span className={`text-sm font-black ${stat.color}`}>{stat.value}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Chat Container */}
                <div className="flex-1 overflow-y-auto pr-4 space-y-6 custom-scrollbar mb-8 relative">
                    <div className="absolute inset-0 pointer-events-none opacity-[0.03] z-50 overflow-hidden rounded-[40px]">
                        <div className="w-full h-full bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] animate-scanline"></div>
                    </div>
                    {messages.map((msg, idx) => (
                        <div 
                            key={idx} 
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4 duration-500`}
                        >
                            <div className={`max-w-[80%] ${
                                msg.role === 'user' 
                                ? 'bg-brand-primary text-black rounded-3xl rounded-tr-none px-6 py-4 shadow-2xl shadow-brand-primary/10' 
                                : msg.isError 
                                    ? 'bg-red-500/10 border border-red-500/20 text-red-400 rounded-3xl rounded-tl-none px-6 py-4'
                                    : 'bg-brand-card border border-white/5 text-white rounded-3xl rounded-tl-none px-6 py-4 shadow-xl'
                            }`}>
                                <div className={`text-sm ${msg.role === 'user' ? 'font-bold' : 'font-medium leading-relaxed'} prose-invert max-w-none`}>
                                    <ReactMarkdown 
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                                            ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2" {...props} />,
                                            ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                                            code: ({node, inline, ...props}) => (
                                                <code className={`${inline ? 'bg-white/10 px-1 rounded' : 'block bg-black/30 p-3 rounded-lg border border-white/5 my-2'} font-mono text-xs`} {...props} />
                                            ),
                                            strong: ({node, ...props}) => <strong className="text-brand-primary font-black" {...props} />,
                                            table: ({node, ...props}) => <div className="overflow-x-auto my-4"><table className="w-full border-collapse border border-white/10 text-xs" {...props} /></div>,
                                            th: ({node, ...props}) => <th className="border border-white/10 px-3 py-2 bg-white/5 font-black text-brand-primary uppercase tracking-tighter" {...props} />,
                                            td: ({node, ...props}) => <td className="border border-white/10 px-3 py-2" {...props} />,
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                                <div className={`mt-2 text-[8px] font-black uppercase tracking-widest opacity-50 ${msg.role === 'user' ? 'text-black' : 'text-brand-muted'}`}>
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    {msg.status === 'approval_required' && ' • ACTION_PENDING'}
                                </div>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-brand-card border border-brand-primary/20 rounded-3xl rounded-tl-none px-8 py-5 flex flex-col gap-3 shadow-2xl shadow-brand-primary/5">
                                <div className="flex gap-2 items-center">
                                    <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce delay-100"></div>
                                    <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce delay-200"></div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-[8px] font-black text-brand-primary uppercase tracking-[0.4em] animate-pulse">Transmitting_Packets</span>
                                    <div className="flex-1 h-[2px] w-24 bg-white/5 overflow-hidden">
                                        <div className="h-full bg-brand-primary w-1/3 animate-ping"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Tray */}
                <form onSubmit={handleSend} className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-brand-primary/20 to-brand-secondary/20 rounded-[32px] blur opacity-25 group-focus-within:opacity-50 transition duration-1000"></div>
                    <div className="relative flex items-center bg-brand-card border border-white/10 rounded-[28px] p-2 pr-4 shadow-2xl backdrop-blur-xl">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a command (e.g., 'Draft a post about our summer launch for Instagram')..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-white font-bold text-sm px-6 py-4 placeholder:text-gray-600 placeholder:italic placeholder:font-medium"
                        />
                        <button 
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="bg-brand-primary hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 p-4 rounded-2xl transition-all shadow-lg shadow-brand-primary/20"
                        >
                            <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                            </svg>
                        </button>
                    </div>
                </form>

                {/* Quick Actions */}
                <div className="mt-6 flex flex-wrap gap-3 opacity-60 hover:opacity-100 transition-opacity">
                    {[
                        { label: 'DRAFT_NARRATIVE', color: 'text-brand-secondary', bg: 'bg-brand-secondary/5', border: 'border-brand-secondary/20' },
                        { label: 'ANALYZE_NODES', color: 'text-brand-primary', bg: 'bg-brand-primary/5', border: 'border-brand-primary/20' },
                        { label: 'SYNC_PROTOCOL', color: 'text-white', bg: 'bg-white/5', border: 'border-white/10' },
                        { label: 'HASHTAG_MATRIX', color: 'text-blue-400', bg: 'bg-blue-400/5', border: 'border-blue-400/20' }
                    ].map(action => (
                        <button 
                            key={action.label}
                            onClick={() => setInput(action.label.replace('_', ' '))}
                            className={`text-[8px] font-black ${action.color} border ${action.border} px-4 py-2 rounded-xl transition-all uppercase tracking-[0.2em] ${action.bg} hover:scale-105 active:scale-95`}
                        >
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>
        </Layout>
    );
}
