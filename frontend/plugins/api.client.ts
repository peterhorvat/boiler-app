import axios from 'axios'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const { $router } = useNuxtApp()
  
  const api = axios.create({
    baseURL: config.public.apiBaseUrl,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor to add auth token
  api.interceptors.request.use(
    (config) => {
      const token = useCookie('access_token')
      if (token.value) {
        config.headers.Authorization = `Bearer ${token.value}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor to handle token refresh
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        const refreshToken = useCookie('refresh_token')
        if (refreshToken.value) {
          try {
            const response = await axios.post(`${config.public.apiBaseUrl}/auth/refresh/`, {
              refresh: refreshToken.value
            })

            const { access } = response.data
            const accessToken = useCookie('access_token')
            accessToken.value = access

            originalRequest.headers.Authorization = `Bearer ${access}`
            return api(originalRequest)
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            const accessToken = useCookie('access_token')
            const refreshTokenCookie = useCookie('refresh_token')
            accessToken.value = null
            refreshTokenCookie.value = null
            
            await $router.push('/login')
            return Promise.reject(refreshError)
          }
        } else {
          // No refresh token, redirect to login
          await $router.push('/login')
        }
      }

      return Promise.reject(error)
    }
  )

  return {
    provide: {
      api
    }
  }
})