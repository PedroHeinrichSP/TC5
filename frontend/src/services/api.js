import axios from 'axios'

// URL do backend no Render
const RENDER_API_URL = 'https://questgen-backend.onrender.com/api/v1'

// Determina a URL base da API
const getBaseURL = () => {
  // Se tiver variavel de ambiente, usa ela
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // Em desenvolvimento local, usa o proxy do Vite
  if (import.meta.env.DEV) {
    return '/api/v1'
  }
  // Em producao (GitHub Pages), usa o backend do Render
  return RENDER_API_URL
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
