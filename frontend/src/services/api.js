import axios from 'axios'

// Determina a URL base da API
// Em dev local: usa proxy do Vite (/api/v1)
// Em producao: usa VITE_API_URL ou fallback para localhost
const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // Em desenvolvimento local, usa o proxy do Vite
  if (import.meta.env.DEV) {
    return '/api/v1'
  }
  // Fallback para localhost (nao funciona em GitHub Pages sem backend)
  return 'http://localhost:8000/api/v1'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 120000, // 2 minutes for long operations
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
