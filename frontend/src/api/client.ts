import axios from 'axios'
import { OpenAPI } from './generated/core/OpenAPI'
import { AuthService } from './generated/services/AuthService'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Настройка OpenAPI клиента для generated services
OpenAPI.BASE = API_BASE_URL
OpenAPI.WITH_CREDENTIALS = true
OpenAPI.CREDENTIALS = 'include'

// Функция для установки токена в OpenAPI
export const setAuthToken = (token: string | null) => {
  if (token) {
    OpenAPI.TOKEN = token
  } else {
    OpenAPI.TOKEN = undefined
  }
}

// Функции для работы с токенами
export const getStoredToken = (): string | null => {
  return localStorage.getItem('access_token')
}

export const saveTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)
  setAuthToken(accessToken)
}

export const clearTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  setAuthToken(null)
}

// Инициализация токена при загрузке
const storedToken = getStoredToken()
if (storedToken) {
  setAuthToken(storedToken)
}

// Axios клиент для legacy кода (если нужен)
export const apiClient = axios.create({
  baseURL: API_BASE_URL + '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor для добавления JWT токена
apiClient.interceptors.request.use(
  (config) => {
    const token = getStoredToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor для обработки ошибок и refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await AuthService.refreshApiV1AuthRefreshPost({
            refresh_token: refreshToken,
          })

          saveTokens(response.access_token, response.refresh_token)

          originalRequest.headers.Authorization = `Bearer ${response.access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh token истёк, выходим
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
