#!/bin/bash
# Script de instalação robusta de dependências Python
# Lida com diferentes cenários: venv, conda, sistema, etc.

set -e

echo "🐍 Instalador Inteligente de Dependências Python"
echo "================================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✅]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[⚠️]${NC} $1"; }
print_error() { echo -e "${RED}[❌]${NC} $1"; }

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        print_error "Python 3 necessário! Versão encontrada: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python não encontrado!"
    exit 1
fi

print_success "Python encontrado: $($PYTHON_CMD --version)"

# Detectar pip
if ! command -v $PIP_CMD &> /dev/null; then
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_info "Usando pip via módulo Python"
        PIP_CMD="$PYTHON_CMD -m pip"
    else
        print_error "pip não encontrado!"
        exit 1
    fi
fi

# Detectar ambiente
INSTALL_METHOD=""
ENV_INFO=""

if [ -n "$VIRTUAL_ENV" ]; then
    INSTALL_METHOD="venv"
    ENV_INFO="Virtual Environment: $VIRTUAL_ENV"
elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    INSTALL_METHOD="conda"
    ENV_INFO="Conda Environment: $CONDA_DEFAULT_ENV"
elif [ -n "$PIPENV_ACTIVE" ]; then
    INSTALL_METHOD="pipenv"
    ENV_INFO="Pipenv Environment"
else
    INSTALL_METHOD="system"
    ENV_INFO="Sistema Python"
fi

print_info "Ambiente detectado: $ENV_INFO"

# Função de instalação inteligente
install_packages() {
    local packages_file="$1"
    
    case $INSTALL_METHOD in
        "venv"|"conda"|"pipenv")
            print_info "Instalando em ambiente isolado (sem --user)..."
            $PIP_CMD install -r "$packages_file"
            ;;
        "system")
            print_info "Instalando no sistema (com --user)..."
            # Tentar primeiro com --user
            if $PIP_CMD install --user -r "$packages_file"; then
                print_success "Instalação com --user bem-sucedida"
            else
                print_warning "Falha com --user, tentando sem flags..."
                $PIP_CMD install -r "$packages_file"
            fi
            ;;
        *)
            print_warning "Ambiente não reconhecido, tentando instalação padrão..."
            $PIP_CMD install -r "$packages_file"
            ;;
    esac
}

# Verificar requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_warning "requirements.txt não encontrado, criando com dependências mínimas..."
    cat > requirements.txt << 'EOF'
# Dependências mínimas para plotagem científica
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
EOF
    print_success "requirements.txt criado"
fi

# Instalação principal
print_info "Instalando dependências Python..."
if install_packages "requirements.txt"; then
    print_success "Dependências instaladas com sucesso!"
else
    print_error "Falha na instalação das dependências"
    
    # Tentar instalação individual como fallback
    print_warning "Tentando instalação individual das dependências essenciais..."
    
    essential_packages=("numpy" "pandas" "matplotlib" "seaborn")
    
    for package in "${essential_packages[@]}"; do
        print_info "Instalando $package..."
        case $INSTALL_METHOD in
            "system")
                if ! $PIP_CMD install --user "$package" 2>/dev/null; then
                    $PIP_CMD install "$package"
                fi
                ;;
            *)
                $PIP_CMD install "$package"
                ;;
        esac
        print_success "$package instalado"
    done
fi

# Teste de importação
print_info "Testando importações..."
$PYTHON_CMD -c "
import sys
print(f'Python {sys.version}')

try:
    import numpy as np
    print(f'✅ NumPy {np.__version__}')
except ImportError as e:
    print(f'❌ NumPy: {e}')
    sys.exit(1)

try:
    import pandas as pd
    print(f'✅ Pandas {pd.__version__}')
except ImportError as e:
    print(f'❌ Pandas: {e}')
    sys.exit(1)

try:
    import matplotlib
    print(f'✅ Matplotlib {matplotlib.__version__}')
except ImportError as e:
    print(f'❌ Matplotlib: {e}')
    sys.exit(1)

try:
    import seaborn as sns
    print(f'✅ Seaborn {sns.__version__}')
except ImportError as e:
    print(f'❌ Seaborn: {e}')
    sys.exit(1)

print('🎉 Todas as dependências estão funcionando!')
"

if [ $? -eq 0 ]; then
    print_success "Teste de importação bem-sucedido!"
else
    print_error "Falha no teste de importação"
    exit 1
fi

# Informações finais
echo ""
print_success "Instalação concluída com sucesso!"
echo ""
print_info "Ambiente configurado:"
echo "  Python: $($PYTHON_CMD --version)"
echo "  Método: $INSTALL_METHOD"
echo "  Local: $ENV_INFO"
echo ""
print_info "Para usar:"
echo "  make plot              # Gráficos básicos"
echo "  make plot-advanced     # Visualizações avançadas"
echo "  make report           # Relatório técnico"
echo "  ./demo_plotting.sh    # Demonstração completa"