import React, { useState, useEffect, useRef } from 'react';
import api, { setAuthToken } from '../api';
import Layout from '../components/Layout';
import { useAuth } from '@clerk/clerk-react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchUser } from '../store/slices/authSlice';
import { fetchKnowledgeBase, updateProfileField, setStatus, clearStatus } from '../store/slices/settingsSlice';
import * as pdfjs from 'pdfjs-dist';

// Define the worker script path - using a stable version and non-mjs fallback for better CDN compatibility
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;

const SettingRow = ({ label, value, onUpdate, field, type = "text" }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [tempValue, setTempValue] = useState(value);

    const handleSave = () => {
        onUpdate(field, tempValue);
        setIsEditing(false);
    };

    return (
        <div className="py-8 flex items-center justify-between border-b border-white/5 last:border-0 hover:bg-white/[0.02] px-6 rounded-3xl transition-all group">
            <div className="flex-1">
                <h4 className="text-[10px] font-black text-brand-muted uppercase tracking-[0.2em] mb-2">{label}</h4>
                {isEditing ? (
                    <input
                        type={type}
                        value={tempValue}
                        onChange={(e) => setTempValue(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm font-bold text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 w-full max-w-md"
                        autoFocus
                    />
                ) : (
                    <p className="text-sm font-bold text-white group-hover:text-brand-secondary transition-colors">{value || 'Not Configured'}</p>
                )}
            </div>
            <div className="flex gap-2">
                {isEditing ? (
                    <>
                        <button
                            onClick={handleSave}
                            className="text-[10px] font-black text-black bg-brand-primary px-6 py-2.5 rounded-xl hover:opacity-90 transition-all uppercase tracking-widest"
                        >
                            Save
                        </button>
                        <button
                            onClick={() => { setIsEditing(false); setTempValue(value); }}
                            className="text-[10px] font-black text-brand-muted bg-white/5 px-6 py-2.5 rounded-xl hover:bg-white/10 transition-all uppercase tracking-widest"
                        >
                            Cancel
                        </button>
                    </>
                ) : (
                    <button
                        onClick={() => setIsEditing(true)}
                        className="text-[10px] font-black text-brand-secondary bg-brand-secondary/10 px-6 py-2.5 rounded-xl hover:bg-brand-secondary/20 transition-all uppercase tracking-widest"
                    >
                        Configure
                    </button>
                )}
            </div>
        </div>
    );
};

export default function Settings() {
    const { getToken } = useAuth();
    const dispatch = useDispatch();
    const { user } = useSelector(state => state.auth);
    const { combinedKnowledge, status, loading: settingsLoading } = useSelector(state => state.settings);
    
    // We keep a local state for the textarea edit
    const [localKnowledge, setLocalKnowledge] = useState('');
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        dispatch(fetchUser());
        dispatch(fetchKnowledgeBase());
    }, [dispatch]);

    useEffect(() => {
        if (combinedKnowledge) {
            setLocalKnowledge(combinedKnowledge);
        }
    }, [combinedKnowledge]);

    const updateProfile = async (field, value) => {
        await dispatch(updateProfileField({ [field]: value }));
        dispatch(fetchUser()); // Refresh user in auth slice
        setTimeout(() => dispatch(clearStatus()), 3000);
    };

    const saveKnowledge = async () => {
        if (!localKnowledge.trim()) return;
        dispatch(setStatus('Indexing Vectors...'));
        try {
            await api.post('/api/ai/knowledge/', {
                category: "brand_voice",
                content: localKnowledge
            });
            dispatch(setStatus('Knowledge Secured.'));
            dispatch(fetchKnowledgeBase());
            setTimeout(() => dispatch(clearStatus()), 3000);
        } catch (err) {
            dispatch(setStatus('Indexing Failed.'));
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Validation
        const MAX_SIZE = 10 * 1024 * 1024;
        const ALLOWED_TYPES = ['application/pdf', 'text/plain'];

        if (file.size > MAX_SIZE) {
            setStatus('File too large. Maximum size is 10MB.');
            setTimeout(() => setStatus(''), 5000);
            return;
        }

        if (!ALLOWED_TYPES.includes(file.type)) {
            setStatus('Invalid file type. Please upload PDF or TXT files only.');
            setTimeout(() => setStatus(''), 5000);
            return;
        }

        setUploading(true);
        setStatus('Extracting text from file...');

        try {
            let extractedText = '';

            // Extract text
            if (file.type === 'text/plain') {
                extractedText = await extractTextFromTXT(file);
            } else if (file.type === 'application/pdf') {
                extractedText = await extractTextFromPDF(file);
            }

            if (!extractedText || extractedText.trim().length === 0) {
                throw new Error('No text content found in file');
            }

            setStatus('Adding to knowledge base...');

            // Get Clerk token
            const token = await getToken();
            console.log('Token obtained:', token ? 'Yes' : 'No');

            if (!token) {
                throw new Error('No authentication token available. Please ensure you are logged in.');
            }

            // Set the token for the api instance
            setAuthToken(token);

            // Make request
            const response = await api.post('/api/ai/knowledge/', {
                category: determineCategory(file.name),
                content: extractedText
            });

            dispatch(setStatus(`✓ Successfully added "${file.name}" to knowledge base`));
            dispatch(fetchKnowledgeBase());
            setTimeout(() => dispatch(clearStatus()), 5000);

            return response.data;

        } catch (err) {
            console.error('Upload error:', err);

            if (err.response?.status === 401) {
                dispatch(setStatus('Authentication failed. Please try logging out and back in.'));
            } else {
                const errorMessage = err.response?.data?.detail || err.message || 'Processing failed';
                dispatch(setStatus(`✗ Failed: ${errorMessage}`));
            }

            setTimeout(() => dispatch(clearStatus()), 5000);
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    // Helper functions
    const extractTextFromTXT = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error('Failed to read TXT file'));
            reader.readAsText(file);
        });
    };

    const extractTextFromPDF = async (file) => {
        try {
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;
            let fullText = '';
            
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const textContent = await page.getTextContent();
                const pageText = textContent.items.map(item => item.str).join(' ');
                fullText += pageText + '\n';
            }
            
            return fullText;
        } catch (error) {
            console.error('PDF Extraction Error:', error);
            throw new Error(`PDF extraction failed: ${error.message}`);
        }
    };

    // Optional: Smart category detection based on filename
    const determineCategory = (filename) => {
        const lowerName = filename.toLowerCase();

        if (lowerName.includes('brand') || lowerName.includes('guideline')) {
            return 'brand_voice';
        } else if (lowerName.includes('audience') || lowerName.includes('persona')) {
            return 'audience';
        } else if (lowerName.includes('policy') || lowerName.includes('rule')) {
            return 'guidelines';
        } else {
            return 'general'; // Default category
        }
    };

    return (
        <Layout user={user}>
            <div className="mb-16 reveal">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-5xl font-black text-white tracking-tighter">System Configuration</h1>
                        <p className="text-brand-muted mt-2 font-bold text-sm uppercase tracking-widest">Global Variables & Strategy Nodes</p>
                    </div>
                    {status && (
                        <div className="px-6 py-2 bg-brand-primary/10 border border-brand-primary/20 rounded-full shadow-2xl shadow-brand-primary/10 transition-all">
                            <span className="text-[10px] font-black text-brand-primary uppercase animate-pulse">{status}</span>
                        </div>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
                <div className="bg-brand-card p-10 rounded-[48px] border border-white/5 shadow-2xl reveal">
                    <h2 className="text-sm font-black text-white mb-10 uppercase tracking-widest">Operator Architecture</h2>
                    <div className="space-y-2">
                        <SettingRow
                            label="Identity Manifest (Username)"
                            value={user?.username}
                            field="username"
                            onUpdate={updateProfile}
                        />
                        <div className="py-8 px-6 flex flex-col border-b border-white/5 last:border-0 opacity-50 cursor-not-allowed">
                            <h4 className="text-[10px] font-black text-brand-muted uppercase tracking-[0.2em] mb-2">Communication Root (Email)</h4>
                            <p className="text-sm font-bold text-white">{user?.email}</p>
                            <span className="text-[8px] font-black text-brand-muted mt-1 uppercase tracking-widest">Managed by Clerk Auth</span>
                        </div>
                        <SettingRow
                            label="Operation Niche"
                            value={user?.niche}
                            field="niche"
                            onUpdate={updateProfile}
                        />
                    </div>
                </div>

                <div className="bg-brand-card p-10 rounded-[48px] border border-white/5 shadow-2xl reveal" style={{ animationDelay: '100ms' }}>
                    <h2 className="text-sm font-black text-white mb-10 uppercase tracking-widest">AI Context (RAG)</h2>
                    <div className="space-y-6">
                        <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest leading-relaxed">
                            Inject long-term context into your AI agent via text or documents.
                        </p>

                        <textarea
                            value={localKnowledge}
                            onChange={(e) => setLocalKnowledge(e.target.value)}
                            placeholder="Manually enter brand guidelines or preferences..."
                            className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-sm font-bold text-white placeholder:text-gray-700 min-h-[120px] focus:outline-none focus:ring-4 focus:ring-brand-primary/20 transition-all font-mono"
                        />

                        <div className="flex gap-4">
                            <button
                                onClick={saveKnowledge}
                                className="flex-1 py-4 brand-gradient rounded-2xl text-black font-black text-xs uppercase tracking-[0.2em] hover:scale-[1.02] active:scale-100 transition-all shadow-xl shadow-brand-primary/20"
                            >
                                Sync Text Context
                            </button>

                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileUpload}
                                className="hidden"
                                accept=".pdf,.txt"
                            />

                            <button
                                onClick={() => fileInputRef.current?.click()}
                                disabled={uploading}
                                className="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-white/10 transition-all disabled:opacity-50"
                            >
                                {uploading ? 'Processing...' : 'Upload PDF'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
                <div className="bg-brand-card p-10 rounded-[48px] border border-white/5 shadow-2xl reveal flex flex-col justify-between relative overflow-hidden group/card" style={{ animationDelay: '200ms' }}>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-brand-primary/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover/card:bg-brand-primary/10 transition-all"></div>
                    
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h2 className="text-sm font-black text-white uppercase tracking-widest">WhatsApp Hook</h2>
                            {user?.verification_status === 'verified' && (
                                <div className="p-1 bg-brand-primary/20 rounded-lg">
                                    <svg className="w-3 h-3 text-brand-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>
                            )}
                        </div>
                        <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest mb-8">Direct Broadcast Node</p>
                    </div>

                    <div className="relative z-10">
                        <div className={`p-1 rounded-3xl transition-all ${user?.verification_status === 'pending' && user?.whatsapp_number !== 'TBD' ? 'bg-amber-500/10 border border-amber-500/20' : ''}`}>
                            <SettingRow
                                label="Verified Number"
                                value={user?.whatsapp_number}
                                field="whatsapp_number"
                                onUpdate={updateProfile}
                            />
                        </div>

                        {user?.whatsapp_number && user?.whatsapp_number !== 'TBD' && (
                            <div className="mt-6">
                                {user?.verification_status === 'verified' ? (
                                    <div className="flex items-center gap-3 px-6 py-4 bg-brand-primary/5 border border-brand-primary/10 rounded-2xl group/status hover:bg-brand-primary/10 transition-all cursor-default">
                                        <div className="w-2 h-2 rounded-full bg-brand-primary animate-pulse"></div>
                                        <span className="text-[9px] font-black text-brand-primary uppercase tracking-widest">
                                            Interface Active & Secured
                                        </span>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <div className="px-6 py-4 bg-amber-500/5 border border-amber-500/10 rounded-2xl">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></div>
                                                <span className="text-[9px] font-black text-amber-500 uppercase tracking-widest">
                                                    Action Required
                                                </span>
                                            </div>
                                            <p className="text-[9px] font-bold text-white/60 uppercase tracking-[0.05em] leading-relaxed">
                                                To finalize the link, please reply <span className="text-amber-500 font-black">"DONE"</span> to our WhatsApp verification message.
                                            </p>
                                        </div>
                                        <button
                                            onClick={async () => {
                                                dispatch(setStatus('Re-initializing Node...'));
                                                try {
                                                    await api.post('/api/users/me/resend-verification');
                                                    dispatch(setStatus('Transmission Sent.'));
                                                } catch (err) {
                                                    dispatch(setStatus('Transmission Failed.'));
                                                }
                                                setTimeout(() => dispatch(clearStatus()), 3000);
                                            }}
                                            className="w-full py-4 bg-white/5 border border-white/10 rounded-2xl text-[9px] font-black text-white uppercase tracking-[0.2em] hover:bg-white/10 active:scale-95 transition-all"
                                        >
                                            Resend Protocol
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-brand-card p-10 rounded-[48px] border border-white/5 shadow-2xl reveal flex flex-col justify-between relative overflow-hidden group/card" style={{ animationDelay: '300ms' }}>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-brand-secondary/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover/card:bg-brand-secondary/10 transition-all"></div>
                    <div>
                        <h2 className="text-sm font-black text-white mb-2 uppercase tracking-widest">Strategy Logic</h2>
                        <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest mb-8">AI Execution Parameters</p>
                    </div>
                    <div className="space-y-4 z-10">
                        <SettingRow
                            label="Tone Protocol"
                            value={user?.ai_tone || "Analytical"}
                            field="ai_tone"
                            onUpdate={updateProfile}
                        />
                        <SettingRow
                            label="Broadcast Cycle"
                            value={user?.broadcast_timing || "System Optimized"}
                            field="broadcast_timing"
                            onUpdate={updateProfile}
                        />
                    </div>
                </div>

                <div className="bg-brand-card p-10 rounded-[48px] border border-brand-primary/10 shadow-2xl reveal group hover:border-brand-primary/30 transition-all relative overflow-hidden" style={{ animationDelay: '400ms' }}>
                    <div className="absolute inset-0 bg-brand-primary/[0.02] group-hover:bg-brand-primary/[0.05] transition-all"></div>
                    <div className="relative z-10 h-full flex flex-col">
                        <h2 className="text-sm font-black text-brand-primary mb-2 uppercase tracking-widest">Billing Tier</h2>
                        <p className="text-[10px] font-black text-brand-muted uppercase tracking-widest mb-8">Infrastructure Access</p>
                        <div className="flex items-baseline gap-2 mb-auto">
                            <span className="text-4xl font-black text-white">Enterprise</span>
                            <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Active</span>
                        </div>
                        <button className="w-full mt-8 py-4 bg-brand-primary/10 border border-brand-primary/20 rounded-2xl text-[10px] font-black text-brand-primary uppercase tracking-[0.2em] hover:bg-brand-primary hover:text-black transition-all shadow-xl shadow-brand-primary/10">
                            Manage Subscription
                        </button>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
