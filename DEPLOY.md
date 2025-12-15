# Guia de Deploy - QuestGen AI

## Arquitetura de Deploy

```
[GitHub Pages]          [Render.com]
   Frontend    <---->    Backend + PostgreSQL
   (Gratuito)            (Gratuito)
```

---

## PARTE 1: Deploy do Backend (Render.com)

### Passo 1: Criar Conta no Render

1. Acesse https://render.com
2. Clique em "Get Started for Free"
3. Faca login com sua conta GitHub

### Passo 2: Criar o Banco de Dados PostgreSQL

1. No dashboard do Render, clique em **"New +"** > **"PostgreSQL"**
2. Configure:
   - **Name**: `questgen-db`
   - **Database**: `questgen`
   - **User**: `questgen_user`
   - **Region**: Ohio (ou mais proximo)
   - **Plan**: **Free**
3. Clique em **"Create Database"**
4. Aguarde criar e **copie a "External Database URL"** (vai precisar depois)

### Passo 3: Criar o Web Service (Backend)

1. Clique em **"New +"** > **"Web Service"**
2. Conecte seu repositorio GitHub (PedroHeinrichSP/TC5)
3. Configure:
   - **Name**: `questgen-backend`
   - **Region**: Ohio (mesma do banco)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Plan**: **Free**

4. Adicione as **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | (cole a External Database URL do passo anterior) |
   | `SECRET_KEY` | (clique em "Generate" para gerar automaticamente) |
   | `JWT_SECRET_KEY` | (clique em "Generate" para gerar automaticamente) |
   | `GOOGLE_API_KEY` | (sua chave da API Gemini) |
   | `AI_PROVIDER` | `gemini` |
   | `DEBUG` | `false` |
   | `PYTHONPATH` | `/app` |

5. Clique em **"Create Web Service"**

### Passo 4: Aguardar Deploy

- O primeiro deploy leva 5-10 minutos
- Quando aparecer "Live", copie a URL (ex: `https://questgen-backend.onrender.com`)

### Passo 5: Testar o Backend

```bash
curl https://questgen-backend.onrender.com/health
```

Deve retornar: `{"status": "healthy"}`

---

## PARTE 2: Configurar Frontend para usar o Backend

### Passo 1: Adicionar Variavel no GitHub

1. Va para: https://github.com/PedroHeinrichSP/TC5/settings/variables/actions
2. Clique em **"New repository variable"**
3. Configure:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://questgen-backend.onrender.com/api/v1`
   (substitua pela URL real do seu backend)
4. Clique em **"Add variable"**

### Passo 2: Re-executar o Deploy do Frontend

1. Va para: https://github.com/PedroHeinrichSP/TC5/actions
2. Clique em **"Deploy Frontend to GitHub Pages"**
3. Clique em **"Run workflow"** > **"Run workflow"**

### Passo 3: Testar

Acesse: https://PedroHeinrichSP.github.io/TC5/

Agora deve funcionar completamente!

---

## Resumo das URLs

| Servico | URL |
|---------|-----|
| Frontend | https://PedroHeinrichSP.github.io/TC5/ |
| Backend | https://questgen-backend.onrender.com |
| API | https://questgen-backend.onrender.com/api/v1 |

---

## Obter Chave da API Gemini (Gratuita)

1. Acesse: https://makersuite.google.com/app/apikey
2. Faca login com conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada
5. Use no campo `GOOGLE_API_KEY` do Render

---

## Limitacoes do Plano Gratuito

### Render Free Tier:
- Backend "dorme" apos 15 min de inatividade
- Primeira requisicao apos "dormir" leva ~30 segundos
- 750 horas/mes de execucao
- Banco PostgreSQL: 1GB, expira em 90 dias

### GitHub Pages:
- Totalmente gratuito para repositorios publicos
- Sem limitacoes significativas

---

## Troubleshooting

### Backend demora para responder
Normal no plano gratuito. O servico "acorda" apos inatividade.

### Erro de CORS
Verifique se a URL do GitHub Pages esta nas origens permitidas.
O arquivo `backend/app/core/config.py` ja inclui `https://PedroHeinrichSP.github.io`.

### Erro 500 no backend
Verifique os logs no Render: Dashboard > questgen-backend > Logs

### Banco de dados expirou
No plano free, o PostgreSQL expira em 90 dias. Crie um novo e atualize DATABASE_URL.

---

## Alternativas de Hospedagem

### Railway.app
- Mais rapido que Render
- $5 de credito gratuito/mes
- Nao "dorme"

### Fly.io
- 3 VMs gratuitas
- Mais complexo de configurar

### Vercel (apenas frontend)
- Excelente para frontend
- Nao suporta backend Python
