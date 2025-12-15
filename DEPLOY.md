# Guia de Deploy - QuestGen AI

## Deploy do Frontend (GitHub Pages)

### Passo 1: Habilitar GitHub Pages

1. Va para o repositorio no GitHub
2. Clique em **Settings** > **Pages**
3. Em "Build and deployment", selecione:
   - **Source**: GitHub Actions
4. Salve

### Passo 2: Executar o Deploy

O deploy e automatico quando voce faz push para a branch `main` com mudancas na pasta `frontend/`.

Para executar manualmente:
1. Va em **Actions** no GitHub
2. Selecione "Deploy Frontend to GitHub Pages"
3. Clique em "Run workflow"

### Passo 3: Acessar o Site

Apos o deploy, acesse:
```
https://PedroHeinrichSP.github.io/TC5/
```

---

## Limitacoes do GitHub Pages

O GitHub Pages hospeda apenas arquivos estaticos. O frontend funcionara, mas:

- **Sem backend**: Autenticacao, upload e geracao de questoes NAO funcionarao
- **Apenas demonstracao visual**: Util para mostrar a interface

Para funcionalidade completa, voce precisa hospedar o backend.

---

## Deploy Completo (Frontend + Backend)

### Opcao 1: Railway (Recomendado - Gratuito)

#### Backend no Railway

1. Crie uma conta em https://railway.app
2. Clique em "New Project" > "Deploy from GitHub repo"
3. Selecione o repositorio TC5
4. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Adicione as variaveis de ambiente:
   ```
   SECRET_KEY=sua-chave-secreta
   JWT_SECRET_KEY=jwt-secret
   DATABASE_URL=(Railway fornece automaticamente com Postgres)
   REDIS_URL=(Railway fornece automaticamente com Redis)
   GOOGLE_API_KEY=sua-chave-gemini
   AI_PROVIDER=gemini
   ```

6. Adicione Postgres e Redis como servicos
7. Copie a URL do backend (ex: `https://tc5-backend.railway.app`)

#### Frontend no GitHub Pages

1. Va em **Settings** > **Secrets and variables** > **Actions** > **Variables**
2. Crie a variavel `VITE_API_URL` com valor: `https://tc5-backend.railway.app/api/v1`
3. Execute o workflow novamente

### Opcao 2: Render (Gratuito com limites)

#### Backend no Render

1. Crie uma conta em https://render.com
2. New > Web Service > Connect GitHub
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Adicione variaveis de ambiente (mesmo do Railway)
5. Adicione Postgres (Render oferece gratuito por 90 dias)

### Opcao 3: Fly.io (Gratuito com limites)

```bash
# Instale o CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy backend
cd backend
fly launch
fly secrets set SECRET_KEY=sua-chave GOOGLE_API_KEY=sua-chave
fly deploy
```

---

## Configuracao de CORS

Se hospedar o backend em outro dominio, adicione o dominio do frontend ao CORS.

No arquivo `backend/app/main.py`, atualize:

```python
origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://PedroHeinrichSP.github.io",  # GitHub Pages
    "https://seu-dominio.com",  # Seu dominio personalizado
]
```

---

## Checklist de Deploy

- [ ] Backend hospedado e funcionando
- [ ] Banco de dados PostgreSQL configurado
- [ ] Redis configurado (opcional, para cache)
- [ ] Variavel VITE_API_URL configurada no GitHub
- [ ] CORS configurado para aceitar o dominio do frontend
- [ ] Chave da API Gemini/OpenAI configurada
- [ ] Testar: registro, login, upload, geracao, export

---

## Troubleshooting

### Erro de CORS
Verifique se a URL do frontend esta na lista de origens permitidas no backend.

### 404 no Refresh
O frontend usa hash history (`/#/`) para evitar isso no GitHub Pages.

### API nao responde
Verifique se a variavel `VITE_API_URL` esta correta e o backend esta rodando.

### Erro de autenticacao
Verifique se `SECRET_KEY` e `JWT_SECRET_KEY` estao configuradas no backend.
