#!/bin/bash

# 🔄 Script para Renomear Repositório Local
# Execute este script no diretório do projeto

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Configurações - ALTERE AQUI
OLD_REPO_NAME="sort_files"
NEW_REPO_NAME="ollama-chat-interface"
GITHUB_USERNAME="Mello-Gabriel"

print_status "Renomeando repositório de '$OLD_REPO_NAME' para '$NEW_REPO_NAME'..."

# 1. Verificar se estamos no repositório correto
if [[ ! -d ".git" ]]; then
    echo "❌ Erro: Execute este script no diretório raiz do repositório"
    exit 1
fi

# 2. Mostrar remote atual
print_status "Remote atual:"
git remote -v

# 3. Atualizar URL do remote
NEW_URL="https://github.com/$GITHUB_USERNAME/$NEW_REPO_NAME.git"
print_status "Atualizando URL do remote para: $NEW_URL"
git remote set-url origin "$NEW_URL"

# 4. Verificar a mudança
print_success "Novo remote configurado:"
git remote -v

# 5. Fazer push para verificar conectividade
print_status "Testando conectividade com o novo repositório..."
git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || {
    print_warning "Não foi possível fazer push automático. Execute manualmente:"
    echo "  git push -u origin main"
    echo "  (ou 'git push -u origin master' se usar master branch)"
}

print_success "✅ Repositório renomeado com sucesso!"
print_status "Próximos passos:"
echo "  1. Renomeie a pasta local se desejar: mv $OLD_REPO_NAME $NEW_REPO_NAME"
echo "  2. Atualize links em documentação/README"
echo "  3. Atualize setup.sh com nova URL"

echo
print_success "🎉 Todos os commits foram preservados!"
