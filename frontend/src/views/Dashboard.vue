<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p class="text-gray-600 mt-1">
          Bem-vindo, {{ authStore.user?.full_name || 'Usuario' }}!
        </p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid md:grid-cols-3 gap-6">
      <div class="bg-white rounded-xl shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Total de Sessoes</p>
            <p class="text-3xl font-bold text-indigo-600">{{ sessions.length }}</p>
          </div>
          <div class="text-4xl text-indigo-300 font-bold">#</div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Questoes Geradas</p>
            <p class="text-3xl font-bold text-green-600">{{ totalQuestions }}</p>
          </div>
          <div class="text-4xl text-green-300 font-bold">Q</div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Ultima Atividade</p>
            <p class="text-lg font-semibold text-gray-700">{{ lastActivity }}</p>
          </div>
          <div class="text-4xl text-gray-300 font-bold">T</div>
        </div>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="bg-white rounded-xl shadow-md p-8">
      <h2 class="text-xl font-bold text-gray-800 mb-6">Novo Upload</h2>
      
      <div 
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        :class="[
          'border-2 border-dashed rounded-xl p-12 text-center transition cursor-pointer',
          isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
        ]"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.txt,.docx"
          class="hidden"
          @change="handleFileSelect"
        />
        
        <div class="text-5xl mb-4 text-indigo-300 font-bold">+</div>
        <p class="text-xl font-medium text-gray-700 mb-2">
          Arraste seu arquivo aqui
        </p>
        <p class="text-gray-500">
          ou clique para selecionar
        </p>
        <p class="text-sm text-gray-400 mt-4">
          Formatos: PDF, TXT, DOCX (max. 20MB, 50 paginas)
        </p>
      </div>

      <!-- Selected File -->
      <div v-if="selectedFile" class="mt-6 p-4 bg-gray-50 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-2xl mr-3 text-indigo-600 font-bold">[F]</span>
            <div>
              <p class="font-medium text-gray-800">{{ selectedFile.name }}</p>
              <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
          </div>
          <button 
            @click="selectedFile = null" 
            class="text-red-500 hover:text-red-700"
          >
            X
          </button>
        </div>
        
        <button
          @click="handleUpload"
          :disabled="questionsStore.loading"
          class="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
        >
          <span v-if="questionsStore.loading">
            Processando...
          </span>
          <span v-else>
            Fazer Upload e Continuar
          </span>
        </button>
      </div>
    </div>

    <!-- Recent Sessions -->
    <div class="bg-white rounded-xl shadow-md p-8">
      <h2 class="text-xl font-bold text-gray-800 mb-6">Sessoes Recentes</h2>
      
      <div v-if="questionsStore.loading" class="text-center py-8">
        <div class="animate-spin text-4xl text-indigo-600">...</div>
        <p class="text-gray-500 mt-2">Carregando...</p>
      </div>
      
      <div v-else-if="sessions.length === 0" class="text-center py-8 text-gray-500">
        <div class="text-5xl mb-4 text-gray-300 font-bold">[ ]</div>
        <p>Nenhuma sessao encontrada. Faca seu primeiro upload!</p>
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          class="border rounded-lg p-4 hover:bg-gray-50 transition"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800">
                {{ session.source_filename || 'Arquivo' }}
              </p>
              <p class="text-sm text-gray-500">
                {{ formatDate(session.created_at) }} • 
                {{ session.question_count || 0 }} questões
              </p>
            </div>
            <div class="flex gap-2">
              <span 
                :class="[
                  'px-3 py-1 rounded-full text-sm',
                  session.status === 'completed' ? 'bg-green-100 text-green-800' : '',
                  session.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : '',
                  session.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''
                ]"
              >
                {{ statusLabel(session.status) }}
              </span>
              <button
                v-if="session.status === 'pending'"
                @click="$router.push(`/generate/${session.id}`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1 rounded-lg text-sm"
              >
                Gerar
              </button>
              <button
                v-else-if="session.status === 'completed'"
                @click="$router.push(`/review/${session.id}`)"
                class="bg-green-600 hover:bg-green-700 text-white px-4 py-1 rounded-lg text-sm"
              >
                Revisar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useQuestionsStore } from '../stores/questions'

const router = useRouter()
const authStore = useAuthStore()
const questionsStore = useQuestionsStore()
const showToast = inject('showToast')

const isDragging = ref(false)
const selectedFile = ref(null)

const sessions = computed(() => questionsStore.sessions)

const totalQuestions = computed(() => {
  return sessions.value.reduce((sum, s) => sum + (s.question_count || 0), 0)
})

const lastActivity = computed(() => {
  if (sessions.value.length === 0) return 'Nenhuma'
  const latest = sessions.value[0]
  return formatDate(latest.created_at)
})

onMounted(async () => {
  await authStore.fetchUser()
  await questionsStore.fetchSessions()
})

const handleDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const validateAndSetFile = (file) => {
  const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const maxSize = 20 * 1024 * 1024 // 20MB
  
  if (!validTypes.includes(file.type)) {
    showToast('Formato não suportado. Use PDF, TXT ou DOCX.', 'error')
    return
  }
  
  if (file.size > maxSize) {
    showToast('Arquivo muito grande. Máximo: 20MB.', 'error')
    return
  }
  
  selectedFile.value = file
}

const handleUpload = async () => {
  if (!selectedFile.value) return
  
  const result = await questionsStore.uploadFile(selectedFile.value)
  
  if (result.success) {
    showToast('Upload realizado com sucesso!', 'success')
    selectedFile.value = null
    router.push(`/generate/${result.session.session_id}`)
  } else {
    showToast(result.error, 'error')
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const statusLabel = (status) => {
  const labels = {
    'pending': 'Pendente',
    'processing': 'Processando',
    'completed': 'Concluído',
    'failed': 'Erro'
  }
  return labels[status] || status
}
</script>
