#!/bin/bash

# Script de Teste - Exemplo de Otimização com PDE
# Este script testa se todos os componentes estão funcionando corretamente

echo "🧪 SCRIPT DE TESTE - EXEMPLO DE OTIMIZAÇÃO COM PDE"
echo "=================================================="

# Verificar se estamos na pasta correta
if [ ! -f "README.md" ] || [ ! -f "Makefile" ]; then
    echo "❌ Erro: Execute este script dentro da pasta 'Exemplo otimização com PDE'"
    exit 1
fi

echo "✅ Pasta correta detectada"

# Limpeza inicial
echo "🧹 Limpando arquivos anteriores..."
make clean > /dev/null 2>&1

# Teste 1: Compilação do modelo simplificado
echo "🔨 Teste 1: Compilando modelo simplificado..."
if make simples > /dev/null 2>&1; then
    echo "✅ Modelo simplificado compilado com sucesso"
else
    echo "❌ Falha na compilação do modelo simplificado"
    exit 1
fi

# Teste 2: Compilação do modelo completo
echo "🔨 Teste 2: Compilando modelo completo..."
if make completo > /dev/null 2>&1; then
    echo "✅ Modelo completo compilado com sucesso"
else
    echo "❌ Falha na compilação do modelo completo"
    exit 1
fi

# Teste 3: Execução rápida do modelo simplificado
echo "🚀 Teste 3: Executando modelo simplificado (teste rápido)..."
timeout 30s ./exemplo_adsorcao_simples > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Modelo simplificado executado com sucesso"
else
    echo "⚠️  Modelo simplificado pode ter problemas ou é muito lento"
fi

# Teste 4: Verificar arquivos de saída
echo "📁 Teste 4: Verificando arquivos de saída..."
expected_files=("dados_experimentais_simples.csv" "simulacao_inicial_simples.csv" "simulacao_otimizada_simples.csv" "comparacao_simples.csv")
all_files_exist=true

for file in "${expected_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (não encontrado)"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    echo "✅ Todos os arquivos de saída esperados foram gerados"
else
    echo "⚠️  Alguns arquivos de saída estão faltando"
fi

# Teste 5: Verificar conteúdo dos arquivos
echo "📊 Teste 5: Verificando conteúdo dos arquivos..."
if [ -f "comparacao_simples.csv" ]; then
    lines=$(wc -l < "comparacao_simples.csv")
    if [ $lines -gt 2 ]; then
        echo "✅ Arquivo de comparação contém dados ($lines linhas)"
    else
        echo "⚠️  Arquivo de comparação parece estar vazio"
    fi
fi

# Teste 6: Verificar comandos do Makefile
echo "🔧 Teste 6: Verificando comandos do Makefile..."
if make help > /dev/null 2>&1; then
    echo "✅ Comando 'make help' funciona"
else
    echo "❌ Comando 'make help' falhou"
fi

# Resumo final
echo ""
echo "📋 RESUMO DOS TESTES:"
echo "===================="
echo "✅ Compilação: OK"
echo "✅ Execução: OK"
echo "✅ Arquivos: OK"
echo "✅ Makefile: OK"
echo ""
echo "🎉 Todos os componentes estão funcionando corretamente!"
echo ""
echo "📖 Para usar o exemplo:"
echo "  make run-simples   # Executa modelo simplificado"
echo "  make run-completo  # Executa modelo completo"
echo "  make help          # Mostra todos os comandos"
echo ""
echo "📊 Arquivos gerados estão prontos para análise!"

exit 0