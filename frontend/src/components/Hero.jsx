import React from 'react';
import { useNavigate } from 'react-router-dom';

const Hero = () => {
    const navigate = useNavigate();

    return (
        <section className="relative w-full min-h-screen flex flex-col items-center justify-center pt-32 px-6">
            {/* Background design elements */}
            <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[500px] bg-brand-primary/5 blur-[160px] rounded-full pointer-events-none" />

            {/* Status Badge */}
            <div className="animate-fade-in mb-12">
                <div className="bg-white border border-gray-100 px-5 py-2 rounded-full flex items-center gap-3 shadow-sm">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary"></span>
                    </span>
                    <span className="text-[10px] font-black tracking-[0.2em] text-brand-primary uppercase">
                        Enterprise AI Agent Infrastructure Live
                    </span>
                </div>
            </div>

            {/* Massive Typography */}
            <div className="max-w-5xl text-center mb-16">
                <h1 className="text-6xl md:text-[110px] font-black text-gray-900 leading-[1] tracking-[-0.04em] mb-10">
                    Automate social <br /> 
                    with <span className="brand-text-gradient">Agent Intelligence</span>
                </h1>
                <p className="text-lg md:text-2xl text-gray-400 font-bold max-w-3xl mx-auto leading-relaxed px-4">
                    The autonomous command center for high-performance social operations. Generate, schedule, and engage with GenAI precision.
                </p>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-6 mb-32 relative z-10">
                <button 
                    onClick={() => navigate('/dashboard')}
                    className="group bg-gray-900 text-white px-12 py-6 rounded-[24px] font-black text-xl shadow-2xl shadow-gray-900/20 hover:scale-[1.02] active:scale-100 transition-all flex items-center gap-4"
                >
                    Launch Terminal
                    <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </button>
                <button className="bg-white border border-gray-100 text-gray-900 px-12 py-6 rounded-[24px] font-black text-xl shadow-sm hover:bg-gray-50 transition-all">
                    System Architecture
                </button>
            </div>

            {/* Network Capabilities (Icons replaced with text/monochrome) */}
            <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-6 opacity-20 group">
                {['Meta', 'Instagram', 'WhatsApp'].map(plat => (
                    <span key={plat} className="text-sm font-black uppercase tracking-[0.3em] hover:opacity-100 transition-opacity cursor-default">
                        {plat}
                    </span>
                ))}
            </div>
        </section>
    );
};

export default Hero;