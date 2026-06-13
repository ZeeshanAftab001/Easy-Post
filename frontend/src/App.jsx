import React, { useEffect, useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth, SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';
import { setAuthToken, registerTokenProvider } from './api';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Connect from './pages/Connect';
import ContentHub from './pages/ContentHub';
import Contact from './pages/Contact';
import Settings from './pages/Settings';
import Billing from './pages/Billing';
import Chat from './pages/Chat';
import FacebookCallback from './pages/FacebookCallback';
import InstagramCallback from './pages/InstagramCallback';

function TokenRefresher({ children }) {
  const { getToken, isSignedIn, isLoaded } = useAuth();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const updateToken = async () => {
      if (isLoaded && isSignedIn) {
        try {
          // Register dynamic provider for always-fresh tokens
          registerTokenProvider(() => getToken());
          
          const token = await getToken();
          console.log("Identity Protocol Active.");
          setAuthToken(token);
          setReady(true);
        } catch (err) {
          console.error("Identity Handshake Failed:", err);
        }
      } else if (isLoaded && !isSignedIn) {
        setAuthToken(null);
        registerTokenProvider(null);
        setReady(true);
      }
    };
    updateToken();
  }, [isSignedIn, isLoaded, getToken]);

  if (!isLoaded || !ready) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-brand-muted text-[10px] font-black uppercase tracking-[0.3em]">Synching Identity...</p>
        </div>
      </div>
    );
  }

  return children;
}

export default function App() {
  return (
    <TokenRefresher>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/auth/facebook/callback" element={<FacebookCallback />} />
        <Route path="/auth/instagram/callback" element={<InstagramCallback />} />

        <Route path="/dashboard" element={
          <>
            <SignedIn><Dashboard /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/connect" element={
          <>
            <SignedIn><Connect /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/content-hub" element={
          <>
            <SignedIn><ContentHub /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/contacts" element={
          <>
            <SignedIn><Contact /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/settings" element={
          <>
            <SignedIn><Settings /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/billing" element={
          <>
            <SignedIn><Billing /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
        <Route path="/chat" element={
          <>
            <SignedIn><Chat /></SignedIn>
            <SignedOut><RedirectToSignIn /></SignedOut>
          </>
        } />
      </Routes>
    </TokenRefresher>
  );
}