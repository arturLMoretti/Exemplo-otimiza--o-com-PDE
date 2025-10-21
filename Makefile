# Makefile para Exemplo de Otimização com PDE
# Uso: make all, make completo, make simples, make clean, make plot

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra
LIBS = -lm
PYTHON = python3

# Alvos principais
.PHONY: all completo simples clean help setup-python plot plot-advanced run-with-plots report install-deps demo

all: exemplo_adsorcao exemplo_adsorcao_simples

# Modelo completo (PDE + Nelder-Mead)
exemplo_adsorcao: exemplo_adsorcao.cpp adsorption_optimization.cpp adsorption_optimization.h
	$(CXX) $(CXXFLAGS) -o $@ exemplo_adsorcao.cpp adsorption_optimization.cpp $(LIBS)
	@echo "✅ Modelo completo compilado com sucesso!"

# Modelo simplificado (Cinético + Grid Search)
exemplo_adsorcao_simples: exemplo_adsorcao_simples.cpp
	$(CXX) $(CXXFLAGS) -o $@ exemplo_adsorcao_simples.cpp $(LIBS)
	@echo "✅ Modelo simplificado compilado com sucesso!"

# Aliases
completo: exemplo_adsorcao
simples: exemplo_adsorcao_simples

# Limpeza
clean:
	rm -f exemplo_adsorcao exemplo_adsorcao_simples
	@echo "🧹 Executáveis removidos."

clean-all: clean
	rm -f Resultados/*.csv Resultados/*.png Resultados/*.pdf Resultados/*.tex Resultados/*.svg
	@echo "🧹 Executáveis e dados removidos."

# Execução rápida
run-completo: exemplo_adsorcao
	@echo "🚀 Executando modelo completo..."
	./exemplo_adsorcao

run-simples: exemplo_adsorcao_simples
	@echo "🚀 Executando modelo simplificado..."
	./exemplo_adsorcao_simples

# Executar com plotagem automática
run-with-plots: exemplo_adsorcao plot
	@echo "🚀 Executando modelo completo com plotagem..."
	./exemplo_adsorcao
	@echo "📊 Gerando gráficos de qualidade para publicação..."
	$(PYTHON) plot_results.py --all-plots --output Resultados/resultado_publicacao
	@echo "✅ Simulação e plotagem concluídas!"

# Configuração do ambiente Python
setup-python:
	@echo "🐍 Verificando ambiente Python..."
	@which $(PYTHON) || (echo "❌ Python3 não encontrado!" && exit 1)
	@echo "📦 Instalando dependências Python..."
	@if [ -n "$$VIRTUAL_ENV" ] || [ -n "$$CONDA_DEFAULT_ENV" ]; then \
		echo "🔄 Ambiente virtual detectado, instalando sem --user..."; \
		$(PYTHON) -m pip install -r requirements.txt; \
	else \
		echo "🔄 Sistema Python, instalando com --user..."; \
		$(PYTHON) -m pip install --user -r requirements.txt; \
	fi
	@echo "✅ Ambiente Python configurado!"

# Instalação completa de dependências
install-deps:
	@echo "🔧 Instalando dependências com detecção automática de ambiente..."
	@./install_python_deps.sh
	@echo "🎯 Sistema pronto para uso!"

# Método alternativo de instalação Python
setup-python-alt: install_python_deps.sh
	@echo "🐍 Instalação alternativa de dependências Python..."
	@./install_python_deps.sh

# Plotagem dos resultados
plot: plot_results.py
	@echo "📊 Verificando arquivos de dados..."
	@test -f Resultados/dados_experimentais.csv || (echo "❌ Execute primeiro o modelo para gerar dados!" && exit 1)
	@echo "🎨 Gerando gráficos de comparação..."
	$(PYTHON) plot_results.py --output Resultados/resultado --all-plots
	@echo "✅ Gráficos gerados com sucesso!"

# Plotagem avançada
plot-advanced: plot_advanced.py
	@echo "🎨 Gerando visualizações avançadas..."
	$(PYTHON) plot_advanced.py --all --output Resultados/avancado
	@echo "✅ Visualizações avançadas geradas!"

# Plotagem personalizada
plot-custom:
	@echo "🎨 Gerando plotagem personalizada..."
	@echo "📊 Gráficos básicos..."
	$(PYTHON) plot_results.py --output Resultados/custom
	@echo "🔬 Análises avançadas..."
	$(PYTHON) plot_advanced.py --all --output Resultados/custom_avancado
	@echo "✅ Plotagem personalizada concluída!"

# Geração de relatório técnico
report: plot_results.py generate_report.py
	@echo "📄 Verificando arquivos de dados..."
	@test -f Resultados/dados_experimentais.csv || (echo "❌ Execute primeiro o modelo!" && exit 1)
	@echo "📊 Gerando gráficos para relatório..."
	$(PYTHON) plot_results.py --output Resultados/relatorio --all-plots
	@echo "📝 Gerando relatório técnico em LaTeX..."
	$(PYTHON) generate_report.py --output Resultados/relatorio_tecnico_final
	@echo "✅ Relatório técnico PDF gerado: Resultados/relatorio_tecnico_final.pdf"

# Análise completa (simulação + plotagem + relatório)
full-analysis: exemplo_adsorcao install-deps
	@echo "🚀 Iniciando análise completa..."
	@echo "1️⃣ Executando simulação..."
	./exemplo_adsorcao
	@echo "2️⃣ Gerando visualizações..."
	$(PYTHON) plot_results.py --all-plots --output Resultados/analise_completa
	$(PYTHON) plot_advanced.py --all --output Resultados/analise_avancada
	@echo "3️⃣ Gerando relatório técnico..."
	$(PYTHON) generate_report.py --output Resultados/relatorio_final
	@echo "✅ Análise completa finalizada!"
	@echo "📂 Arquivos gerados na pasta Resultados/:"
	@ls -la Resultados/*.png Resultados/*.csv Resultados/*.tex Resultados/*.pdf 2>/dev/null || echo "   Verifique os arquivos na pasta Resultados/"

# Demonstração completa das capacidades
demo: exemplo_adsorcao install-deps
	@echo "🎭 Iniciando demonstração completa..."
	@echo "Executando simulação para gerar dados..."
	./exemplo_adsorcao
	@echo "Executando demonstração de plotagem..."
	./demo_plotting.sh
	@echo "🎉 Demonstração concluída!"

# Ajuda
help:
	@echo "📋 Comandos disponíveis:"
	@echo ""
	@echo "🔧 CONFIGURAÇÃO:"
	@echo "  make install-deps     - Instala todas as dependências necessárias"
	@echo "  make setup-python     - Configura apenas ambiente Python"
	@echo ""
	@echo "⚙️  COMPILAÇÃO:"
	@echo "  make all              - Compila ambos os modelos"
	@echo "  make completo         - Compila apenas o modelo completo"
	@echo "  make simples          - Compila apenas o modelo simplificado"
	@echo ""
	@echo "🚀 EXECUÇÃO:"
	@echo "  make run-completo     - Compila e executa o modelo completo"
	@echo "  make run-simples      - Compila e executa o modelo simplificado"
	@echo "  make run-with-plots   - Executa modelo + plotagem automática"
	@echo "  make full-analysis    - Análise completa (simulação + plots + relatório)"
	@echo ""
	@echo "📊 VISUALIZAÇÃO:"
	@echo "  make plot             - Gera gráficos de comparação"
	@echo "  make plot-advanced    - Gera visualizações avançadas (3D, sensibilidade)"
	@echo "  make plot-custom      - Gera plotagem personalizada completa"
	@echo "  make report           - Gera relatório técnico em LaTeX/PDF"
	@echo ""
	@echo "🧹 LIMPEZA:"
	@echo "  make clean            - Remove executáveis"
	@echo "  make clean-all        - Remove executáveis e dados CSV"
	@echo "  make clean-plots      - Remove apenas gráficos gerados"
	@echo ""
	@echo "ℹ️  AJUDA:"
	@echo "  make help             - Mostra esta ajuda"
	@echo "  make info             - Mostra informações do sistema"

# Limpeza de gráficos
clean-plots:
	rm -f Resultados/*.png Resultados/*.pdf Resultados/*.svg
	@echo "🧹 Gráficos removidos da pasta Resultados/."

# Informações do sistema
info:
	@echo "🔧 Informações de compilação:"
	@echo "  Compilador: $(CXX)"
	@echo "  Flags: $(CXXFLAGS)"
	@echo "  Bibliotecas: $(LIBS)"
	@$(CXX) --version | head -1