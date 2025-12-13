# Guia de Testes Manuais - QuestGen AI

Este documento descreve como realizar testes manuais no sistema QuestGen AI.

## Pre-requisitos

- Docker e Docker Compose instalados
- Navegador web moderno (Chrome, Firefox, Edge)
- Conexao com internet (para provedores de IA externos)
- (Opcional) Ollama instalado localmente para testes com IA local

## 1. Inicializacao do Sistema

### 1.1 Subir os Containers

```bash
cd /home/Heinrich/TC5
docker-compose up --build
```

Aguarde ate que todos os servicos estejam rodando:
- Backend: http://localhost:8000
- Frontend: http://localhost:80 (ou simplesmente http://localhost)
- PostgreSQL: porta 5432
- Redis: porta 6379

### 1.2 Verificar Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

---

## 2. Testes de Autenticacao

### 2.1 Registro de Usuario

1. Acesse http://localhost
2. Clique em "Registrar"
3. Preencha os campos:
   - Nome: `Usuario Teste`
   - Email: `teste@teste.com`
   - Senha: `Senha123!`
   - Confirmar Senha: `Senha123!`
4. Clique em "Criar Conta"

**Resultado esperado:** Redirecionamento para pagina de login com mensagem de sucesso.

### 2.2 Login

1. Acesse http://localhost/login
2. Preencha:
   - Email: `teste@teste.com`
   - Senha: `Senha123!`
3. Clique em "Entrar"

**Resultado esperado:** Redirecionamento para o Dashboard.

### 2.3 Logout

1. Estando logado, clique no botao "Sair" na navbar
2. Verifique que foi redirecionado para a pagina inicial

**Resultado esperado:** Usuario deslogado, token removido.

### 2.4 Teste de Validacao

1. Tente registrar com email invalido
2. Tente registrar com senha menor que 8 caracteres
3. Tente login com credenciais erradas

**Resultados esperados:** Mensagens de erro apropriadas.

---

## 3. Testes de Upload de Arquivo

### 3.1 Upload de PDF

1. Faca login no sistema
2. Acesse "Gerar Questoes" no menu
3. Na secao de upload, arraste um arquivo PDF (maximo 50 paginas, 20MB)
4. Aguarde o processamento

**Resultado esperado:** Arquivo aceito, texto extraido.

### 3.2 Upload de TXT

1. Repita o processo com um arquivo .txt

**Resultado esperado:** Arquivo aceito, conteudo carregado.

### 3.3 Teste de Validacao de Arquivo

1. Tente enviar arquivo maior que 20MB
2. Tente enviar arquivo de tipo nao suportado (.exe, .zip)
3. Tente enviar PDF com mais de 50 paginas

**Resultados esperados:** Mensagens de erro especificas.

### 3.4 Validacao de Conteudo

1. Tente enviar arquivo com menos de 500 palavras

**Resultado esperado:** Aviso sobre conteudo insuficiente.

---

## 4. Testes de Geracao de Questoes

### 4.1 Configuracao de Geracao

1. Apos upload bem-sucedido, configure os parametros:
   - Quantidade: 5 questoes
   - Tipos: Multipla Escolha, Verdadeiro/Falso
   - Dificuldade: Media
   - Provedor: Ollama (gratuito) ou Gemini (gratuito)

2. Clique em "Gerar Questoes"

**Resultado esperado:** Progresso mostrado, questoes geradas em ate 60 segundos.

### 4.2 Teste com Diferentes Provedores

Repita o teste 4.1 com cada provedor disponivel:
- Ollama (local gratuito)
- Gemini (API gratuita)
- OpenAI (requer API key)
- Claude (requer API key)

### 4.3 Teste de Limite de Questoes

1. Configure para gerar 20 questoes (maximo)
2. Verifique se todas sao geradas corretamente

**Resultado esperado:** Exatamente 20 questoes geradas.

### 4.4 Teste de Tipos de Questao

Gere questoes de cada tipo separadamente:
- Somente Multipla Escolha
- Somente Verdadeiro/Falso
- Somente Dissertativa

**Resultado esperado:** Questoes do tipo correto geradas.

---

## 5. Testes de Revisao e Edicao

### 5.1 Visualizacao de Questoes

1. Apos geracao, acesse a tela de revisao
2. Verifique que todas as questoes sao exibidas
3. Use os filtros por tipo e dificuldade

**Resultado esperado:** Filtros funcionando corretamente.

### 5.2 Edicao de Questao

1. Clique no icone de edicao de uma questao
2. Modifique o enunciado
3. Clique em "Salvar"

**Resultado esperado:** Questao atualizada.

### 5.3 Edicao de Alternativas (Multipla Escolha)

1. Edite uma questao de multipla escolha
2. Modifique as alternativas
3. Altere a resposta correta
4. Salve

**Resultado esperado:** Alternativas e resposta atualizadas.

### 5.4 Regenerar Questao Individual

1. Clique no icone de regenerar em uma questao especifica
2. Confirme a acao

**Resultado esperado:** Nova questao gerada no lugar da anterior.

### 5.5 Excluir Questao

1. Clique no icone de excluir
2. Confirme a exclusao

**Resultado esperado:** Questao removida da lista.

---

## 6. Testes de Exportacao

### 6.1 Exportar PDF com Gabarito

1. Na tela de revisao, clique em "PDF com Gabarito"
2. Aguarde o download

**Resultado esperado:** PDF gerado com questoes e respostas.

### 6.2 Exportar PDF sem Gabarito

1. Clique em "PDF sem Gabarito"
2. Aguarde o download

**Resultado esperado:** PDF gerado apenas com questoes.

### 6.3 Exportar CSV

1. Clique em "CSV"
2. Aguarde o download

**Resultado esperado:** Arquivo CSV com dados estruturados.

### 6.4 Verificar Conteudo Exportado

1. Abra os arquivos exportados
2. Verifique se todas as questoes estao presentes
3. Verifique formatacao e legibilidade

---

## 7. Testes de Performance

### 7.1 Tempo de Geracao

1. Inicie um cronometro
2. Gere 20 questoes de um texto de 2000 palavras
3. Pare o cronometro quando finalizar

**Criterio de aceitacao:** Maximo 60 segundos.

### 7.2 Tempo de Processamento de PDF

1. Inicie um cronometro
2. Faca upload de PDF de 50 paginas
3. Pare quando o texto for extraido

**Criterio de aceitacao:** Maximo 120 segundos.

### 7.3 Responsividade da Interface

1. Navegue entre as paginas do sistema
2. Verifique tempo de carregamento

**Criterio de aceitacao:** Maximo 5 segundos por pagina.

---

## 8. Testes de Interface Responsiva

### 8.1 Teste em Desktop

1. Acesse o sistema em tela cheia (1920x1080)
2. Navegue por todas as paginas
3. Verifique alinhamento e espaçamento

### 8.2 Teste em Tablet

1. Redimensione a janela para 768px de largura
2. Verifique adaptacao dos elementos
3. Teste navegacao e formularios

### 8.3 Teste em Mobile

1. Redimensione para 375px de largura
2. Verifique menu hamburguer (se aplicavel)
3. Teste todos os formularios

---

## 9. Testes de API Direta

Use curl ou Postman para testar endpoints diretamente.

### 9.1 Registro via API

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"api@teste.com","password":"Senha123!","name":"API User"}'
```

### 9.2 Login via API

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=api@teste.com&password=Senha123!"
```

### 9.3 Upload via API

```bash
curl -X POST http://localhost:8000/api/upload/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@documento.pdf"
```

### 9.4 Gerar Questoes via API

```bash
curl -X POST http://localhost:8000/api/generation/generate \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<SESSION_ID>",
    "num_questions": 5,
    "question_types": ["multiple_choice", "true_false"],
    "difficulty": "medium",
    "provider": "ollama"
  }'
```

---

## 10. Testes de Erro e Recuperacao

### 10.1 Conexao Perdida Durante Geracao

1. Inicie geracao de questoes
2. Desconecte a rede brevemente
3. Reconecte

**Resultado esperado:** Sistema mostra erro e permite tentar novamente.

### 10.2 Sessao Expirada

1. Faca login
2. Aguarde o token expirar (ou limpe manualmente)
3. Tente uma acao

**Resultado esperado:** Redirecionamento para login.

### 10.3 Provedor de IA Indisponivel

1. Configure um provedor com credenciais invalidas
2. Tente gerar questoes

**Resultado esperado:** Mensagem de erro clara sobre o provedor.

---

## 11. Checklist de Aceitacao

### Autenticacao
- [ ] Registro de novo usuario funciona
- [ ] Login com credenciais validas funciona
- [ ] Logout remove sessao corretamente
- [ ] Validacoes de formulario funcionam

### Upload
- [ ] Upload de PDF funciona
- [ ] Upload de TXT funciona
- [ ] Validacao de tamanho funciona
- [ ] Validacao de tipo funciona

### Geracao
- [ ] Geracao com Ollama funciona
- [ ] Geracao com Gemini funciona
- [ ] Todos os tipos de questao sao gerados
- [ ] Classificacao de dificuldade funciona

### Revisao
- [ ] Listagem de questoes funciona
- [ ] Filtros funcionam
- [ ] Edicao de questoes funciona
- [ ] Regeneracao individual funciona
- [ ] Exclusao funciona

### Exportacao
- [ ] Exportacao PDF com gabarito funciona
- [ ] Exportacao PDF sem gabarito funciona
- [ ] Exportacao CSV funciona

### Performance
- [ ] Geracao em ate 60 segundos
- [ ] Upload em ate 120 segundos
- [ ] Paginas carregam em ate 5 segundos

---

## 12. Relatorio de Bugs

Ao encontrar um bug, documente:

1. **Descricao**: O que aconteceu
2. **Passos para reproduzir**: Sequencia exata
3. **Resultado esperado**: O que deveria acontecer
4. **Resultado obtido**: O que realmente aconteceu
5. **Ambiente**: Navegador, SO, versao
6. **Screenshots**: Se aplicavel

---

## Contato

Em caso de duvidas sobre os testes, consulte a documentacao em `docs/Arquitetura_Software_IA.md` ou o README principal.
