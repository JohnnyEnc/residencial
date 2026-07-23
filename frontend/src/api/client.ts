import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// No forzar redirect en fallos de login/me (el formulario muestra el error).
api.interceptors.response.use(
  (r) => r,
  (error) => {
    const status = error.response?.status
    const url = String(error.config?.url || '')
    const isAuthCall = url.includes('/auth/login') || url.includes('/auth/me')
    if (status === 401 && !isAuthCall) {
      localStorage.removeItem('token')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
