# Gerador de Questoes Academicas com IA

Sistema para geracao automatica de questoes academicas a partir de documentos PDF, DOCX e TXT, utilizando Inteligencia Artificial.

## Quick Start

### Pre-requisitos

- Docker e Docker Compose instalados
- (Opcional) Chave de API de um provedor de IA para melhor qualidade

### Opcoes 100% Gratuitas

1. **Google Gemini (Recomendado)** - Gratuito com limites generosos
   - Obtenha uma chave em: https://makersuite.google.com/app/apikey
   - Configure: `AI_PROVIDER=gemini`

2. **Ollama (Local)** - Totalmente gratuito, roda na sua maquina
   - Instale: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Baixe um modelo: `ollama pull llama3.2`
   - Configure: `AI_PROVIDER=ollama`

### Instalacao

1. **Clone o repositorio**
```bash
git clone https://github.com/PedroHeinrichSP/TC5.git
cd TC5
```

2. **Configure as variaveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env:
# - Para Gemini: adicione GOOGLE_API_KEY
# - Para Ollama: configure AI_PROVIDER=ollama
```

3. **Inicie os containers**
```bash
docker-compose up --build
```

4. **Acesse a aplicacao**
- **Frontend**: http://localhost
- **API Swagger**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Testes

### Executar todos os testes
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Executar testes com cobertura
```bash
pytest --cov=app --cov-report=html
```

### Executar testes especificos
```bash
# Testes de autenticacao
pytest tests/test_auth.py -v

# Testes de upload
pytest tests/test_upload.py -v

# Testes de geracao
pytest tests/test_generation.py -v

# Testes de integracao
pytest tests/test_integration.py -v
```

## Funcionalidades

### Upload de Arquivos
- Suporte a PDF (ate 50 paginas), DOCX e TXT
- Extracao automatica de texto
- Analise de conteudo e identificacao de topicos

### Geracao de Questoes
- **Multipla Escolha**: 4 alternativas com distratores plausiveis
- **Verdadeiro/Falso**: Com justificativa da resposta
- **Dissertativas**: Com resposta esperada e criterios de avaliacao

### Classificacao de Dificuldade
- Analise automatica baseada em:
  - Complexidade lexical (Flesch Reading Ease)
  - Complexidade conceitual
  - Nivel vocabular

### Exportacao
- PDF (com ou sem gabarito)
- CSV (para analise de dados)
- TXT (formato simples)

## Configuracao

### Variaveis de Ambiente

| Variavel | Descricao | Obrigatorio |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | Sim* |
| `GOOGLE_API_KEY` | Chave da API Google Gemini | Nao |
| `ANTHROPIC_API_KEY` | Chave da API Anthropic Claude | Nao |
| `AI_PROVIDER` | Provedor padrao (openai/gemini/claude) | Nao |
| `SECRET_KEY` | Chave secreta da aplicacao | Sim |
| `DATABASE_URL` | URL do PostgreSQL | Auto |

*Pelo menos uma chave de IA e obrigatoria.

## API Endpoints

### Autenticacao
- `POST /api/v1/auth/register` - Cadastro de usuario
- `POST /api/v1/auth/login` - Login (retorna JWT)
- `GET /api/v1/auth/me` - Dados do usuario atual

### Upload
- `POST /api/v1/upload/file` - Upload de arquivo
- `POST /api/v1/upload/text` - Envio de texto direto

### Geracao
- `POST /api/v1/generate/{session_id}` - Gerar questoes
- `GET /api/v1/generate/sessions` - Listar sessoes
- `GET /api/v1/generate/sessions/{id}` - Detalhes da sessao
- `PUT /api/v1/generate/questions/{id}` - Editar questao
- `DELETE /api/v1/generate/questions/{id}` - Remover questao
- `POST /api/v1/generate/questions/{id}/regenerate` - Regenerar questao

### Exportacao
- `POST /api/v1/export/session/{session_id}` - Exportar questoes

## Arquitetura

```
backend/
├── app/
│   ├── api/routes/          # Endpoints da API
│   ├── core/                # Configuracoes e seguranca
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   └── services/
│       └── ai/              # Servicos de IA
│           ├── providers/   # OpenAI, Gemini, Claude
│           ├── text_extractor.py
│           ├── topic_segmenter.py
│           ├── difficulty_classifier.py
│           └── question_service.py
```

## Equipe

- **Pedro Heinrich** - Claude
- **Pedro Rigotto** - GPT
- **Felipe Augusto** - Gemini

## Licenca

Projeto academico - PUC Minas 2025
