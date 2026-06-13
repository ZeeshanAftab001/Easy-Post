import React from 'react';
import Navbar from "../components/Navbar";

const FeatureCard = ({ icon, title, description }) => (
    <div className="bg-brand-card p-12 rounded-[56px] border border-white/5 shadow-2xl hover:shadow-brand-primary/5 transition-all group overflow-hidden relative reveal">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-bl-full translate-x-16 -translate-y-16 group-hover:bg-brand-primary/10 transition-colors" />
        <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center text-brand-muted mb-10 group-hover:brand-gradient group-hover:text-white transition-all shadow-sm">
            {icon}
        </div>
        <h3 className="text-[10px] font-black text-brand-muted mb-4 uppercase tracking-[0.3em]">{title}</h3>
        <p className="text-white font-bold leading-relaxed text-lg">
            {description}
        </p>
    </div>
);

const EngineStep = ({ num, title, description }) => (
    <div className="text-center group px-6 reveal">
        <div className="w-20 h-20 bg-white/5 rounded-[32px] border border-white/10 flex items-center justify-center text-2xl font-black text-white mx-auto mb-10 shadow-sm group-hover:brand-gradient transition-all transform group-hover:rotate-6">
            {num}
        </div>
        <h3 className="text-[10px] font-black text-brand-muted mb-4 uppercase tracking-[0.4em]">{title}</h3>
        <p className="text-white font-bold text-sm max-w-[220px] mx-auto leading-relaxed group-hover:text-brand-secondary transition-colors">
            {description}
        </p>
    </div>
);

export default function Home() {
    return (
        <div className="w-full bg-brand-bg text-white min-h-screen font-medium relative selection:bg-brand-primary selection:text-white">
            {/* Background Grain/Noise or Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-brand-primary/10 blur-[150px] rounded-full -z-10 opacity-30" />
            
            <Navbar />
            
            <main>
                {/* Hero Section Refined */}
                <section className="pt-48 pb-32 px-6 text-center reveal">
                    <div className="inline-block px-4 py-2 rounded-full border border-white/10 bg-white/5 text-[10px] font-black uppercase tracking-[0.5em] text-brand-secondary mb-12 shadow-2xl">
                        Universal Deployment Protocol
                    </div>
                    <h1 className="text-7xl md:text-9xl font-black tracking-tight mb-12 max-w-6xl mx-auto leading-[0.9]">
                        Automate your <span className="brand-text-gradient animate-pan">Digital Legacy.</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-brand-muted max-w-2xl mx-auto mb-20 font-bold leading-relaxed">
                        The elite command layer for social infrastructure. Built for high-frequency operators who demand zero friction.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                        <button 
                            onClick={() => window.location.href = '/signup'}
                            className="px-12 py-6 brand-gradient rounded-full font-black text-xl hover:scale-105 active:scale-100 transition-all shadow-2xl shadow-brand-primary/30 uppercase tracking-widest"
                        >
                            Ignite System
                        </button>
                        <button className="px-12 py-6 rounded-full border border-white/10 hover:bg-white/5 transition-all text-sm font-black uppercase tracking-widest">
                            Infrastructure Docs
                        </button>
                    </div>
                </section>

                {/* Integration Grid */}
                <div className="max-w-7xl mx-auto px-6 py-20">
                    <div className="bg-brand-card rounded-[60px] p-1 border border-white/5 shadow-2xl">
                        <div className="bg-[#050505] rounded-[59px] py-12 px-20 flex flex-col md:flex-row items-center justify-between gap-12">
                            <span className="text-[10px] font-black text-brand-muted uppercase tracking-[0.5em]">Linked Ecosystems</span>
                            <div className="flex flex-wrap justify-center gap-16 opacity-30 filter grayscale invert group-hover:grayscale-0 transition-all duration-700">
                                <span className="text-2xl font-black tracking-tighter">METAFEED</span>
                                <span className="text-2xl font-black tracking-tighter">INSTAGRAM</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Features Section */}
                <section id="features" className="py-40 px-6">
                    <div className="max-w-7xl mx-auto">
                        <div className="text-center mb-32 reveal">
                            <h2 className="text-6xl md:text-8xl font-black text-white tracking-tighter mb-8">Infrastructure.</h2>
                            <p className="text-brand-muted font-black uppercase tracking-[0.4em] text-xs">Total Lifecycle Management Modules</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            <FeatureCard 
                                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>}
                                title="Autonomous Agent"
                                description="Engineered for high-fidelity communication and automated asset deployment via WhatsApp."
                            />
                            <FeatureCard 
                                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>}
                                title="Sentiment Logic"
                                description="Advanced detection of community variables to drive automated, intelligent interaction."
                            />
                            <FeatureCard 
                                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>}
                                title="Data Synthesis"
                                description="Deep-layer engagement tracking across global networks with real-time feedback loops."
                            />
                        </div>
                    </div>
                </section>

                {/* Footer Section */}
                <footer className="py-24 px-6 border-t border-white/5 text-center">
                    <div className="mb-12">
                         <div className="w-12 h-12 brand-gradient rounded-xl flex items-center justify-center text-white mx-auto mb-6 shadow-2xl">
                            <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/></svg>
                        </div>
                        <span className="text-3xl font-black text-white tracking-tighter">EasyPost <span className="text-brand-secondary">AI</span></span>
                    </div>
                    <span className="text-[10px] font-black text-gray-600 uppercase tracking-[0.6em]">© MMXXVI EasyPost Global Infrastructure | Systems Operational</span>
                </footer>
            </main>
        </div>
    );
}