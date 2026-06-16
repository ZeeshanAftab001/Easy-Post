import axios from "axios";

const apiUrl = "http://localhost:8000/";

const api = axios.create({
  baseURL: apiUrl,
});

// We will inject the token through this interceptor
// Components will need to call api.interceptors.request.use or we can use a simpler approach
// For now, let's allow setting it via a global variable or a setter function
let authToken = null;
let tokenProvider = null;
let tokenCache = {
  token: null,
  expiry: 0
};

export const setAuthToken = (token) => {
  authToken = token;
  tokenCache.token = token;
  tokenCache.expiry = Date.now() + 30000; // 30s cache
};

export const registerTokenProvider = (provider) => {
  tokenProvider = provider;
};

api.interceptors.request.use(
  async (config) => {
    let token = null;
    
    // Check cache first to avoid async overhead from Clerk
    if (tokenCache.token && Date.now() < tokenCache.expiry) {
      token = tokenCache.token;
    } else if (tokenProvider) {
      try {
        // Dynamic provider (Clerk getToken)
        token = await tokenProvider();
        // Update cache
        tokenCache.token = token;
        tokenCache.expiry = Date.now() + 30000; 
      } catch (e) {
        console.error("Token Provider Failed:", e);
      }
    }
    
    // Fallback to static token
    if (!token) {
      token = authToken;
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If 401, we might want to handle it, but Clerk handles session expiration
    return Promise.reject(error);
  }
);

export default api;