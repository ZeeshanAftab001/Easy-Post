import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ user }) => {
    const navItems = [
        { name: 'Overview', path: '/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"/></svg> },
        { name: 'AI Operator', path: '/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg> },
        { name: 'Content Hub', path: '/content-hub', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg> },
        { name: 'Connections', path: '/connect', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg> },
        { name: 'Billing', path: '/billing', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg> },
        { name: 'Settings', path: '/settings', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg> },
    ];

    return (
        <aside className="w-64 min-h-screen bg-brand-bg border-r border-white/5 flex flex-col fixed left-0 top-0 z-50">
            <div className="p-10">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 brand-gradient rounded-lg flex items-center justify-center text-black glow-primary">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/></svg>
                    </div>
                    <span className="text-xl font-black text-white tracking-tighter">EasyPost <span className="text-brand-primary">AI</span></span>
                </div>
            </div>

            <nav className="flex-1 px-6 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-black transition-all group ${
                                isActive 
                                ? 'bg-brand-primary/10 text-brand-primary' 
                                : 'text-gray-500 hover:bg-white/[0.02] hover:text-white'
                            }`
                        }
                    >
                        <div className={`transition-transform group-hover:scale-110`}>{item.icon}</div>
                        <span className="uppercase tracking-[0.2em]">{item.name}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-8 mt-auto border-t border-white/5 bg-white/[0.01]">
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-[10px] font-black text-brand-primary">
                        {user?.username?.substring(0, 2).toUpperCase() || 'OP'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-xs font-black text-white truncate uppercase tracking-widest">{user?.username || 'Operator'}</p>
                        <p className="text-[9px] font-black text-brand-primary/60 uppercase tracking-widest">
                            {user?.subscription_tier || 'System Admin'}
                        </p>
                    </div>
                </div>
                <button 
                    onClick={() => window.location.href = '/logout'}
                    className="w-full py-3 px-4 rounded-xl text-[10px] font-black text-gray-600 hover:text-brand-primary hover:bg-brand-primary/5 border border-transparent hover:border-brand-primary/20 transition-all flex items-center justify-center gap-2 uppercase tracking-[0.2em]"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                    Disconnect
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
