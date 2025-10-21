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
$PYTHON_CMD plot_results.py --all-plots --output Resultados/resultados
$PYTHON_CMD plot_advanced.py --all --output Resultados/avancado

echo "📄 Gerando relatório..."
$PYTHON_CMD generate_report.py --output Resultados/relatorio

echo "✅ Análise completa finalizada!"
echo "📂 Verifique os arquivos gerados na pasta Resultados/:"
ls -la Resultados/*.png Resultados/*.csv Resultados/*.tex 2>/dev/null || echo "   (arquivos na pasta Resultados/)"
