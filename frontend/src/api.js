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

export const setAuthToken = (token) => {
  authToken = token;
};

export const registerTokenProvider = (provider) => {
  tokenProvider = provider;
};

api.interceptors.request.use(
  async (config) => {
    let token = null;
    
    // Always prefer the dynamic provider for fresh tokens
    if (tokenProvider) {
      try {
        token = await tokenProvider();
      } catch (e) {
        console.error("Token Provider Failed:", e);
      }
    }
    
    // Fallback to static token if provider failed or not registered
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