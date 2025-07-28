import { defineStore } from 'pinia'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_verified: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    fullName: (state) => {
      if (state.user) {
        return `${state.user.first_name} ${state.user.last_name}`
      }
      return ''
    }
  },

  actions: {
    async login(credentials: { email: string; password: string }) {
      this.loading = true
      try {
        const { $api } = useNuxtApp()
        const response = await $api.post('/auth/login/', credentials)
        
        const { access, refresh, user } = response.data
        
        // Store tokens in cookies
        const accessToken = useCookie('access_token', {
          maxAge: 60 * 60, // 1 hour
          secure: true,
          sameSite: 'strict'
        })
        const refreshToken = useCookie('refresh_token', {
          maxAge: 60 * 60 * 24 * 7, // 7 days
          secure: true,
          sameSite: 'strict'
        })
        
        accessToken.value = access
        refreshToken.value = refresh
        
        this.user = user
        this.isAuthenticated = true
        
        return { success: true }
      } catch (error: any) {
        console.error('Login error:', error)
        return { 
          success: false, 
          error: error.response?.data?.non_field_errors?.[0] || 'Login failed' 
        }
      } finally {
        this.loading = false
      }
    },

    async register(userData: {
      username: string
      email: string
      first_name: string
      last_name: string
      password: string
      password_confirm: string
    }) {
      this.loading = true
      try {
        const { $api } = useNuxtApp()
        const response = await $api.post('/auth/register/', userData)
        
        const { access, refresh, user } = response.data
        
        // Store tokens in cookies
        const accessToken = useCookie('access_token', {
          maxAge: 60 * 60, // 1 hour
          secure: true,
          sameSite: 'strict'
        })
        const refreshToken = useCookie('refresh_token', {
          maxAge: 60 * 60 * 24 * 7, // 7 days
          secure: true,
          sameSite: 'strict'
        })
        
        accessToken.value = access
        refreshToken.value = refresh
        
        this.user = user
        this.isAuthenticated = true
        
        return { success: true }
      } catch (error: any) {
        console.error('Registration error:', error)
        return { 
          success: false, 
          error: error.response?.data || 'Registration failed' 
        }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        const { $api } = useNuxtApp()
        const refreshToken = useCookie('refresh_token')
        
        if (refreshToken.value) {
          await $api.post('/auth/logout/', { refresh: refreshToken.value })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // Clear tokens and user data
        const accessToken = useCookie('access_token')
        const refreshTokenCookie = useCookie('refresh_token')
        
        accessToken.value = null
        refreshTokenCookie.value = null
        
        this.user = null
        this.isAuthenticated = false
        
        await navigateTo('/login')
      }
    },

    async fetchUser() {
      try {
        const { $api } = useNuxtApp()
        const response = await $api.get('/users/me/')
        this.user = response.data
        this.isAuthenticated = true
      } catch (error) {
        console.error('Fetch user error:', error)
        this.user = null
        this.isAuthenticated = false
      }
    },

    async checkAuth() {
      const accessToken = useCookie('access_token')
      if (accessToken.value) {
        await this.fetchUser()
      }
    },

    async changePassword(passwordData: {
      old_password: string
      new_password: string
      new_password_confirm: string
    }) {
      this.loading = true
      try {
        const { $api } = useNuxtApp()
        await $api.post('/auth/change-password/', passwordData)
        return { success: true }
      } catch (error: any) {
        console.error('Change password error:', error)
        return { 
          success: false, 
          error: error.response?.data || 'Password change failed' 
        }
      } finally {
        this.loading = false
      }
    }
  }
})