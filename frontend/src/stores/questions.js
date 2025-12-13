import { defineStore } from 'pinia'
import api from '../services/api'

export const useQuestionsStore = defineStore('questions', {
  state: () => ({
    sessions: [],
    currentSession: null,
    questions: [],
    loading: false,
    generating: false,
    progress: 0,
    error: null
  }),

  getters: {
    getSessionById: (state) => (id) => {
      return state.sessions.find(s => s.id === id)
    },
    
    questionsByType: (state) => (type) => {
      return state.questions.filter(q => q.question_type === type)
    },
    
    questionsByDifficulty: (state) => (difficulty) => {
      return state.questions.filter(q => q.difficulty === difficulty)
    }
  },

  actions: {
    async fetchSessions() {
      this.loading = true
      try {
        const response = await api.get('/generation/sessions')
        this.sessions = response.data.data || []
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao carregar sessões'
        this.sessions = []
      } finally {
        this.loading = false
      }
    },

    async uploadFile(file, params) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await api.post('/upload/file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        this.currentSession = response.data.data
        return { success: true, session: this.currentSession }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao fazer upload'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async generateQuestions(sessionId, params) {
      this.generating = true
      this.progress = 0
      this.error = null
      
      try {
        const response = await api.post(`/generation/${sessionId}/generate`, params)
        const data = response.data.data
        this.questions = data.questions || []
        // Update session info if available
        if (data.session_id) {
          this.currentSession = { 
            id: data.session_id,
            questions_generated: data.questions_generated,
            metadata: data.metadata
          }
        }
        this.progress = 100
        return { success: true, questions: this.questions }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao gerar questoes'
        return { success: false, error: this.error }
      } finally {
        this.generating = false
      }
    },

    async fetchQuestions(sessionId) {
      this.loading = true
      try {
        const response = await api.get(`/generation/${sessionId}/questions`)
        this.questions = response.data
        return { success: true, questions: this.questions }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao carregar questões'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async updateQuestion(questionId, updates) {
      try {
        const response = await api.put(`/generation/questions/${questionId}`, updates)
        
        // Update local state
        const index = this.questions.findIndex(q => q.id === questionId)
        if (index !== -1) {
          this.questions[index] = response.data
        }
        
        return { success: true, question: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao atualizar questão'
        return { success: false, error: this.error }
      }
    },

    async deleteQuestion(questionId) {
      try {
        await api.delete(`/generation/questions/${questionId}`)
        this.questions = this.questions.filter(q => q.id !== questionId)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao excluir questão'
        return { success: false, error: this.error }
      }
    },

    async regenerateQuestion(questionId) {
      try {
        const response = await api.post(`/generation/questions/${questionId}/regenerate`)
        
        // Update local state
        const index = this.questions.findIndex(q => q.id === questionId)
        if (index !== -1) {
          this.questions[index] = response.data
        }
        
        return { success: true, question: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao regenerar questão'
        return { success: false, error: this.error }
      }
    },

    async exportQuestions(sessionId, format, includeAnswers = true) {
      try {
        const response = await api.post(`/export/session/${sessionId}`, {
          format: format,
          include_answers: includeAnswers
        }, {
          responseType: 'blob'
        })
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `questoes_${sessionId}.${format}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erro ao exportar questoes'
        return { success: false, error: this.error }
      }
    },

    clearError() {
      this.error = null
    }
  }
})
