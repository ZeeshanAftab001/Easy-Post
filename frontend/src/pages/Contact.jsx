import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Layout from '../components/Layout';

const ContactItem = ({ title, details, icon }) => (
    <div className="bg-brand-card p-10 rounded-[48px] border border-white/5 shadow-2xl relative overflow-hidden group reveal">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-bl-full translate-x-16 -translate-y-16 group-hover:bg-brand-primary/10 transition-colors" />
        <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center text-brand-muted mb-8 group-hover:brand-gradient group-hover:text-white transition-all shadow-sm">
            {icon}
        </div>
        <h3 className="text-[10px] font-black text-brand-muted uppercase tracking-[0.3em] mb-4">{title}</h3>
        <p className="text-xl font-bold text-white tracking-tight">
            {details}
        </p>
    </div>
);

const Contact = ({ isPage = false }) => {
    const content = (
        <div className="max-w-7xl mx-auto">
            <div className="text-center mb-24 reveal">
                <span className="inline-block px-4 py-2 rounded-full border border-white/10 bg-white/5 text-[10px] font-black uppercase tracking-[0.5em] text-brand-secondary mb-10">Communications Module</span>
                <h1 className="text-6xl font-black text-white tracking-tighter mb-6 underline decoration-brand-secondary decoration-8 underline-offset-8">Human Interface.</h1>
                <p className="text-brand-muted font-black uppercase tracking-[0.3em] text-xs">Direct Support & Infrastructure Queries</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <ContactItem 
                    title="Protocol Support" 
                    details="support@easypost.ai" 
                    icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>}
                />
                <ContactItem 
                    title="Direct Sync" 
                    details="+92 (300) 123-4567" 
                    icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>}
                />
                <ContactItem 
                    title="Command HQ" 
                    details="Science Park, Dubai, UAE" 
                    icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>}
                />
            </div>
            
            <div className="mt-20 bg-brand-card p-12 rounded-[56px] border border-white/5 shadow-2xl relative overflow-hidden group reveal">
                 <div className="absolute top-0 right-0 w-64 h-64 brand-gradient opacity-[0.03] blur-[100px] -translate-y-1/2 translate-x-1/2 group-hover:opacity-[0.05] transition-opacity" />
                 <h2 className="text-3xl font-black text-white mb-6 uppercase tracking-widest text-sm">Deployment Inquiry</h2>
                 <p className="text-brand-muted font-bold text-lg leading-relaxed mb-10 max-w-2xl">
                    Need an enterprise-level custom solution or a high-frequency posting strategy? Our senior operators are ready to synchronize.
                 </p>
                 <button className="px-12 py-6 brand-gradient rounded-full font-black text-xs uppercase tracking-widest text-white shadow-2xl shadow-brand-primary/20 hover:scale-105 transition-all">
                    Initiate Direct Channel
                 </button>
            </div>
        </div>
    );

    if (isPage) {
        return (
            <div className="min-h-screen bg-brand-bg pt-24 px-6 md:px-12">
                <Navbar />
                <div className="py-20">{content}</div>
            </div>
        );
    }

    return content;
};

export default Contact;