import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children, user }) => {
    return (
        <div className="flex min-h-screen bg-brand-bg">
            <Sidebar user={user} />
            <main className="ml-64 flex-1 p-10 pb-20">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
