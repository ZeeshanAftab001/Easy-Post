import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import LoadingIndicator from "./LoadingIndicator";
import { Link } from "react-router-dom";

export default function Form({ route, method }) {
  const navigate = useNavigate();
  const isLogin = method === "login";

  // Common fields
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Signup-only fields
  const [whatsapp, setWhatsapp] = useState("");
  const [niche, setNiche] = useState("");
  const [email, setEmail] = useState("");

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);

  let body;
  
  if (isLogin) {
    // For login: send as form-encoded
    body = new URLSearchParams();
    body.append('username', username.trim());  // Note: 'username' field for email
    body.append('password', password.trim());
    
    console.log("Login body (form):", body.toString());
  } else {
    // For signup: send as JSON (as before)
    body = {
      username: username.trim(),
      password: password.trim(),
      whatsapp_number: whatsapp.trim(),
      niche: niche.split(",").map(s => s.trim()).join(","), 
      email: email.trim().toLowerCase(),
    };
    console.log("Signup body (JSON):", body);
  }

  try {
    let res;
    
    if (isLogin) {
      // Send form-encoded for login
      res = await api.post(route, body.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
    } else {
      // Send JSON for signup
      res = await api.post(route, body);
    }

    console.log("Response:", res.data);

    if (isLogin) {
      localStorage.setItem(ACCESS_TOKEN, res.data.access_token);  // Note: access_token not access
      // Check if refresh token is returned
      if (res.data.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh_token);
      }
      navigate("/");
    } else {
      navigate("/login");
    }

  } catch (err) {
    console.error("Full error:", err);
    alert("Error: " + (err.response?.data?.detail || err.message));
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="bg-black flex justify-center items-center min-h-screen w-full relative px-4 sm:px-6 lg:px-8 py-8">
      {/* Grid Background */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `
            repeating-linear-gradient(0deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px),
            repeating-linear-gradient(90deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px)
          `,
          backgroundSize: "100px 100px",
          opacity: 0.1,
        }}
      />

      <div className="w-full max-w-6xl flex flex-col lg:flex-row items-center justify-center gap-8 lg:gap-12">
        {/* Left side - Welcome/Info Section */}
        <div className="w-full lg:w-1/2 text-center lg:text-left">
          <div className="mb-6 lg:mb-8">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
              {isLogin ? "Welcome Back!" : "Start Your Career Journey"}
            </h1>
            <p className="text-gray-300 text-base sm:text-lg lg:text-xl">
              {isLogin 
                ? "Sign in to access personalized career recommendations and AI guidance."
                : "Create an account to get personalized career advice based on your skills and interests."}
            </p>
          </div>
          
          {/* Features/Benefits */}
          <div className="hidden lg:block mt-8 space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-gray-300">AI-powered posting</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-gray-300">Personalized skill development plans</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-gray-300">Real-time industry insights</span>
            </div>
          </div>
        </div>

        {/* Right side - Form */}
        <div className="w-full lg:w-1/2">
          <form
            onSubmit={handleSubmit}
            className="relative z-10 p-6 sm:p-8 md:p-10 rounded-2xl shadow-lg flex flex-col items-center w-full bg-black/80 backdrop-blur-lg border border-gray-800"
          >
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-6">
              {isLogin ? "Login" : "Create Account"}
            </h1>

            <div className="w-full space-y-4">
              {/* Username */}
              <div>
                <input
                  type="text"
                  placeholder="Username"
                  className="w-full p-3 sm:p-4 rounded-lg bg-gray-900/70 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition-all"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              {/* Password */}
              <div>
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full p-3 sm:p-4 rounded-lg bg-gray-900/70 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition-all"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {/* SIGNUP FIELDS (Only visible in Signup mode) */}
              {!isLogin && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <input
                        type="text"
                        placeholder="Business Niche (comma-separated, e.g., Tech, Health, Finance)"
                        className="w-full p-3 sm:p-4 rounded-lg bg-gray-900/70 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition-all"
                        value={niche}
                        onChange={(e) => setNiche(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <input
                        type="email"
                        placeholder="Email"
                        className="w-full p-3 sm:p-4 rounded-lg bg-gray-900/70 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition-all"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <input
                      type="text"
                      placeholder="WhatsApp Number"
                      className="w-full p-3 sm:p-4 rounded-lg bg-gray-900/70 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition-all"
                      value={whatsapp}
                      onChange={(e) => setWhatsapp(e.target.value)}
                    />
                  </div>
                </div>
              )}

              {loading && (
                <div className="flex justify-center">
                  <LoadingIndicator />
                </div>
              )}

              {/* Submit Button */}
              <button 
                type="submit" 
                className="w-full btn text-black font-semibold p-3 sm:p-4 rounded-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] mt-2"
                disabled={loading}
              >
                {loading ? "Processing..." : (isLogin ? "Login" : "Create Account")}
              </button>

              {/* Link to toggle between Login/Signup */}
              <div className="text-center mt-4">
                {isLogin ? (
                  <p className="text-gray-400">
                    Don't have an account?{" "}
                    <Link to="/signup" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                      Sign up here
                    </Link>
                  </p>
                ) : (
                  <p className="text-gray-400">
                    Already have an account?{" "}
                    <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                      Login here
                    </Link>
                  </p>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}