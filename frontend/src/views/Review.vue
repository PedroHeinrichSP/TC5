<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button 
          @click="$router.push('/dashboard')" 
          class="text-gray-500 hover:text-gray-700"
        >
          <- Voltar
        </button>
        <div>
          <h1 class="text-3xl font-bold text-gray-800">Revisar Questoes</h1>
          <p class="text-gray-600 mt-1">
            {{ questions.length }} questoes geradas
          </p>
        </div>
      </div>
      
      <!-- Export Buttons -->
      <div class="flex gap-3">
        <button
          @click="exportQuestions('pdf', true)"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          PDF com Gabarito
        </button>
        <button
          @click="exportQuestions('pdf', false)"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          PDF sem Gabarito
        </button>
        <button
          @click="exportQuestions('csv', true)"
          class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          CSV
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-md p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div>
          <label class="text-sm text-gray-600 mr-2">Tipo:</label>
          <select v-model="filters.type" class="border rounded-lg px-3 py-2">
            <option value="">Todos</option>
            <option value="multipla_escolha">Multipla Escolha</option>
            <option value="verdadeiro_falso">V/F</option>
            <option value="dissertativa">Dissertativa</option>
          </select>
        </div>
        <div>
          <label class="text-sm text-gray-600 mr-2">Dificuldade:</label>
          <select v-model="filters.difficulty" class="border rounded-lg px-3 py-2">
            <option value="">Todas</option>
            <option value="facil">Facil</option>
            <option value="medio">Media</option>
            <option value="dificil">Dificil</option>
          </select>
        </div>
        <div class="flex-1"></div>
        <p class="text-gray-500 text-sm">
          Mostrando {{ filteredQuestions.length }} de {{ questions.length }}
        </p>
      </div>
    </div>

    <!-- Questions List -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin text-5xl text-indigo-600">...</div>
      <p class="text-gray-500 mt-4">Carregando questoes...</p>
    </div>

    <div v-else-if="questions.length === 0" class="text-center py-12 bg-white rounded-xl shadow-md">
      <div class="text-5xl mb-4 text-gray-300 font-bold">[ ]</div>
      <p class="text-gray-500">Nenhuma questao encontrada.</p>
      <button
        @click="$router.push(`/generate/${sessionId}`)"
        class="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
      >
        Gerar Questoes
      </button>
    </div>

    <div v-else class="space-y-6">
      <div 
        v-for="(question, index) in filteredQuestions" 
        :key="question.id"
        class="bg-white rounded-xl shadow-md p-6"
      >
        <!-- Question Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <span class="text-2xl font-bold text-indigo-600">{{ index + 1 }}</span>
            <span 
              :class="[
                'px-2 py-1 rounded text-xs font-medium',
                question.question_type === 'multiple_choice' ? 'bg-blue-100 text-blue-800' : '',
                question.question_type === 'true_false' ? 'bg-purple-100 text-purple-800' : '',
                question.question_type === 'essay' ? 'bg-orange-100 text-orange-800' : ''
              ]"
            >
              {{ typeLabel(question.question_type) }}
            </span>
            <span 
              :class="[
                'px-2 py-1 rounded text-xs font-medium',
                question.difficulty === 'easy' ? 'bg-green-100 text-green-800' : '',
                question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' : '',
                question.difficulty === 'hard' ? 'bg-red-100 text-red-800' : ''
              ]"
            >
              {{ difficultyLabel(question.difficulty) }}
            </span>
          </div>
          
          <div class="flex gap-2">
            <button
              @click="editQuestion(question)"
              class="text-gray-500 hover:text-indigo-600 p-2"
              title="Editar"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
            </button>
            <button
              @click="regenerateQuestion(question.id)"
              class="text-gray-500 hover:text-blue-600 p-2"
              title="Regenerar"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            </button>
            <button
              @click="deleteQuestion(question.id)"
              class="text-gray-500 hover:text-red-600 p-2"
              title="Excluir"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
          </div>
        </div>

        <!-- Question Content -->
        <div v-if="editingQuestion?.id === question.id" class="space-y-4">
          <!-- Edit Mode -->
          <textarea
            v-model="editingQuestion.content"
            rows="3"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg"
          ></textarea>
          
          <div v-if="question.question_type === 'multiple_choice'" class="space-y-2">
            <p class="font-medium text-gray-700">Alternativas:</p>
            <div v-for="(option, i) in editingQuestion.options" :key="i" class="flex items-center gap-2">
              <input
                type="radio"
                :checked="editingQuestion.correct_answer === option"
                @change="editingQuestion.correct_answer = option"
              />
              <input
                v-model="editingQuestion.options[i]"
                class="flex-1 px-3 py-2 border rounded-lg"
              />
            </div>
          </div>
          
          <div v-else-if="question.question_type === 'true_false'" class="space-y-2">
            <p class="font-medium text-gray-700">Resposta:</p>
            <select v-model="editingQuestion.correct_answer" class="px-3 py-2 border rounded-lg">
              <option value="true">Verdadeiro</option>
              <option value="false">Falso</option>
            </select>
          </div>
          
          <div class="space-y-2">
            <p class="font-medium text-gray-700">Justificativa:</p>
            <textarea
              v-model="editingQuestion.justification"
              rows="2"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg"
            ></textarea>
          </div>
          
          <div class="flex gap-3">
            <button
              @click="saveEdit"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
            >
              Salvar
            </button>
            <button
              @click="editingQuestion = null"
              class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg"
            >
              Cancelar
            </button>
          </div>
        </div>

        <div v-else>
          <!-- View Mode -->
          <p class="text-gray-800 text-lg mb-4">{{ question.content }}</p>
          
          <!-- Multiple Choice Options -->
          <div v-if="question.question_type === 'multiple_choice'" class="space-y-2 mb-4">
            <div 
              v-for="(option, i) in question.options" 
              :key="i"
              :class="[
                'p-3 rounded-lg',
                option === question.correct_answer ? 'bg-green-100 border-2 border-green-500' : 'bg-gray-50'
              ]"
            >
              <span class="font-medium mr-2">{{ String.fromCharCode(65 + i) }})</span>
              {{ option }}
              <span v-if="option === question.correct_answer" class="text-green-600 ml-2">(correta)</span>
            </div>
          </div>
          
          <!-- True/False Answer -->
          <div v-else-if="question.question_type === 'true_false'" class="mb-4">
            <p class="text-gray-700">
              <strong>Resposta:</strong> 
              <span :class="question.correct_answer === 'true' ? 'text-green-600' : 'text-red-600'">
                {{ question.correct_answer === 'true' ? 'Verdadeiro' : 'Falso' }}
              </span>
            </p>
          </div>
          
          <!-- Justification -->
          <div v-if="question.justification" class="bg-blue-50 p-4 rounded-lg">
            <p class="text-sm text-gray-600">
              <strong>Justificativa:</strong> {{ question.justification }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionsStore } from '../stores/questions'

const route = useRoute()
const router = useRouter()
const questionsStore = useQuestionsStore()
const showToast = inject('showToast')

const sessionId = route.params.sessionId
const loading = ref(true)
const editingQuestion = ref(null)

const filters = ref({
  type: '',
  difficulty: ''
})

const questions = computed(() => questionsStore.questions)

const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    if (filters.value.type && q.question_type !== filters.value.type) return false
    if (filters.value.difficulty && q.difficulty !== filters.value.difficulty) return false
    return true
  })
})

onMounted(async () => {
  const result = await questionsStore.fetchQuestions(sessionId)
  loading.value = false
  
  if (!result.success) {
    showToast('Erro ao carregar questões', 'error')
  }
})

const typeLabel = (type) => {
  const labels = {
    'multipla_escolha': 'Multipla Escolha',
    'verdadeiro_falso': 'V/F',
    'dissertativa': 'Dissertativa'
  }
  return labels[type] || type
}

const difficultyLabel = (diff) => {
  const labels = {
    'facil': 'Facil',
    'medio': 'Media',
    'dificil': 'Dificil'
  }
  return labels[diff] || diff
}

const editQuestion = (question) => {
  editingQuestion.value = { 
    ...question,
    options: question.options ? [...question.options] : []
  }
}

const saveEdit = async () => {
  const result = await questionsStore.updateQuestion(editingQuestion.value.id, {
    content: editingQuestion.value.content,
    options: editingQuestion.value.options,
    correct_answer: editingQuestion.value.correct_answer,
    justification: editingQuestion.value.justification
  })
  
  if (result.success) {
    showToast('Questão atualizada!', 'success')
    editingQuestion.value = null
  } else {
    showToast(result.error, 'error')
  }
}

const regenerateQuestion = async (questionId) => {
  if (!confirm('Regenerar esta questão? A versão atual será substituída.')) return
  
  const result = await questionsStore.regenerateQuestion(questionId)
  
  if (result.success) {
    showToast('Questão regenerada!', 'success')
  } else {
    showToast(result.error, 'error')
  }
}

const deleteQuestion = async (questionId) => {
  if (!confirm('Excluir esta questão?')) return
  
  const result = await questionsStore.deleteQuestion(questionId)
  
  if (result.success) {
    showToast('Questão excluída!', 'success')
  } else {
    showToast(result.error, 'error')
  }
}

const exportQuestions = async (format, includeAnswers) => {
  const result = await questionsStore.exportQuestions(sessionId, format, includeAnswers)
  
  if (result.success) {
    showToast('Download iniciado!', 'success')
  } else {
    showToast(result.error, 'error')
  }
}
</script>
