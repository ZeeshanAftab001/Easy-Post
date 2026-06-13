import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";

const Navbar = () => {
    const navigate = useNavigate();

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-brand-bg/80 backdrop-blur-xl border-b border-white/5">
            <div className="max-w-7xl mx-auto px-6 h-24 flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3">
                    <div className="w-9 h-9 brand-gradient rounded-xl flex items-center justify-center text-white glow-primary">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/></svg>
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">EasyPost <span className="text-brand-secondary">AI</span></span>
                </Link>

                {/* Nav Links */}
                <div className="hidden md:flex items-center gap-10">
                    {['Features', 'Protocols', 'Enterprise'].map(item => (
                        <a key={item} href={`#${item.toLowerCase()}`} className="text-[10px] font-black text-brand-muted hover:text-white uppercase tracking-[0.4em] transition-all">
                            {item}
                        </a>
                    ))}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-6">
                    <SignedOut>
                        <div className="flex items-center gap-2">
                            <button 
                                onClick={() => navigate('/login')}
                                className="text-[10px] font-black text-white hover:text-brand-secondary px-6 py-2 transition-colors uppercase tracking-widest"
                            >
                                Authenticate
                            </button>
                            <button 
                                onClick={() => navigate('/signup')}
                                className="bg-white text-gray-900 px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-100 transition-all shadow-xl shadow-white/10"
                            >
                                Provision Operator
                            </button>
                        </div>
                    </SignedOut>
                    <SignedIn>
                        <div className="flex items-center gap-6">
                            <button 
                                onClick={() => navigate('/dashboard')}
                                className="bg-white text-gray-900 px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-100 transition-all shadow-xl shadow-white/10"
                            >
                                Open Terminal
                            </button>
                            <UserButton 
                                appearance={{
                                    elements: {
                                        userButtonAvatarBox: "w-10 h-10 border-2 border-brand-primary"
                                    }
                                }}
                                afterSignOutUrl="/"
                            />
                        </div>
                    </SignedIn>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;