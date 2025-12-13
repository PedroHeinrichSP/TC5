# Arquitetura do Software Baseado em IA
## Sistema Gerador de Questões Acadêmicas

**Projeto:** TC5 - Trabalho de Conclusão de Curso  
**Equipe:** Pedro Heinrich, Pedro Rigotto, Felipe Augusto  
**Instituição:** PUC Minas - Ciência da Computação  
**Data:** 28/09/2025  
**Entrega Final:** 14/12/2025

---

## 1. Visão Geral do Sistema

### 1.1 Propósito
O Sistema Gerador de Questões Acadêmicas é uma aplicação baseada em Inteligência Artificial projetada para auxiliar professores na criação automatizada de avaliações. O sistema processa documentos acadêmicos (PDF, TXT, DOCX) e gera questões de múltipla escolha, verdadeiro/falso e dissertativas, classificando-as por nível de dificuldade.

### 1.2 Objetivos Arquiteturais
- **Modularidade:** Separação clara de responsabilidades em camadas
- **Escalabilidade:** Suporte a múltiplos modelos de IA via configuração
- **Confiabilidade:** Tratamento robusto de falhas e preservação de dados
- **Usabilidade:** Interface intuitiva com feedback visual em tempo real
- **Portabilidade:** Deployment via Docker para diferentes ambientes

---

## 2. Arquitetura em Camadas

### 2.1 Diagrama Arquitetural Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMADA DE APRESENTAÇÃO                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Upload    │ │   Review    │ │    Edit     │ │   Export    ││
│  │ Interface   │ │ Interface   │ │ Interface   │ │ Interface   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────────┐
│                      CAMADA DE API/CONTROLE                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    Auth     │ │   Upload    │ │  Generation │ │   Export    ││
│  │ Controller  │ │ Controller  │ │ Controller  │ │ Controller  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │ Service Layer Interface
┌─────────────────────▼───────────────────────────────────────────┐
│                   CAMADA DE LÓGICA DE NEGÓCIO                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Content   │ │  Question   │ │ Difficulty  │ │ Validation  ││
│  │  Processor  │ │  Generator  │ │ Classifier  │ │   Service   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │ AI Services Interface
┌─────────────────────▼───────────────────────────────────────────┐
│                   CAMADA DE PROCESSAMENTO IA                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    Text     │ │   Topic     │ │     AI      │ │   Quality   ││
│  │  Extractor  │ │  Segmenter  │ │  Interface  │ │  Validator  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                  │                              │
│  ┌─────────────┐ ┌─────────────┐ ├─────────────┐ ┌─────────────┐│
│  │   OpenAI    │ │   Gemini    │ │   Claude    │ │Open Data API││
│  │   Client    │ │   Client    │ │   Client    │ │  Connector  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │ Data Access Interface
┌─────────────────────▼───────────────────────────────────────────┐
│                    CAMADA DE PERSISTÊNCIA                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    User     │ │   Session   │ │  Question   │ │    File     ││
│  │ Repository  │ │ Repository  │ │ Repository  │ │  Storage    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────────────────┐│
│  │   PostgreSQL    │              │      File System           ││
│  │    Database     │              │   (/tmp/uploads/)           ││
│  └─────────────────┘              └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Explicação das Camadas

#### **Camada de Apresentação**
Responsável pela interface do usuário e experiência visual:
- **Upload Interface**: Drag-and-drop para arquivos, validação client-side, barra de progresso
- **Review Interface**: Visualização lado-a-lado do conteúdo original e questões geradas
- **Edit Interface**: Edição inline com validação em tempo real
- **Export Interface**: Configuração de formato e opções de exportação

#### **Camada de API/Controle**
Gerencia as requisições HTTP e orquestra os serviços:
- **Auth Controller**: Autenticação JWT, middleware de autorização
- **Upload Controller**: Validação de arquivos, controle de rate limiting
- **Generation Controller**: Orquestração do pipeline de geração
- **Export Controller**: Geração de PDFs e formatos de exportação

#### **Camada de Lógica de Negócio**
Implementa as regras de negócio específicas do domínio:
- **Content Processor**: Limpeza de texto, normalização, segmentação
- **Question Generator**: Orquestração da geração baseada em templates
- **Difficulty Classifier**: Análise de complexidade lexical e conceitual
- **Validation Service**: Verificação de qualidade e coerência

#### **Camada de Processamento IA**
Integração com modelos de IA e processamento de linguagem natural:
- **Text Extractor**: Extração de texto de PDFs/DOCX usando bibliotecas especializadas
- **Topic Segmenter**: Identificação de tópicos usando TF-IDF e clustering
- **AI Interface**: Factory pattern para múltiplos provedores de IA
- **Quality Validator**: Análise de relevância e precisão factual

#### **Camada de Persistência**
Gerenciamento de dados persistentes e temporários:
- **Repositories**: Padrão Repository para abstração de acesso a dados
- **PostgreSQL**: Dados estruturados (usuários, sessões, questões)
- **File System**: Armazenamento temporário de arquivos uploadados

---

## 3. Fluxo de Dados e Atividades

### 3.1 Diagrama de Fluxo Principal

```
INÍCIO
  │
  ▼
┌─────────────────────┐
│   1. AUTENTICAÇÃO   │ ──── Validação JWT/Session
│                     │      Verificação de permissões
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  2. UPLOAD ARQUIVO  │ ──── Validação tipo/tamanho
│                     │      Armazenamento temporário
│   - PDF validation  │      Verificação integridade
│   - Size check     │
│   - Temp storage   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. EXTRAÇÃO TEXTO   │ ──── PyPDF2/pdfplumber (PDF)
│                     │      python-docx (DOCX)
│   - Remove headers  │      Regex para limpeza
│   - Clean artifacts│      Normalização encoding
│   - Normalize text │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. VALIDAÇÃO        │ ──── Min 500 palavras
│    CONTEÚDO         │      Detecção idioma (PT-BR)
│                     │      Análise qualidade texto
│   - Word count     │
│   - Language detect│
│   - Quality check  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 5. SEGMENTAÇÃO      │ ──── TF-IDF vectorization
│    TÓPICOS          │      K-means clustering
│                     │      Named Entity Recognition
│   - Topic modeling │      Context window creation
│   - Concept extract│
│   - Context windows│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 6. GERAÇÃO IA       │ ──── Prompt engineering
│                     │      Context injection
│   ┌─── OpenAI ────┐ │      Response parsing
│   ├─── Gemini ────┤ │      Fallback handling
│   └─── Claude ────┘ │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 7. CLASSIFICAÇÃO    │ ──── Flesch Reading Ease
│    DIFICULDADE      │      Concept complexity analysis
│                     │      Vocabulary level assessment
│   - Lexical analysis│
│   - Concept depth  │
│   - Cognitive load │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 8. VALIDAÇÃO        │ ──── Fact-checking básico
│    QUALIDADE        │      Coerência contextual
│                     │      Grammar checking
│   - Fact checking  │      Distractor quality
│   - Context match  │
│   - Grammar check  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 9. APRESENTAÇÃO     │ ──── Interface de revisão
│    PARA REVISÃO     │      Edição inline
│                     │      Batch operations
│   - Preview mode   │
│   - Edit interface │
│   - Regeneration   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 10. EXPORTAÇÃO      │ ──── Template PDF generation
│                     │      CSV structured export
│   - PDF generation │      Metadata inclusion
│   - CSV export     │      Answer key options
│   - Metadata       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 11. ARMAZENAMENTO   │ ──── Session persistence
│     HISTÓRICO       │      Cleanup temporary files
│                     │      User activity logging
└─────────────────────┘
```

### 3.2 Atividades Detalhadas por Etapa

#### **Etapa 1: Autenticação**
- **Entrada:** Credenciais do usuário (email/senha)
- **Processamento:** Hash bcrypt, verificação JWT, criação de sessão
- **Saída:** Token de autenticação, contexto do usuário
- **Tratamento de Erro:** Rate limiting, bloqueio por tentativas

#### **Etapa 2: Upload de Arquivo**
- **Entrada:** Arquivo (PDF/DOCX/TXT), metadados
- **Processamento:** Validação MIME type, verificação de tamanho, scan de malware básico
- **Saída:** Arquivo armazenado temporariamente, hash de identificação
- **Tratamento de Erro:** Rejeição de formatos inválidos, cleanup automático

#### **Etapa 3: Extração de Texto**
- **Entrada:** Arquivo validado
- **Processamento:** 
  - PDF: PyPDF2 + pdfplumber para texto complexo
  - DOCX: python-docx para estrutura preservada
  - TXT: encoding detection e normalização
- **Saída:** Texto limpo e normalizado
- **Tratamento de Erro:** Fallback entre bibliotecas, OCR para PDFs problemáticos

#### **Etapa 4: Validação de Conteúdo**
- **Entrada:** Texto extraído
- **Processamento:** Contagem de palavras, detecção de idioma, análise de qualidade
- **Saída:** Texto validado ou sugestões de melhoria
- **Tratamento de Erro:** Recomendações para expansão de conteúdo

#### **Etapa 5: Segmentação de Tópicos**
- **Entrada:** Texto validado
- **Processamento:**
  - TF-IDF para identificação de termos relevantes
  - Clustering K-means para agrupamento de tópicos
  - NER (Named Entity Recognition) para conceitos chave
- **Saída:** Segmentos de texto com tópicos identificados
- **Tratamento de Erro:** Ajuste dinâmico do número de clusters

#### **Etapa 6: Geração via IA**
- **Entrada:** Segmentos de texto, parâmetros de geração
- **Processamento:**
  - Prompt engineering específico por tipo de questão
  - Context injection com Open Data Portal
  - Response parsing e estruturação
- **Saída:** Questões estruturadas com metadados
- **Tratamento de Erro:** Fallback entre provedores, retry com parâmetros ajustados

#### **Etapa 7: Classificação de Dificuldade**
- **Entrada:** Questões geradas
- **Processamento:**
  - Análise lexical (Flesch Reading Ease)
  - Complexidade conceitual
  - Depth de conhecimento requerido
- **Saída:** Questões classificadas (Fácil/Médio/Difícil)
- **Tratamento de Erro:** Classificação padrão com flag de incerteza

#### **Etapa 8: Validação de Qualidade**
- **Entrada:** Questões classificadas
- **Processamento:**
  - Fact-checking básico contra fonte
  - Análise de coerência contextual
  - Validação gramatical
- **Saída:** Questões validadas com score de qualidade
- **Tratamento de Erro:** Marcação de questões suspeitas para revisão manual

#### **Etapas 9-11: Interface e Persistência**
- **Processamento:** Apresentação interativa, edição, exportação e armazenamento
- **Integração:** Feedback loop para melhoria contínua do sistema

---

## 4. Técnicas e Algoritmos de IA

### 4.1 Processamento de Linguagem Natural (NLP)

#### **4.1.1 Text Preprocessing Pipeline**
```python
# Pipeline de pré-processamento
def preprocess_text(raw_text):
    # 1. Limpeza inicial
    text = remove_artifacts(raw_text)  # Headers, footers, page numbers
    
    # 2. Normalização
    text = normalize_encoding(text)    # UTF-8 standardization
    text = normalize_whitespace(text)  # Espaços consistentes
    
    # 3. Tokenização
    tokens = advanced_tokenize(text)   # NLTK + spaCy hybrid
    
    # 4. Filtering
    tokens = remove_stopwords(tokens, language='pt')
    tokens = filter_by_pos(tokens)    # Manter substantivos, verbos, adjetivos
    
    return tokens
```

#### **4.1.2 Topic Modeling com TF-IDF + K-Means**
```python
# Implementação de segmentação de tópicos
class TopicSegmenter:
    def __init__(self, n_topics=5, min_cluster_size=100):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='portuguese'
        )
        self.kmeans = KMeans(n_clusters=n_topics, random_state=42)
    
    def segment_content(self, text_chunks):
        # 1. Vectorização TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(text_chunks)
        
        # 2. Clustering K-Means
        clusters = self.kmeans.fit_predict(tfidf_matrix)
        
        # 3. Extração de tópicos representativos
        topics = self._extract_topic_keywords(clusters, tfidf_matrix)
        
        return topics, clusters
```

#### **4.1.3 Named Entity Recognition (NER)**
- **Biblioteca:** spaCy pt_core_news_sm
- **Entidades Alvo:** PERSON, ORG, GPE, DATE, MONEY, PERCENT
- **Aplicação:** Identificação de conceitos específicos para geração de questões focadas

### 4.2 Modelos de Linguagem Large Language Models (LLMs)

#### **4.2.1 Factory Pattern para Múltiplos Provedores**
```python
class AIProviderFactory:
    @staticmethod
    def create_provider(provider_name):
        providers = {
            'openai': OpenAIProvider(),
            'gemini': GeminiProvider(), 
            'claude': ClaudeProvider()
        }
        return providers.get(provider_name, OpenAIProvider())

class OpenAIProvider(AIProvider):
    def generate_questions(self, context, parameters):
        prompt = self._build_prompt(context, parameters)
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return self._parse_response(response)
```

#### **4.2.2 Prompt Engineering Especializado**

**Template para Questões de Múltipla Escolha:**
```
CONTEXTO: {extracted_text}
TÓPICO: {identified_topic}
DIFICULDADE: {target_difficulty}

INSTRUÇÃO: Baseado no contexto fornecido, gere UMA questão de múltipla escolha seguindo estas regras:

1. A questão deve ser factual e extraível do contexto
2. Inclua 4 alternativas: 1 correta e 3 distratores plausíveis
3. Distratores devem ser conceitualmente relacionados mas incorretos
4. Forneça justificativa de 2-3 linhas para a resposta correta
5. Use linguagem acadêmica apropriada para nível {target_difficulty}

FORMATO DE SAÍDA:
QUESTÃO: [texto da questão]
A) [alternativa A]
B) [alternativa B] 
C) [alternativa C]
D) [alternativa D]
RESPOSTA: [letra correta]
JUSTIFICATIVA: [explicação da resposta]
```

### 4.3 Classificação de Dificuldade

#### **4.3.1 Algoritmo Híbrido de Classificação**
```python
class DifficultyClassifier:
    def __init__(self):
        self.flesch_calculator = FleschReadingEase()
        self.concept_analyzer = ConceptComplexityAnalyzer()
        self.vocab_analyzer = VocabularyLevelAnalyzer()
    
    def classify_difficulty(self, question_data):
        # 1. Análise lexical (30% do score)
        flesch_score = self.flesch_calculator.score(question_data['text'])
        lexical_weight = self._normalize_flesch(flesch_score) * 0.3
        
        # 2. Complexidade conceitual (50% do score)  
        concept_score = self.concept_analyzer.analyze(question_data['context'])
        concept_weight = concept_score * 0.5
        
        # 3. Nível vocabular (20% do score)
        vocab_score = self.vocab_analyzer.analyze(question_data['text'])
        vocab_weight = vocab_score * 0.2
        
        # 4. Score final
        final_score = lexical_weight + concept_weight + vocab_weight
        
        return self._score_to_difficulty(final_score)
```

#### **4.3.2 Métricas de Complexidade Conceitual**
- **Depth Score:** Número de conceitos pré-requisito necessários
- **Abstraction Level:** Grau de abstração (concreto → teórico)
- **Cognitive Load:** Quantidade de informação para processamento simultâneo

### 4.4 Quality Validation Pipeline

#### **4.4.1 Fact-Checking Algoritm**
```python
class FactChecker:
    def validate_question_against_source(self, question, source_text):
        # 1. Extração de claims da questão
        claims = self.extract_claims(question['text'])
        
        # 2. Busca por evidências no texto fonte
        evidence_scores = []
        for claim in claims:
            similarity = self.semantic_similarity(claim, source_text)
            evidence_scores.append(similarity)
        
        # 3. Score de factualidade
        factuality_score = np.mean(evidence_scores)
        
        return {
            'is_factual': factuality_score > 0.8,
            'confidence': factuality_score,
            'problematic_claims': [c for c, s in zip(claims, evidence_scores) if s < 0.6]
        }
```

---

## 5. Integração com Portal de Dados Abertos

### 5.1 Escolha do Dataset: Portal Brasileiro de Dados Abertos

#### **5.1.1 Dataset Selecionado:** 
**"Dados Educacionais - ENADE e Indicadores de Qualidade da Educação Superior"**
- **URL:** https://dados.gov.br/dados/conjuntos-dados/microdados-do-enade
- **Formato:** CSV/JSON APIs
- **Volume:** ~2.3M registros de avaliações educacionais
- **Atualização:** Anual (INEP)

#### **5.1.2 Justificativa da Escolha:**
1. **Relevância Temática:** Dados sobre avaliação educacional complementam sistema de questões acadêmicas
2. **Qualidade dos Dados:** Fonte oficial (INEP/MEC) com alta confiabilidade
3. **Volume Adequado:** Suficiente para enrichment sem overhead computacional excessivo
4. **Estrutura Compatível:** Metadados estruturados fáceis de integrar

### 5.2 Arquitetura de Integração

#### **5.2.1 Componente Open Data Connector**
```python
class OpenDataConnector:
    def __init__(self):
        self.base_url = "https://api.dados.gov.br/v1"
        self.cache = RedisCache(ttl=3600)  # Cache 1 hora
    
    def enrich_question_context(self, topic_keywords):
        # 1. Busca dados relevantes por keywords
        query_params = {
            'q': ' OR '.join(topic_keywords),
            'dataset': 'enade-indicadores',
            'format': 'json',
            'limit': 50
        }
        
        # 2. Cache check
        cache_key = f"opendata_{hash(str(query_params))}"
        if cached_data := self.cache.get(cache_key):
            return cached_data
        
        # 3. API call
        response = requests.get(f"{self.base_url}/search", params=query_params)
        data = response.json()
        
        # 4. Processamento e cache
        enriched_context = self._process_open_data(data, topic_keywords)
        self.cache.set(cache_key, enriched_context)
        
        return enriched_context
```

#### **5.2.2 Fluxo de Enrichment**
```
Tópicos Identificados
         │
         ▼
┌─────────────────────┐
│   Query Builder     │ ──── Construção de consulta baseada em keywords
│                     │      Mapeamento de termos acadêmicos
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Open Data Portal   │ ──── API call para dados.gov.br
│      API Call       │      Rate limiting e retry logic
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Data Processing    │ ──── Filtro por relevância
│   & Filtering       │      Normalização de formato
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Context Enrichment  │ ──── Injeção de estatísticas
│                     │      Dados complementares
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Enhanced Question   │ ──── Questões com contexto enriquecido
│   Generation        │      Exemplos baseados em dados reais
└─────────────────────┘
```

### 5.3 Casos de Uso da Integração

#### **5.3.1 Enrichment de Questões sobre Estatísticas Educacionais**
**Exemplo:**
- **Tópico Original:** "Avaliação do Ensino Superior"
- **Dados Open Data:** Médias ENADE por curso/região
- **Questão Enriquecida:**
  ```
  Baseado nos dados do ENADE 2022, qual região brasileira apresentou 
  a maior média no componente específico de Ciência da Computação?
  
  A) Norte (média: 2.1)
  B) Nordeste (média: 2.3) 
  C) Sudeste (média: 2.8)
  D) Sul (média: 2.6)
  
  Dados: Portal de Dados Abertos (dados.gov.br/enade-2022)
  ```

#### **5.3.2 Contextualização com Indicadores Reais**
- **Questões Dissertativas:** Incorporação de estatísticas atuais para análise crítica
- **Questões V/F:** Validação de afirmações com dados oficiais
- **Múltipla Escolha:** Alternativas baseadas em valores estatísticos reais

### 5.4 Implementação Técnica

#### **5.4.1 Data Schema Integration**
```python
@dataclass
class EnrichedQuestionContext:
    original_context: str
    topic_keywords: List[str]
    open_data_references: List[Dict[str, Any]]
    statistical_context: Dict[str, float]
    source_metadata: Dict[str, str]
    
class QuestionEnricher:
    def enrich_with_open_data(self, question_context: QuestionContext) -> EnrichedQuestionContext:
        # 1. Extract relevant keywords
        keywords = self.extract_keywords(question_context.text)
        
        # 2. Query open data portal
        open_data = self.open_data_connector.search(keywords)
        
        # 3. Build enriched context
        return EnrichedQuestionContext(
            original_context=question_context.text,
            topic_keywords=keywords,
            open_data_references=open_data['references'],
            statistical_context=open_data['statistics'],
            source_metadata=open_data['metadata']
        )
```

#### **5.4.2 Cache e Performance**
- **Redis Cache:** TTL de 1 hora para dados estáticos
- **Rate Limiting:** Máximo 100 requests/minuto para API externa
- **Fallback Strategy:** Sistema funcional mesmo sem conectividade externa
- **Data Validation:** Verificação de integridade dos dados externos

---

## 6. Padrões de Projeto Aplicados

### 6.1 Factory Pattern
- **Aplicação:** Criação de provedores de IA (OpenAI, Gemini, Claude)
- **Benefício:** Troca transparente de modelos via configuração

### 6.2 Repository Pattern
- **Aplicação:** Camada de persistência (User, Session, Question repositories)
- **Benefício:** Abstração do acesso a dados, facilita testes unitários

### 6.3 Strategy Pattern
- **Aplicação:** Algoritmos de classificação de dificuldade
- **Benefício:** Flexibilidade para experimentar diferentes abordagens

### 6.4 Observer Pattern
- **Aplicação:** Sistema de notificações de progresso
- **Benefício:** Interface reativa com feedback em tempo real

### 6.5 Template Method Pattern
- **Aplicação:** Pipeline de geração de questões
- **Benefício:** Estrutura consistente com customização por tipo

---

## 7. Considerações de Implementação

### 7.1 Tecnologias Selecionadas

#### **Backend:**
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Cache:** Redis
- **Task Queue:** Celery para processamento assíncrono
- **Testing:** pytest + pytest-asyncio

#### **Frontend:**
- **Framework:** Vue.js 3 + Composition API
- **UI Library:** Quasar Framework
- **State Management:** Pinia
- **HTTP Client:** Axios

#### **DevOps:**
- **Containerization:** Docker + Docker Compose
- **Process Management:** Gunicorn + Uvicorn workers
- **Monitoring:** Prometheus + Grafana
- **Logging:** Structured JSON logs

### 7.2 Configuração de Ambiente

#### **7.2.1 Docker Compose Structure**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/questgen
      - REDIS_URL=redis://redis:6379
      - AI_PROVIDER=openai
    depends_on: [db, redis]
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [web]
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: questgen
    volumes: ["postgres_data:/var/lib/postgresql/data"]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  worker:
    build: ./backend
    command: celery worker -A app.celery
    depends_on: [db, redis]
```

### 7.3 Métricas e Observabilidade

#### **7.3.1 KPIs do Sistema**
- **Performance:** Tempo médio de geração por questão (target: <3s)
- **Quality:** Taxa de aceitação de questões geradas (target: >85%)
- **Reliability:** Uptime do sistema (target: >98%)
- **User Experience:** Tempo total do fluxo usuário (target: <5min)

#### **7.3.2 Logging Strategy**
```python
# Structured logging example
import structlog

logger = structlog.get_logger()

def generate_questions(user_id, content_hash, params):
    logger.info(
        "question_generation_started",
        user_id=user_id,
        content_hash=content_hash,
        question_count=params.count,
        ai_provider=params.provider
    )
    
    try:
        questions = ai_service.generate(content, params)
        logger.info(
            "question_generation_completed",
            user_id=user_id,
            questions_generated=len(questions),
            avg_difficulty=calculate_avg_difficulty(questions)
        )
        return questions
    except Exception as e:
        logger.error(
            "question_generation_failed",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

---

## 8. Considerações de Segurança e Privacidade

### 8.1 Proteção de Dados
- **Criptografia:** Dados sensíveis em repouso (AES-256)
- **Sanitização:** Remoção automática de informações pessoais dos textos
- **Retention Policy:** Exclusão automática de arquivos após 7 dias
- **Audit Trail:** Log completo de acessos e operações

### 8.2 Compliance Acadêmica
- **Transparência:** Avisos claros sobre uso de IA
- **Attribution:** Referências às fontes originais mantidas
- **Academic Integrity:** Guidelines para uso ético das questões geradas
- **Data Ownership:** Usuários mantêm direitos sobre conteúdo original

---

## 9. Cronograma de Desenvolvimento

### 9.1 Sprint Planning (Timeline até 14/12/2025)

#### **Sprint 1-2 (Out 2025): MVP Core**
- Autenticação básica e upload de arquivos
- Extração de texto e pipeline básico
- Integração com um modelo de IA (OpenAI)
- Interface básica de visualização

#### **Sprint 3-4 (Nov 2025): IA Enhancement**
- Implementação de múltiplos provedores
- Sistema de classificação de dificuldade
- Validação de qualidade
- Integração com Open Data Portal

#### **Sprint 5-6 (Dez 2025): Polish & Deploy**
- Interface completa de edição
- Sistema de exportação
- Testes de carga e otimização
- Documentação e deployment final

### 9.2 Entregáveis
- **Código fonte** completo no GitHub
- **Documentação técnica** e de usuário
- **Ambiente Docker** pronto para produção
- **Apresentação final** com demos ao vivo
- **Este documento de arquitetura** como referência técnica

---

## Conclusão

Esta arquitetura fornece uma base sólida para o desenvolvimento do Sistema Gerador de Questões Acadêmicas, balanceando complexidade técnica com viabilidade de implementação no prazo acadêmico. A integração com o Portal de Dados Abertos adiciona valor significativo ao enriquecer questões com informações estatísticas reais, enquanto a arquitetura modular permite evolução incremental e manutenibilidade.

O sucesso do projeto dependerá da execução disciplinada desta arquitetura, com ênfase em testes contínuos, feedback dos usuários e iterações baseadas em métricas de qualidade objetivas.

---

**Documento preparado por:** Pedro Heinrich, Pedro Rigotto, Felipe Augusto  
**Revisão técnica:** [A ser preenchido após review]  
**Aprovação acadêmica:** [A ser preenchido pelo orientador]