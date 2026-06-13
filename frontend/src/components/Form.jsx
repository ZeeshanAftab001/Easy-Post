import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import LoadingIndicator from "./LoadingIndicator";
import { Link } from "react-router-dom";

export default function Form({ route, method }) {
    const navigate = useNavigate();
    const isLogin = method === "login";

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [whatsapp, setWhatsapp] = useState("");
    const [niche, setNiche] = useState("");
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        let body;
        if (isLogin) {
            body = new URLSearchParams();
            body.append('username', username.trim());
            body.append('password', password.trim());
        } else {
            body = {
                username: username.trim(),
                password: password.trim(),
                whatsapp_number: whatsapp.trim(),
                niche: niche.split(",").map(s => s.trim()).join(","), 
                email: email.trim().toLowerCase(),
            };
        }

        try {
            let res;
            if (isLogin) {
                res = await api.post(route, body.toString(), {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                });
            } else {
                res = await api.post(route, body);
            }

            if (isLogin) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access_token);
                if (res.data.refresh_token) {
                    localStorage.setItem(REFRESH_TOKEN, res.data.refresh_token);
                }
                navigate("/dashboard");
            } else {
                navigate("/login");
            }
        } catch (err) {
            alert("Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen">
            {/* Left Side: Branding/Visual */}
            <div className="hidden lg:flex w-1/2 brand-gradient flex-col justify-between p-16 text-white relative overflow-hidden">
                <div className="absolute top-[-10%] right-[-10%] w-[60%] h-[60%] bg-white/10 blur-[120px] rounded-full" />
                
                <div className="relative z-10 flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center font-black text-xl">
                        ⚡
                    </div>
                    <span className="text-2xl font-black tracking-tight tracking-tighter">EasyPost AI</span>
                </div>

                <div className="relative z-10">
                    <h1 className="text-6xl font-black leading-[1.1] mb-8">
                        {isLogin ? "Welcome back to the Future of Social." : "Join the AI Revolution in Social Media."}
                    </h1>
                    <p className="text-xl text-white/80 font-medium max-w-md leading-relaxed">
                        The ultimate command center for creators who value their time. Automate, scale, and thrive.
                    </p>
                </div>

                <div className="relative z-10 text-sm font-bold text-white/40">
                    © 2026 EasyPost AI. All rights reserved.
                </div>
            </div>

            {/* Right Side: Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-brand-bg relative">
                <div className="w-full max-w-md">
                    <div className="mb-12">
                        <h2 className="text-4xl font-black text-gray-900 mb-3">
                            {isLogin ? "Sign In" : "Create Account"}
                        </h2>
                        <p className="text-gray-500 font-bold">
                            {isLogin ? "Enter your credentials to manage your social empire." : "Fill in the details to start your journey."}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-4">
                            <label className="block">
                                <span className="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2 px-1">Logon Name</span>
                                <input
                                    type="text"
                                    placeholder="yourname"
                                    className="w-full bg-white border border-gray-100 rounded-2xl px-6 py-4 text-sm font-bold text-gray-900 focus:ring-4 focus:ring-brand-primary/10 focus:border-brand-primary outline-none transition-all"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </label>

                            {!isLogin && (
                                <label className="block animate-fade-in">
                                    <span className="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2 px-1">Email Address</span>
                                    <input
                                        type="email"
                                        placeholder="you@creators.com"
                                        className="w-full bg-white border border-gray-100 rounded-2xl px-6 py-4 text-sm font-bold text-gray-900 focus:ring-4 focus:ring-brand-primary/10 focus:border-brand-primary outline-none transition-all"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </label>
                            )}

                            <label className="block">
                                <span className="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2 px-1">Password Key</span>
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    className="w-full bg-white border border-gray-100 rounded-2xl px-6 py-4 text-sm font-bold text-gray-900 focus:ring-4 focus:ring-brand-primary/10 focus:border-brand-primary outline-none transition-all"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </label>

                            {!isLogin && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
                                    <label className="block">
                                        <span className="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2 px-1">Niche</span>
                                        <input
                                            type="text"
                                            placeholder="Tech, Fashion"
                                            className="w-full bg-white border border-gray-100 rounded-2xl px-5 py-4 text-sm font-bold text-gray-900 focus:ring-4 focus:ring-brand-primary/10 focus:border-brand-primary outline-none"
                                            value={niche}
                                            onChange={(e) => setNiche(e.target.value)}
                                        />
                                    </label>
                                    <label className="block">
                                        <span className="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2 px-1">WhatsApp</span>
                                        <input
                                            type="text"
                                            placeholder="+123..."
                                            className="w-full bg-white border border-gray-100 rounded-2xl px-5 py-4 text-sm font-bold text-gray-900 focus:ring-4 focus:ring-brand-primary/10 focus:border-brand-primary outline-none"
                                            value={whatsapp}
                                            onChange={(e) => setWhatsapp(e.target.value)}
                                        />
                                    </label>
                                </div>
                            )}
                        </div>

                        {loading && <LoadingIndicator />}

                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full py-5 brand-gradient text-white rounded-[24px] font-black text-lg transition-all hover:scale-[1.02] active:scale-100 shadow-xl shadow-brand-primary/30 disabled:opacity-50"
                        >
                            {loading ? "Processing..." : (isLogin ? "Sign In Now" : "Create My Empire")}
                        </button>

                        <div className="text-center mt-8">
                            {isLogin ? (
                                <p className="text-gray-400 font-bold text-sm">
                                    New to the platform?{" "}
                                    <Link to="/signup" className="text-brand-primary hover:underline">
                                        Create an account
                                    </Link>
                                </p>
                            ) : (
                                <p className="text-gray-400 font-bold text-sm">
                                    Already have an account?{" "}
                                    <Link to="/login" className="text-brand-primary hover:underline">
                                        Sign in here
                                    </Link>
                                </p>
                            )}
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}