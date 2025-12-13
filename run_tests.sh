#!/bin/bash

# ===========================================
# Script de Testes - QuestGen AI
# ===========================================

set -e

echo "Iniciando testes do QuestGen AI..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -d "backend" ]; then
    echo -e "${RED}ERRO: Execute este script do diretório raiz do projeto (TC5)${NC}"
    exit 1
fi

cd backend

# Verificar se venv existe ou criar
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar dependências
echo "Instalando dependencias..."
pip install -r requirements.txt -q

# Executar testes
echo ""
echo "Executando testes..."
echo "==========================================="

pytest tests/ -v --tb=short

echo ""
echo "==========================================="
echo -e "${GREEN}Testes concluidos com sucesso!${NC}"
