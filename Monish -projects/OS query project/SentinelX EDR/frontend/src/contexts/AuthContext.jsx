import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, setAuthToken, removeAuthToken } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionWarning, setSessionWarning] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
      return null;
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setAuthToken(token);
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error("Failed to fetch user on load", error);
          logout();
        }
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

  useEffect(() => {
    let warningTimer;
    let countdownInterval;

    const setupTimers = () => {
      const token = localStorage.getItem('access_token');
      if (token && user) {
        const decoded = parseJwt(token);
        if (decoded && decoded.exp) {
          const expiresAt = decoded.exp * 1000;
          const timeUntilWarning = expiresAt - Date.now() - (60 * 1000); // 60 seconds before expiry

          if (timeUntilWarning > 0) {
            warningTimer = setTimeout(() => {
              setSessionWarning(true);
              setTimeLeft(60);
              
              countdownInterval = setInterval(() => {
                setTimeLeft((prev) => {
                  if (prev <= 1) {
                    clearInterval(countdownInterval);
                    logout();
                    return 0;
                  }
                  return prev - 1;
                });
              }, 1000);
            }, timeUntilWarning);
          } else if (Date.now() < expiresAt) {
            // Already in warning window
            setSessionWarning(true);
            setTimeLeft(Math.floor((expiresAt - Date.now()) / 1000));
            countdownInterval = setInterval(() => {
              setTimeLeft((prev) => {
                if (prev <= 1) {
                  clearInterval(countdownInterval);
                  logout();
                  return 0;
                }
                return prev - 1;
              });
            }, 1000);
          }
        }
      }
    };

    setupTimers();

    return () => {
      clearTimeout(warningTimer);
      clearInterval(countdownInterval);
    };
  }, [user]);

  const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    setAuthToken(access_token);
    
    const userResponse = await api.get('/auth/me');
    setUser(userResponse.data);
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await api.post('/auth/logout');
      }
    } catch (e) {
      console.error("Logout error", e);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      removeAuthToken();
      setUser(null);
      setSessionWarning(false);
    }
  };

  const extendSession = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        const res = await api.post('/auth/refresh', { refresh_token: refreshToken });
        const { access_token, refresh_token: new_refresh_token } = res.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', new_refresh_token);
        setAuthToken(access_token);
        setSessionWarning(false);
        // Force token re-evaluation by fetching user
        const userResponse = await api.get('/auth/me');
        setUser(userResponse.data);
      }
    } catch (err) {
      logout();
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isAuthenticated: !!user, sessionWarning, timeLeft, extendSession }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
