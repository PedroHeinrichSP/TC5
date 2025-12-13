<template>
  <div class="min-h-screen flex flex-col">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-20">
      <div class="max-w-4xl mx-auto text-center px-4">
        <h1 class="text-5xl font-bold mb-6">
          Gerador de Questoes com IA
        </h1>
        <p class="text-xl mb-8 opacity-90">
          Transforme seus materiais academicos em questoes de alta qualidade 
          automaticamente usando Inteligencia Artificial.
        </p>
        <div class="flex justify-center gap-4">
          <router-link
            to="/register"
            class="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            Comecar Gratis
          </router-link>
          <router-link
            to="/login"
            class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-indigo-600 transition"
          >
            Ja tenho conta
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12 text-gray-800">
          Como Funciona
        </h2>
        
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center p-6">
            <div class="text-5xl mb-4 text-indigo-600 font-bold">1</div>
            <h3 class="text-xl font-semibold mb-2">Upload</h3>
            <p class="text-gray-600">
              Faca upload do seu material em PDF, TXT ou DOCX (ate 50 paginas).
            </p>
          </div>
          
          <div class="text-center p-6">
            <div class="text-5xl mb-4 text-indigo-600 font-bold">2</div>
            <h3 class="text-xl font-semibold mb-2">Geracao</h3>
            <p class="text-gray-600">
              A IA analisa o conteudo e gera questoes de multipla escolha, V/F e dissertativas.
            </p>
          </div>
          
          <div class="text-center p-6">
            <div class="text-5xl mb-4 text-indigo-600 font-bold">3</div>
            <h3 class="text-xl font-semibold mb-2">Revisao</h3>
            <p class="text-gray-600">
              Revise, edite e exporte as questoes em PDF ou CSV.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Question Types -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12 text-gray-800">
          Tipos de Questoes
        </h2>
        
        <div class="grid md:grid-cols-3 gap-6">
          <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center mb-4">
              <span class="text-3xl mr-3 text-blue-600 font-bold">[A]</span>
              <h3 class="text-lg font-semibold">Multipla Escolha</h3>
            </div>
            <p class="text-gray-600 text-sm">
              4-5 alternativas com distratores plausiveis. Ideal para avaliacoes objetivas.
            </p>
          </div>
          
          <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center mb-4">
              <span class="text-3xl mr-3 text-green-600 font-bold">V/F</span>
              <h3 class="text-lg font-semibold">Verdadeiro/Falso</h3>
            </div>
            <p class="text-gray-600 text-sm">
              Com justificativa da resposta correta para facilitar a correcao.
            </p>
          </div>
          
          <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center mb-4">
              <span class="text-3xl mr-3 text-orange-600 font-bold">[D]</span>
              <h3 class="text-lg font-semibold">Dissertativa</h3>
            </div>
            <p class="text-gray-600 text-sm">
              Questoes abertas com pontos-chave sugeridos para avaliacao.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- AI Info -->
    <section class="py-16 bg-white">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-6 text-gray-800">
          Powered by AI
        </h2>
        <p class="text-gray-600 mb-8">
          Utilizamos modelos de IA de ultima geracao para garantir questoes 
          relevantes e de alta qualidade academica.
        </p>
        <div class="flex justify-center gap-8 flex-wrap">
          <div class="flex items-center gap-2 text-gray-500">
            <span class="w-4 h-4 bg-green-500 rounded-full"></span> Google Gemini
          </div>
          <div class="flex items-center gap-2 text-gray-500">
            <span class="w-4 h-4 bg-blue-500 rounded-full"></span> OpenAI GPT
          </div>
          <div class="flex items-center gap-2 text-gray-500">
            <span class="w-4 h-4 bg-purple-500 rounded-full"></span> Claude
          </div>
          <div class="flex items-center gap-2 text-gray-500">
            <span class="w-4 h-4 bg-gray-500 rounded-full"></span> Ollama (Local)
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-16 bg-indigo-600 text-white">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-4">
          Pronto para comecar?
        </h2>
        <p class="mb-8 opacity-90">
          Crie sua conta gratuitamente e gere suas primeiras questoes em minutos.
        </p>
        <router-link
          to="/register"
          class="inline-block bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          Criar Conta Gratis
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
// Home page - no logic needed
</script>
