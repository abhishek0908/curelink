import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        // Extract APIError message if available
        const apiError = error.response?.data?.error;
        if (apiError) {
            error.message = apiError.message;
        } else if (error.response?.data?.message) {
            // Fallback to top-level message if present
            error.message = error.response.data.message;
        }
        return Promise.reject(error);
    }
);

export default api;
