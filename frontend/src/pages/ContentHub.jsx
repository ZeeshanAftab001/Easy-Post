import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchUser } from '../store/slices/authSlice';
import { fetchPosts, addPost, removePost } from '../store/slices/postSlice';
import api from '../api';
import Layout from '../components/Layout';

const ContentHub = () => {
    const dispatch = useDispatch();
    const { user, loading: authLoading } = useSelector(state => state.auth);
    const { list: posts, loading: postsLoading } = useSelector(state => state.posts);
    
    const [filter, setFilter] = useState('All Content');
    const [isModalOpen, setIsModalOpen] = useState(false);
    
    const resetForm = () => {
        setContent('');
        setMediaUrl('');
        setScheduleTime('');
        setIsScheduled(false);
        setIsModalOpen(false);
        setDeployStatus(null);
        setStatusMessage(null);
        fetchData();
    };

    const [content, setContent] = useState('');
    const [platform, setPlatform] = useState('facebook');
    const [isScheduled, setIsScheduled] = useState(false);
    const [scheduleTime, setScheduleTime] = useState('');
    const [deployStatus, setDeployStatus] = useState(null);
    const [validationErrors, setValidationErrors] = useState([]);

    const platformLimits = {
        facebook: 63206,
        instagram: 2200,
        all: 2200 // Conservative overlap
    };
    
    const [mediaUrl, setMediaUrl] = useState('');
    
    const [aiSuggestions, setAiSuggestions] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [posting, setPosting] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);

    useEffect(() => {
        dispatch(fetchUser());
        dispatch(fetchPosts());
    }, [dispatch]);

    const loading = authLoading || postsLoading;
    
    const fetchData = () => {
        dispatch(fetchPosts());
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await api.post('/api/media/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setMediaUrl(response.data.url);
        } catch (error) {
            alert('Upload failed. Infrastructure storage offline.');
        } finally {
            setUploading(false);
        }
    };

    const handleAIGenerate = async () => {
        if (!content) return alert('Enter a topic first');
        setPosting(true);
        setStatusMessage({ type: 'info', text: 'AI is optimizing your narrative...' });
        try {
            const response = await api.post('/api/ai/generate', {
                topic: content,
                platforms: [platform === 'all' ? 'facebook' : platform],
                tone: 'attractive'
            });
            setAiSuggestions(response.data.suggestions);
            if (response.data.suggestions.length > 0) {
                setStatusMessage({ type: 'success', text: 'Multiple strategic variants synthesized.' });
            }
        } catch (err) {
            setStatusMessage({ type: 'error', text: 'AI engine unavailable.' });
        } finally {
            setPosting(false);
        }
    };

    const selectSuggestion = (suggestion) => {
        const hashtags = suggestion.hashtags.map(h => h.startsWith('#') ? h : `#${h}`).join(' ');
        setContent(`${suggestion.caption}\n\n${hashtags}`);
        setAiSuggestions([]);
        setStatusMessage({ type: 'success', text: 'Asset narrative applied.' });
        setTimeout(() => setStatusMessage(null), 2000);
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (posting) return;

        setPosting(true);
        setStatusMessage({ type: 'info', text: 'Executing deployment protocol...' });

        try {
            const endpoint = isScheduled ? '/api/posts/create' : '/api/posts/instant';
            const payload = {
                content,
                platform,
                media_url: mediaUrl,
                ...(isScheduled && { schedule_time: scheduleTime })
            };

            const res = await api.post(endpoint, payload);

            if (res.data.success) {
                if (!isScheduled && res.data.results) {
                    setDeployStatus(res.data.results);
                } else {
                    setStatusMessage({ type: 'success', text: isScheduled ? 'Asset queued for future synchronization.' : 'Asset deployed successfully!' });
                }
                
                setTimeout(() => {
                    if (!isScheduled && res.data.results) {
                        // Keep deployment terminal open for a bit
                    } else {
                        resetForm();
                    }
                }, 1500);
            } else {
                throw new Error('Deployment rejected by node');
            }
        } catch (err) {
            setStatusMessage({ type: 'error', text: err.response?.data?.detail || 'Deployment sequence failure.' });
        } finally {
            setPosting(false);
        }
    };

    const broadcastExisting = async (post) => {
        setLoading(true);
        try {
            await api.post('/api/posts/instant', {
                content: post.content,
                platform: post.platform,
                media_url: post.media_url
            });
            fetchData();
        } catch (err) {
            alert('Broadcast sequence failed.');
        } finally {
            setLoading(false);
        }
    };

    const deletePost = async (id) => {
        if (!confirm('Discard this asset protocol?')) return;
        try {
            await api.delete(`/api/posts/${id}`);
            fetchData();
        } catch (err) {
            alert('Protocol rejection.');
        }
    };

    const filteredPosts = posts.filter(p => {
        if (filter === 'All Content') return true;
        return p.status.toLowerCase() === filter.toLowerCase();
    });

    if (loading && posts.length === 0) return null;

    return (
        <Layout user={user}>
            <div className="flex justify-between items-end mb-12 reveal">
                <div>
                    <h1 className="text-5xl font-black text-white tracking-tighter">Content Pipeline</h1>
                    <p className="text-brand-muted mt-2 font-bold text-sm uppercase tracking-widest">Asset Lifecycle Management</p>
                </div>
                <div className="flex gap-4">
                    <div className="relative">
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            className="appearance-none bg-brand-card border border-white/5 rounded-2xl px-8 py-4 text-[10px] font-black uppercase tracking-widest text-brand-muted shadow-2xl outline-none focus:ring-4 focus:ring-brand-primary/10 transition-all cursor-pointer pr-12"
                        >
                            <option>All Content</option>
                            <option>Published</option>
                            <option>Scheduled</option>
                            <option>Failed</option>
                        </select>
                        <div className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-brand-muted">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 9l-7 7-7-7" /></svg>
                        </div>
                    </div>
                    <button
                        onClick={() => {
                            setStatusMessage(null);
                            setIsModalOpen(true);
                        }}
                        className="bg-white text-gray-900 px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] flex items-center gap-2 hover:scale-105 transition-all shadow-xl shadow-white/5"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                        Synthesize Asset
                    </button>
                </div>
            </div>

            <div className="bg-brand-card rounded-[48px] border border-white/5 shadow-2xl overflow-hidden min-h-[400px] reveal" style={{ animationDelay: '100ms' }}>
                <div className="divide-y divide-white/[0.03]">
                    {filteredPosts.map((post) => (
                        <div key={post.id} className="p-10 hover:bg-white/[0.01] transition-colors group relative">
                            <div className="flex justify-between items-start gap-8 relative z-10">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-4 mb-6">
                                        <div className={`px-4 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest ${post.status === 'published'
                                                ? 'bg-emerald-500/10 text-emerald-400'
                                                : post.status === 'scheduled'
                                                    ? 'bg-amber-500/10 text-amber-400'
                                                    : 'bg-red-400/10 text-red-400'
                                            }`}>
                                            {post.status}
                                        </div>
                                        <div className="flex items-center gap-2 text-[10px] font-black text-brand-muted uppercase tracking-[0.2em]">
                                            {post.platform} • {new Date(post.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <h3 className="text-2xl font-bold text-white truncate mb-3 tracking-tight">
                                        {post.content.split('\n')[0] || 'Untitled Narrative'}
                                    </h3>
                                    <p className="text-brand-muted text-sm font-medium line-clamp-2 leading-relaxed max-w-4xl">
                                        {post.content}
                                    </p>
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => broadcastExisting(post)}
                                        className="w-12 h-12 rounded-2xl border border-white/5 bg-white/[0.03] flex items-center justify-center text-brand-muted hover:text-brand-secondary hover:border-brand-secondary/30 hover:scale-110 transition-all shadow-sm"
                                        title="Broadcast Now"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                                    </button>
                                    <button
                                        onClick={() => deletePost(post.id)}
                                        className="w-12 h-12 rounded-2xl border border-white/5 bg-white/[0.03] flex items-center justify-center text-brand-muted hover:text-red-400 hover:border-red-400/30 hover:scale-110 transition-all shadow-sm"
                                        title="Discard"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                    {filteredPosts.length === 0 && (
                        <div className="py-32 flex flex-col items-center justify-center text-center px-6">
                            <div className="w-20 h-20 bg-white/5 rounded-3xl flex items-center justify-center mb-8 text-white/10">
                                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                            </div>
                            <p className="text-brand-muted font-black text-[10px] uppercase tracking-[0.5em]">No assets detected in current pipeline.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Create Post Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-brand-bg/90 backdrop-blur-sm">
                    <div className="absolute inset-0" onClick={() => setIsModalOpen(false)} />
                    <div className="bg-brand-card w-full max-w-4xl rounded-[56px] border border-white/5 shadow-2xl relative overflow-hidden flex flex-col max-h-[95vh] reveal">
                        <div className="p-12 pb-6 flex justify-between items-center bg-white/[0.01] border-b border-white/5">
                            <div>
                                <h2 className="text-3xl font-black text-white tracking-tighter uppercase tracking-[0.1em] text-sm">Synthesize Asset</h2>
                                <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest mt-1">Multi-Node Deployment Sequence</p>
                            </div>
                            <button 
                                onClick={resetForm}
                                className="absolute top-10 right-10 w-12 h-12 bg-white/5 rounded-full flex items-center justify-center hover:bg-white/10 transition-all text-brand-muted hover:text-white"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>

                            {/* Deployment Terminal Overlay */}
                            {deployStatus && (
                                <div className="absolute inset-x-0 bottom-0 top-[140px] bg-brand-bg/95 backdrop-blur-3xl z-50 rounded-b-[48px] p-20 flex flex-col items-center justify-center animate-in fade-in zoom-in duration-500">
                                    <div className="max-w-2xl w-full">
                                        <div className="flex items-center gap-6 mb-16">
                                            <div className="w-16 h-16 brand-gradient rounded-3xl flex items-center justify-center text-white shadow-2xl animate-spin-slow">
                                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                                            </div>
                                            <div>
                                                <h3 className="text-3xl font-black text-white tracking-tighter">Synchronizing Nodes.</h3>
                                                <p className="text-[10px] font-black text-brand-secondary uppercase tracking-[0.5em] mt-2 opacity-70">Deployment Protocol Active</p>
                                            </div>
                                        </div>

                                        <div className="space-y-6">
                                            {deployStatus.map((node, i) => (
                                                <div key={i} className={`p-8 rounded-[32px] border flex items-center justify-between transition-all duration-700 animate-in slide-in-from-left-8`} style={{ transitionDelay: `${i * 200}ms` }}>
                                                    <div className="flex items-center gap-8">
                                                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${node.success ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'} border`}>
                                                            {node.success ? (
                                                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                                                            ) : (
                                                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" /></svg>
                                                            )}
                                                        </div>
                                                        <div>
                                                            <div className="flex items-center gap-3 mb-1">
                                                                <span className="text-[10px] font-black text-brand-muted uppercase tracking-widest">{node.platform} Node</span>
                                                                {node.success && <span className="text-[8px] font-bold text-green-500 bg-green-500/10 px-2 py-0.5 rounded-full">ACTIVE</span>}
                                                            </div>
                                                            <p className={`font-black tracking-tight ${node.success ? 'text-white' : 'text-red-500/70'}`}>
                                                                {node.success ? 'Synchronization Successful' : `Signal Disrupted: ${node.error || 'Unknown Interference'}`}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    {node.success && (
                                                        <div className="text-right">
                                                            <div className="text-[8px] font-black text-brand-muted uppercase tracking-widest mb-1">Latency</div>
                                                            <div className="text-sm font-black text-brand-secondary">{Math.round(node.latency)}ms</div>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>

                                        <button 
                                            onClick={resetForm}
                                            className="w-full mt-16 py-6 bg-white/5 border border-white/5 rounded-3xl font-black text-[10px] uppercase tracking-[0.4em] text-brand-muted hover:bg-white/10 hover:text-white transition-all shadow-sm"
                                        >
                                            Execute Final Sequence & Close
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="p-12 space-y-10 overflow-y-auto flex-1 custom-scrollbar">
                            {statusMessage && (
                                <div className={`p-5 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] animate-in fade-in slide-in-from-top-4 duration-300 ${statusMessage.type === 'success' ? 'bg-emerald-500/10 text-emerald-400' :
                                        statusMessage.type === 'error' ? 'bg-red-400/10 text-red-400' : 'bg-brand-secondary/10 text-brand-secondary'
                                    }`}>
                                    {statusMessage.text}
                                </div>
                            )}

                            <div>
                                <label className="block text-[10px] font-black text-brand-muted uppercase tracking-widest mb-4 px-1">Asset Narrative</label>
                                <textarea
                                    value={content}
                                    onChange={(e) => setContent(e.target.value)}
                                    placeholder="Define the strategic narrative..."
                                    className="w-full h-64 bg-white/[0.03] border border-white/5 rounded-[40px] p-10 text-white placeholder-gray-800 focus:ring-4 focus:ring-brand-primary/10 outline-none resize-none font-bold text-lg transition-all"
                                />
                                <div className="mt-4 flex justify-between items-center px-4">
                                    <div className="flex gap-2">
                                        {!mediaUrl && platform === 'instagram' && (
                                            <span className="text-[10px] font-black text-amber-500 uppercase tracking-widest animate-pulse flex items-center gap-2">
                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                                                Visual Node Required for {platform}
                                            </span>
                                        )}
                                    </div>
                                    <div className={`text-[10px] font-black uppercase tracking-[0.2em] flex items-center gap-3 ${content.length > platformLimits[platform] ? 'text-red-500' : 'text-brand-muted'}`}>
                                        <span className="opacity-50">Logistics Check:</span>
                                        <span className="bg-white/5 px-3 py-1 rounded-full border border-white/5">
                                            {content.length.toLocaleString()} / {platformLimits[platform].toLocaleString()}
                                        </span>
                                    </div>
                                </div>

                                <div className="mt-6 flex justify-end gap-4">
                                    {aiSuggestions.length > 0 && (
                                        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-4">
                                            {aiSuggestions.map((s, idx) => (
                                                <div 
                                                    key={idx} 
                                                    onClick={() => selectSuggestion(s)}
                                                    className="p-6 bg-white/[0.02] border border-white/5 rounded-3xl cursor-pointer hover:bg-brand-primary/5 hover:border-brand-primary/30 transition-all group relative overflow-hidden"
                                                >
                                                    <div className="absolute top-0 right-0 w-24 h-24 bg-brand-primary/5 rounded-bl-full translate-x-12 -translate-y-12 group-hover:bg-brand-primary/10 transition-all"></div>
                                                    <div className="flex justify-between items-start mb-3 relative z-10">
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-brand-secondary animate-pulse"></div>
                                                            <span className="text-[9px] font-black text-brand-secondary uppercase tracking-[0.2em]">Decrypted {s.platform === 'all' ? 'Universal' : s.platform} Path</span>
                                                        </div>
                                                        <svg className="w-4 h-4 text-brand-secondary opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                                                    </div>
                                                    <p className="text-[10px] text-brand-muted line-clamp-3 leading-relaxed font-bold group-hover:text-white transition-colors relative z-10">{s.caption}</p>
                                                    <div className="mt-4 flex flex-wrap gap-1.5 relative z-10">
                                                        {s.hashtags && s.hashtags.slice(0, 3).map((h, hi) => (
                                                            <span key={hi} className="text-[7px] font-black text-brand-primary uppercase tracking-widest px-2 py-1 bg-brand-primary/5 rounded-md border border-brand-primary/10">#{h}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    <button
                                        type="button"
                                        onClick={handleAIGenerate}
                                        disabled={posting || !content}
                                        className="h-fit text-[10px] font-black text-brand-secondary bg-brand-secondary/10 px-8 py-3.5 rounded-xl hover:bg-brand-secondary/20 transition-all flex items-center gap-3 uppercase tracking-widest self-start"
                                    >
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" /></svg>
                                        {aiSuggestions.length > 0 ? 'Retry Optimization' : 'Assistant Optimization'}
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                                <div>
                                    <label className="block text-[10px] font-black text-brand-muted uppercase tracking-widest mb-4 px-1">Visual Architecture</label>
                                    <div className="flex gap-4">
                                        <label className="flex-1 cursor-pointer group">
                                            <div className={`w-full bg-white/[0.03] border-2 border-dashed border-white/5 rounded-2xl px-8 py-5 flex items-center justify-center text-[10px] font-black text-brand-muted group-hover:border-brand-secondary/30 group-hover:bg-brand-secondary/5 transition-all uppercase tracking-widest h-[58px] ${uploading ? 'animate-pulse' : ''}`}>
                                                {uploading ? 'Syncing...' : mediaUrl ? '✅ Load Complete' : 'Upload Visual'}
                                            </div>
                                            <input type="file" className="hidden" accept="image/*" onChange={handleFileUpload} />
                                        </label>
                                        {mediaUrl && (
                                            <div className="w-14 h-14 rounded-2xl overflow-hidden border border-white/10 flex-shrink-0 bg-white/5 relative group">
                                                <img src={mediaUrl} alt="Preview" className="w-full h-full object-cover transition-transform group-hover:scale-110" />
                                                <div 
                                                    onClick={() => setMediaUrl('')}
                                                    className="absolute inset-0 bg-red-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                                >
                                                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" /></svg>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-brand-muted uppercase tracking-widest mb-4 px-1">Sync Logistics</label>
                                    <div className="flex gap-4">
                                        <button 
                                            type="button"
                                            onClick={() => setIsScheduled(!isScheduled)}
                                            className={`flex-1 h-[58px] rounded-2xl border flex items-center justify-center gap-3 transition-all ${isScheduled 
                                                ? 'bg-amber-500/10 border-amber-500/30 text-amber-500' 
                                                : 'bg-white/[0.03] border-white/5 text-brand-muted hover:border-white/20'}`}
                                        >
                                            <div className={`w-3 h-3 rounded-full ${isScheduled ? 'bg-amber-500 animate-pulse' : 'bg-white/10'}`} />
                                            <span className="text-[10px] font-black uppercase tracking-widest">{isScheduled ? 'Scheduled Mode' : 'Instant Deploy'}</span>
                                        </button>
                                        {isScheduled && (
                                            <div className="flex-1 relative animate-in zoom-in duration-300">
                                                <input 
                                                    type="datetime-local" 
                                                    value={scheduleTime}
                                                    onChange={(e) => setScheduleTime(e.target.value)}
                                                    className="w-full h-[58px] bg-white/[0.05] border border-amber-500/20 rounded-2xl px-6 text-[10px] font-black text-white outline-none focus:border-amber-500/50 transition-all uppercase"
                                                />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 gap-10">
                                <div>
                                    <label className="block text-[10px] font-black text-brand-muted uppercase tracking-widest mb-4 px-1">Channel Strategy</label>
                                    <div className="relative">
                                        <select
                                            value={platform}
                                            onChange={(e) => setPlatform(e.target.value)}
                                            className="appearance-none w-full bg-white/[0.03] border border-white/5 rounded-2xl px-8 py-5 text-xs font-black text-white focus:ring-4 focus:ring-brand-primary/10 outline-none cursor-pointer uppercase tracking-widest"
                                        >
                                            <option value="facebook">Meta Feed</option>
                                            <option value="instagram">Instagram Box</option>
                                            <option value="all">Meta Sync</option>
                                        </select>
                                        <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-brand-muted">
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 9l-7 7-7-7" /></svg>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleSubmit}
                                disabled={posting || !content || (isScheduled && !scheduleTime)}
                                className={`w-full py-7 text-white rounded-[32px] font-black text-2xl transition-all hover:scale-[1.02] active:scale-100 shadow-2xl disabled:opacity-50 uppercase tracking-[0.2em] ${isScheduled ? 'bg-amber-500 shadow-amber-500/30' : 'brand-gradient shadow-brand-primary/30'}`}
                            >
                                {posting ? 'Deploying...' : isScheduled ? 'Schedule Deployment' : 'Initiate Deployment'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </Layout>
    );
};

export default ContentHub;
