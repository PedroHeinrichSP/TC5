<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Login</h1>
        <p class="text-gray-600 mt-2">Entre na sua conta</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Error Alert -->
        <div 
          v-if="error" 
          class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg"
        >
          {{ error }}
        </div>

        <!-- Email -->
        <div>
          <label class="block text-gray-700 font-medium mb-2">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="seu@email.com"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-gray-700 font-medium mb-2">
            Senha
          </label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="********"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="authStore.loading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Entrando...
          </span>
          <span v-else>Entrar</span>
        </button>
      </form>

      <!-- Register Link -->
      <p class="mt-6 text-center text-gray-600">
        Nao tem conta?
        <router-link to="/register" class="text-indigo-600 hover:underline font-medium">
          Registre-se
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showToast = inject('showToast')

const form = ref({
  email: '',
  password: ''
})

const error = ref('')

const handleLogin = async () => {
  error.value = ''
  
  const result = await authStore.login(form.value.email, form.value.password)
  
  if (result.success) {
    showToast('Login realizado com sucesso!', 'success')
    router.push('/dashboard')
  } else {
    error.value = result.error
  }
}
</script>
