#!/bin/bash
# Setup script para projeto de otimização com PDE
# Configura ambiente completo para desenvolvimento e análise

set -e  # Parar em caso de erro

echo "🚀 Configurando projeto de Otimização com PDE..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "Makefile" ] || [ ! -f "exemplo_adsorcao.cpp" ]; then
    print_error "Execute este script no diretório do projeto!"
    exit 1
fi

print_status "Verificando sistema operacional..."
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac
print_success "Sistema detectado: $MACHINE"

# Verificar compilador C++
print_status "Verificando compilador C++..."
if command -v g++ &> /dev/null; then
    GCC_VERSION=$(g++ --version | head -n1)
    print_success "g++ encontrado: $GCC_VERSION"
else
    print_error "g++ não encontrado! Instale build-essential (Ubuntu) ou Xcode (Mac)"
    exit 1
fi

# Verificar Python
print_status "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        print_success "Python encontrado: $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        print_error "Python 3 necessário! Versão encontrada: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python não encontrado! Instale Python 3.8+"
    exit 1
fi

# Verificar pip
print_status "Verificando pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 encontrado"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    print_success "pip encontrado"
    PIP_CMD="pip"
else
    print_error "pip não encontrado! Instale python3-pip"
    exit 1
fi

# Instalar dependências Python
print_status "Instalando dependências Python..."

# Detectar se estamos em um ambiente virtual
if [ -n "$VIRTUAL_ENV" ] || [ -n "$CONDA_DEFAULT_ENV" ]; then
    print_status "Ambiente virtual detectado: instalando sem --user"
    USER_FLAG=""
else
    print_status "Sistema Python: instalando com --user"
    USER_FLAG="--user"
fi

if [ -f "requirements.txt" ]; then
    print_status "Usando requirements.txt..."
    $PIP_CMD install $USER_FLAG -r requirements.txt
    print_success "Dependências Python instaladas"
else
    print_warning "requirements.txt não encontrado, instalando dependências essenciais..."
    $PIP_CMD install $USER_FLAG numpy pandas matplotlib seaborn scipy
    print_success "Dependências essenciais instaladas"
fi

# Testar importações Python
print_status "Testando importações Python..."
$PYTHON_CMD -c "
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
print('✅ Todas as bibliotecas importadas com sucesso!')
print(f'NumPy: {np.__version__}')
print(f'Pandas: {pd.__version__}')
print(f'Matplotlib: {plt.matplotlib.__version__}')
print(f'Seaborn: {sns.__version__}')
" && print_success "Importações Python OK" || {
    print_error "Erro nas importações Python!"
    exit 1
}

# Compilar projeto
print_status "Compilando projeto C++..."
make clean > /dev/null 2>&1 || true
if make all; then
    print_success "Compilação bem-sucedida"
else
    print_error "Erro na compilação!"
    exit 1
fi

# Verificar LaTeX (opcional)
print_status "Verificando LaTeX (opcional para relatórios PDF)..."
if command -v pdflatex &> /dev/null; then
    LATEX_VERSION=$(pdflatex --version | head -n1)
    print_success "LaTeX encontrado: $LATEX_VERSION"
    LATEX_AVAILABLE=true
else
    print_warning "LaTeX não encontrado. Relatórios PDF não estarão disponíveis."
    print_warning "Para instalar: sudo apt-get install texlive-latex-base texlive-latex-extra (Ubuntu)"
    LATEX_AVAILABLE=false
fi

# Criar script de execução rápida
print_status "Criando script de execução rápida..."
cat > run_analysis.sh << 'EOF'
#!/bin/bash
# Script de execução rápida para análise completa

echo "🚀 Executando análise completa de adsorção..."

# Compilar e executar
make exemplo_adsorcao
echo "📊 Executando simulação..."
./exemplo_adsorcao

# Gerar gráficos
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "🎨 Gerando visualizações..."
$PYTHON_CMD plot_results.py --all-plots --output resultados
$PYTHON_CMD plot_advanced.py --all --output avancado

echo "📄 Gerando relatório..."
$PYTHON_CMD generate_report.py --output relatorio

echo "✅ Análise completa finalizada!"
echo "📂 Verifique os arquivos gerados:"
ls -la *.png *.csv *.tex 2>/dev/null || echo "   (arquivos na pasta do projeto)"
EOF

chmod +x run_analysis.sh
print_success "Script run_analysis.sh criado"

# Resumo final
echo ""
echo "=================================================="
print_success "CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================================="
echo ""
echo "📋 RESUMO DO SISTEMA:"
echo "   Sistema operacional: $MACHINE"
echo "   Compilador C++: ✅ Disponível"
echo "   Python: ✅ $PYTHON_VERSION"
echo "   Bibliotecas Python: ✅ Instaladas e testadas"
if [ "$LATEX_AVAILABLE" = true ]; then
    echo "   LaTeX: ✅ Disponível (relatórios PDF)"
else
    echo "   LaTeX: ⚠️ Não disponível (apenas relatórios .tex)"
fi
echo ""
echo "🚀 COMANDOS DISPONÍVEIS:"
echo ""
echo "   Execução rápida:"
echo "     ./run_analysis.sh        # Análise completa automatizada"
echo ""
echo "   Comandos make:"
echo "     make help                # Lista todos os comandos"
echo "     make full-analysis       # Análise completa via Makefile"
echo "     make run-with-plots      # Simulação + gráficos básicos"
echo ""
echo "   Compilação e execução:"
echo "     make completo            # Compilar modelo"
echo "     ./exemplo_adsorcao       # Executar simulação"
echo ""
echo "   Visualização:"
echo "     $PYTHON_CMD plot_results.py --all-plots"
echo "     $PYTHON_CMD plot_advanced.py --all"
echo "     $PYTHON_CMD generate_report.py"
echo ""
print_success "Sistema pronto para uso! 🎉"
echo ""
echo "💡 Dica: Execute './run_analysis.sh' para começar rapidamente!"