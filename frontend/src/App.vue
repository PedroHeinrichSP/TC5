<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <!-- Navbar -->
    <nav class="bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <span class="text-2xl font-bold text-indigo-600">QuestGen AI</span>
            </router-link>
          </div>
          
          <div class="flex items-center space-x-4">
            <template v-if="authStore.isAuthenticated">
              <router-link to="/dashboard" class="text-gray-700 hover:text-indigo-600">
                Dashboard
              </router-link>
              <span class="text-gray-500">|</span>
              <span class="text-gray-600">{{ authStore.user?.email }}</span>
              <button 
                @click="handleLogout"
                class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
              >
                Sair
              </button>
            </template>
            <template v-else>
              <router-link 
                to="/login" 
                class="text-gray-700 hover:text-indigo-600"
              >
                Login
              </router-link>
              <router-link 
                to="/register" 
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition"
              >
                Registrar
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-auto">
      <div class="max-w-7xl mx-auto py-4 px-4 text-center text-gray-500">
        <p>(c) 2025 QuestGen AI - Gerador de Questoes Academicas</p>
        <p class="text-sm mt-1">
          PUC Minas - Pedro Heinrich, Pedro Rigotto, Felipe Augusto
        </p>
      </div>
    </footer>

    <!-- Toast Notifications -->
    <div class="fixed bottom-4 right-4 z-50">
      <transition-group name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'mb-2 p-4 rounded-lg shadow-lg max-w-sm',
            toast.type === 'success' ? 'bg-green-500 text-white' : '',
            toast.type === 'error' ? 'bg-red-500 text-white' : '',
            toast.type === 'info' ? 'bg-blue-500 text-white' : ''
          ]"
        >
          {{ toast.message }}
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Toast system
const toasts = ref([])

const showToast = (message, type = 'info') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

provide('showToast', showToast)

const handleLogout = () => {
  authStore.logout()
  showToast('Logout realizado com sucesso!', 'success')
  router.push('/login')
}
</script>

<style>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
