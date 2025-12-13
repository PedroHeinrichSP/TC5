<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <button 
        @click="$router.push('/dashboard')" 
        class="text-gray-500 hover:text-gray-700"
      >
        <- Voltar
      </button>
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Gerar Questoes</h1>
        <p class="text-gray-600 mt-1">
          Configure os parametros de geracao
        </p>
      </div>
    </div>

    <!-- Session Info -->
    <div class="bg-white rounded-xl shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Arquivo Carregado</h2>
      <div v-if="session" class="flex items-center gap-4">
        <div class="text-4xl text-indigo-300 font-bold">[F]</div>
        <div>
          <p class="font-medium text-gray-800">{{ session.source_filename }}</p>
          <p class="text-sm text-gray-500">
            {{ session.word_count || '?' }} palavras - 
            {{ session.topics?.length || '?' }} topicos identificados
          </p>
        </div>
      </div>
      <div v-else class="text-gray-500">Carregando informacoes...</div>
    </div>

    <!-- Generation Parameters -->
    <div class="bg-white rounded-xl shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-6">Parametros de Geracao</h2>
      
      <form @submit.prevent="handleGenerate" class="space-y-6">
        <!-- Question Count -->
        <div>
          <label class="block text-gray-700 font-medium mb-2">
            Quantidade de Questoes (max. 20)
          </label>
          <input
            v-model.number="params.questionCount"
            type="number"
            min="1"
            max="20"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <!-- Question Types -->
        <div>
          <label class="block text-gray-700 font-medium mb-2">
            Tipos de Questoes
          </label>
          <div class="grid md:grid-cols-3 gap-4">
            <label 
              :class="[
                'flex items-center p-4 border rounded-lg cursor-pointer transition',
                params.types.includes('multipla_escolha') ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              <input
                type="checkbox"
                v-model="params.types"
                value="multipla_escolha"
                class="mr-3"
              />
              <div>
                <span class="font-medium">[A] Multipla Escolha</span>
                <p class="text-sm text-gray-500">4-5 alternativas</p>
              </div>
            </label>
            
            <label 
              :class="[
                'flex items-center p-4 border rounded-lg cursor-pointer transition',
                params.types.includes('verdadeiro_falso') ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              <input
                type="checkbox"
                v-model="params.types"
                value="verdadeiro_falso"
                class="mr-3"
              />
              <div>
                <span class="font-medium">V/F Verdadeiro/Falso</span>
                <p class="text-sm text-gray-500">Com justificativa</p>
              </div>
            </label>
            
            <label 
              :class="[
                'flex items-center p-4 border rounded-lg cursor-pointer transition',
                params.types.includes('dissertativa') ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              <input
                type="checkbox"
                v-model="params.types"
                value="dissertativa"
                class="mr-3"
              />
              <div>
                <span class="font-medium">[D] Dissertativa</span>
                <p class="text-sm text-gray-500">Resposta aberta</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Difficulty -->
        <div>
          <label class="block text-gray-700 font-medium mb-2">
            Dificuldade Preferida
          </label>
          <select
            v-model="params.difficulty"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="mixed">Mista (automatica)</option>
            <option value="easy">Facil</option>
            <option value="medium">Media</option>
            <option value="hard">Dificil</option>
          </select>
        </div>

        <!-- Topics Selection -->
        <div v-if="session?.topics?.length">
          <label class="block text-gray-700 font-medium mb-2">
            Topicos (opcional)
          </label>
          <div class="flex flex-wrap gap-2">
            <label 
              v-for="topic in session.topics" 
              :key="topic"
              :class="[
                'px-3 py-1 rounded-full cursor-pointer transition text-sm',
                params.selectedTopics.includes(topic) 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              <input
                type="checkbox"
                v-model="params.selectedTopics"
                :value="topic"
                class="hidden"
              />
              {{ topic }}
            </label>
          </div>
          <p class="text-sm text-gray-500 mt-2">
            Deixe vazio para usar todos os topicos
          </p>
        </div>

        <!-- Generate Button -->
        <button
          type="submit"
          :disabled="questionsStore.generating || params.types.length === 0"
          class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-lg font-semibold transition disabled:opacity-50 text-lg"
        >
          <span v-if="questionsStore.generating" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Gerando Questoes... (pode levar ate 60s)
          </span>
          <span v-else>Gerar Questoes</span>
        </button>
      </form>
    </div>

    <!-- Progress Indicator -->
    <div v-if="questionsStore.generating" class="bg-white rounded-xl shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Progresso</h2>
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="animate-spin text-2xl text-indigo-600">*</div>
          <p class="text-gray-600">Analisando conteudo e gerando questoes com IA...</p>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div 
            class="bg-indigo-600 h-3 rounded-full transition-all duration-500"
            :style="{ width: questionsStore.progress + '%' }"
          ></div>
        </div>
        <p class="text-sm text-gray-500">
          Isso pode levar de 30 a 60 segundos dependendo do tamanho do documento.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionsStore } from '../stores/questions'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const questionsStore = useQuestionsStore()
const showToast = inject('showToast')

const sessionId = route.params.sessionId
const session = ref(null)

const params = ref({
  questionCount: 10,
  types: ['multipla_escolha', 'verdadeiro_falso'],
  difficulty: 'mixed',
  selectedTopics: []
})

onMounted(async () => {
  try {
    const response = await api.get(`/generation/sessions/${sessionId}`)
    session.value = response.data.data
  } catch (error) {
    showToast('Erro ao carregar sessão', 'error')
    router.push('/dashboard')
  }
})

const handleGenerate = async () => {
  if (params.value.types.length === 0) {
    showToast('Selecione pelo menos um tipo de questão', 'error')
    return
  }

  const result = await questionsStore.generateQuestions(sessionId, {
    num_questions: params.value.questionCount,
    question_types: params.value.types,
    difficulty_distribution: params.value.difficulty === 'mixed' ? null : { [params.value.difficulty]: 1.0 },
    topics_filter: params.value.selectedTopics.length > 0 ? params.value.selectedTopics : null
  })

  if (result.success) {
    showToast(`${result.questions.length} questões geradas com sucesso!`, 'success')
    router.push(`/review/${sessionId}`)
  } else {
    showToast(result.error, 'error')
  }
}
</script>
