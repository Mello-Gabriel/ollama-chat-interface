#!/bin/bash

# 🔄 Script Completo de Renomeação do Repositório
# Este script atualiza todas as referências após renomeação no GitHub

set -e

# Configurações
OLD_NAME="sort_files"
NEW_NAME="ollama-chat-interface"
GITHUB_USER="Mello-Gabriel"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "🔄 Atualizando referências do repositório..."
echo "   De: $OLD_NAME"
echo "   Para: $NEW_NAME"
echo

# 1. Atualizar remote URL
print_step "1. Atualizando URL do remote..."
git remote set-url origin "https://github.com/$GITHUB_USER/$NEW_NAME.git"
print_success "Remote URL atualizada"

# 2. Atualizar setup.sh
print_step "2. Atualizando setup.sh..."
sed -i.bak "s|$GITHUB_USER/$OLD_NAME|$GITHUB_USER/$NEW_NAME|g" setup.sh
sed -i.bak "s|PROJECT_DIR=\"$OLD_NAME\"|PROJECT_DIR=\"$NEW_NAME\"|g" setup.sh
print_success "setup.sh atualizado"

# 3. Atualizar README.md
print_step "3. Atualizando README.md..."
sed -i.bak "s|$GITHUB_USER/$OLD_NAME|$GITHUB_USER/$NEW_NAME|g" README.md
print_success "README.md atualizado"

# 4. Atualizar rename_repo.sh (caso exista)
if [[ -f "rename_repo.sh" ]]; then
    print_step "4. Atualizando rename_repo.sh..."
    sed -i.bak "s|OLD_REPO_NAME=\"$OLD_NAME\"|OLD_REPO_NAME=\"$OLD_NAME\"|g" rename_repo.sh
    sed -i.bak "s|NEW_REPO_NAME=\".*\"|NEW_REPO_NAME=\"$NEW_NAME\"|g" rename_repo.sh
    print_success "rename_repo.sh atualizado"
fi

# 5. Remover arquivos de backup
print_step "5. Limpando arquivos temporários..."
rm -f *.bak
print_success "Arquivos temporários removidos"

# 6. Testar conectividade
print_step "6. Testando conectividade..."
if git ls-remote origin &>/dev/null; then
    print_success "Conectividade OK"
else
    print_warning "Problema de conectividade - verifique se o repositório foi renomeado no GitHub"
fi

# 7. Mostrar status
print_step "7. Status das mudanças:"
git status --porcelain

echo
print_success "✅ Todas as referências foram atualizadas!"
echo
echo "📝 Próximos passos:"
echo "   1. Revisar as mudanças: git diff"
echo "   2. Fazer commit: git add . && git commit -m 'docs: update repo URLs after rename'"
echo "   3. Fazer push: git push origin master"
echo "   4. Renomear pasta local: cd .. && mv $OLD_NAME $NEW_NAME"
echo
print_success "🎉 Histórico de commits preservado!"
