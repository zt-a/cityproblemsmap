import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { OpenAPI } from './generated/core/OpenAPI'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Функции для работы с токенами
export const getStoredToken = (): string | null => {
  return localStorage.getItem('access_token')
}

export const getStoredRefreshToken = (): string | null => {
  return localStorage.getItem('refresh_token')
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

// Функция для установки токена в OpenAPI
export const setAuthToken = (token: string | null) => {
  if (token) {
    OpenAPI.TOKEN = token
  } else {
    OpenAPI.TOKEN = undefined
  }
}

// Флаг для предотвращения множественных refresh запросов
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token!)
    }
  })
  failedQueue = []
}

// Глобальный request interceptor для axios
axios.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Глобальный response interceptor для axios
axios.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Если 401 и это не повторный запрос и не запрос на refresh/login/register
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/refresh') &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/register')
    ) {
      if (isRefreshing) {
        // Если уже идёт refresh, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return axios(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getStoredRefreshToken()
      if (!refreshToken) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Создаём новый axios instance без interceptors для refresh запроса
        const refreshAxios = axios.create()
        const response = await refreshAxios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        )

        const { access_token, refresh_token } = response.data
        saveTokens(access_token, refresh_token)

        // Обрабатываем очередь запросов
        processQueue(null, access_token)

        // Повторяем оригинальный запрос
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        return axios(originalRequest)
      } catch (refreshError) {
        // Refresh token истёк или невалиден
        processQueue(refreshError, null)
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// Настройка OpenAPI клиента для generated services
OpenAPI.BASE = API_BASE_URL
OpenAPI.WITH_CREDENTIALS = true
OpenAPI.CREDENTIALS = 'include'

// Инициализация токена при загрузке
const storedToken = getStoredToken()
if (storedToken) {
  setAuthToken(storedToken)
}

// Export axios для использования в других местах
export const apiClient = axios

export default axios
