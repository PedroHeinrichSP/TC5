import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user
  },

  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)
        
        const response = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
        
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        
        // Fetch user data
        await this.fetchUser()
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao fazer login'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async register(email, password, fullName) {
      this.loading = true
      this.error = null
      
      try {
        await api.post('/auth/register', {
          email,
          password,
          full_name: fullName
        })
        
        // Auto-login after registration
        return await this.login(email, password)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao registrar'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async fetchUser() {
      if (!this.token) return
      
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
      } catch (error) {
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    }
  }
})
