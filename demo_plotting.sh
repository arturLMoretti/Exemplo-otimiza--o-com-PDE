#!/bin/bash
# Demonstração das capacidades de plotagem do projeto
# Execute após ter dados de simulação disponíveis

echo "🎨 Demonstração de Plotagem Científica de Alta Qualidade"
echo "======================================================="

# Verificar se os dados existem
if [ ! -f "Resultados/dados_experimentais.csv" ]; then
    echo "❌ Dados experimentais não encontrados!"
    echo "💡 Execute primeiro: ./exemplo_adsorcao"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi

# Verificar dependências Python
echo "🔍 Verificando dependências Python..."
python3 -c "import numpy, pandas, matplotlib, seaborn" 2>/dev/null || {
    echo "❌ Dependências Python faltando!"
    echo "💡 Execute: make setup-python"
    exit 1
}

echo "✅ Dependências verificadas!"
echo ""

# 1. Gráficos básicos de comparação
echo "📊 1. Gerando gráficos de comparação experimental vs simulado..."
python3 plot_results.py \
    --exp Resultados/dados_experimentais.csv \
    --sim Resultados/simulacao_otimizada.csv \
    --comp Resultados/comparacao_resultados.csv \
    --output Resultados/demo_comparacao \
    --all-plots

if [ $? -eq 0 ]; then
    echo "   ✅ Gráfico gerado: demo_comparacao_comparacao.png"
    echo "   ✅ Análise detalhada: demo_comparacao_analise_detalhada.png"
else
    echo "   ❌ Erro na geração dos gráficos básicos"
fi

echo ""

# 2. Visualizações avançadas
echo "🔬 2. Gerando visualizações avançadas..."
python3 plot_advanced.py \
    --sim-data Resultados/simulacao_otimizada.csv \
    --output Resultados/demo_avancado \
    --all

if [ $? -eq 0 ]; then
    echo "   ✅ Perfil 3D: demo_avancado_perfil_3d.png"
    echo "   ✅ Análise de sensibilidade: demo_avancado_sensibilidade.png"
    echo "   ✅ Mecanismos de adsorção: demo_avancado_mecanismos.png"
    echo "   ✅ Comparação de isotermas: demo_avancado_isotermas.png"
else
    echo "   ❌ Erro na geração das visualizações avançadas"
fi

echo ""

# 3. Relatório técnico
echo "📄 3. Gerando relatório técnico..."
python3 generate_report.py \
    --exp Resultados/dados_experimentais.csv \
    --sim Resultados/simulacao_otimizada.csv \
    --output Resultados/demo_relatorio

if [ $? -eq 0 ]; then
    echo "   ✅ Relatório LaTeX: demo_relatorio.tex"
    if [ -f "demo_relatorio.pdf" ]; then
        echo "   ✅ Relatório PDF: demo_relatorio.pdf"
    else
        echo "   ⚠️  PDF não gerado (LaTeX não disponível)"
    fi
else
    echo "   ❌ Erro na geração do relatório"
fi

echo ""

# 4. Resumo dos arquivos gerados
echo "📂 Arquivos de plotagem gerados:"
echo "================================="

echo ""
echo "📊 GRÁFICOS DE COMPARAÇÃO:"
ls -la Resultados/demo_comparacao_*.png 2>/dev/null | while read line; do
    filename=$(echo $line | awk '{print $9}')
    filesize=$(echo $line | awk '{print $5}')
    echo "   📈 $filename ($filesize bytes)"
done

echo ""
echo "🔬 VISUALIZAÇÕES AVANÇADAS:"
ls -la Resultados/demo_avancado_*.png 2>/dev/null | while read line; do
    filename=$(echo $line | awk '{print $9}')
    filesize=$(echo $line | awk '{print $5}')
    echo "   🎯 $filename ($filesize bytes)"
done

echo ""
echo "📄 RELATÓRIOS TÉCNICOS:"
ls -la Resultados/demo_relatorio.* 2>/dev/null | while read line; do
    filename=$(echo $line | awk '{print $9}')
    filesize=$(echo $line | awk '{print $5}')
    extension="${filename##*.}"
    if [ "$extension" = "tex" ]; then
        echo "   📝 $filename ($filesize bytes) - LaTeX"
    elif [ "$extension" = "pdf" ]; then
        echo "   📚 $filename ($filesize bytes) - PDF"
    fi
done

echo ""

# 5. Instruções para visualização
echo "👀 Como visualizar os resultados:"
echo "================================="
echo ""
echo "🖼️  IMAGENS (PNG):"
echo "   - Linux: xdg-open arquivo.png"
echo "   - macOS: open arquivo.png"
echo "   - Windows: start arquivo.png"
echo ""
echo "📄 RELATÓRIO LaTeX:"
echo "   - Qualquer editor de texto: nano, vim, gedit"
echo "   - LaTeX editor: TeXstudio, Overleaf"
echo ""
echo "📚 RELATÓRIO PDF:"
echo "   - Leitor PDF: evince, Adobe Reader, navegador"
echo ""

# 6. Verificar qualidade das imagens
echo "🔍 Verificação de qualidade:"
echo "============================"

total_images=0
total_size=0

for img in Resultados/demo_*.png; do
    if [ -f "$img" ]; then
        size=$(stat -f%z "$img" 2>/dev/null || stat -c%s "$img" 2>/dev/null)
        total_size=$((total_size + size))
        total_images=$((total_images + 1))
        
        # Verificar se imagem não está vazia
        if [ $size -gt 10000 ]; then
            echo "   ✅ $img - Qualidade adequada"
        else
            echo "   ⚠️  $img - Arquivo muito pequeno (possível erro)"
        fi
    fi
done

if [ $total_images -gt 0 ]; then
    avg_size=$((total_size / total_images))
    echo ""
    echo "📊 Estatísticas:"
    echo "   Total de imagens: $total_images"
    echo "   Tamanho total: $(echo "scale=2; $total_size/1024/1024" | bc 2>/dev/null || echo "$total_size bytes")"
    echo "   Tamanho médio: $(echo "scale=2; $avg_size/1024" | bc 2>/dev/null || echo "$avg_size bytes")"
fi

echo ""
echo "🎉 Demonstração de plotagem concluída!"
echo ""
echo "💡 Dicas para usar em pesquisa:"
echo "   • Use resolução 300 DPI para publicações"
echo "   • Formate gráficos em escala adequada"
echo "   • Inclua barras de erro quando apropriado"
echo "   • Cite as referências do modelo matemático"
echo ""
echo "🔬 Para análise científica:"
echo "   • Verifique R² > 0.95 para excelente ajuste"
echo "   • Analise distribuição dos resíduos"
echo "   • Compare com outros modelos da literatura"
echo "   • Valide com dados experimentais independentes"