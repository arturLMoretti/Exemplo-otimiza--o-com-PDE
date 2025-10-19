# Makefile para Exemplo de Otimização com PDE
# Uso: make all, make completo, make simples, make clean

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra
LIBS = -lm

# Alvos principais
.PHONY: all completo simples clean help

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
	rm -f *.csv
	@echo "🧹 Executáveis e dados removidos."

# Execução rápida
run-completo: exemplo_adsorcao
	@echo "🚀 Executando modelo completo..."
	./exemplo_adsorcao

run-simples: exemplo_adsorcao_simples
	@echo "🚀 Executando modelo simplificado..."
	./exemplo_adsorcao_simples

# Ajuda
help:
	@echo "📋 Comandos disponíveis:"
	@echo "  make all          - Compila ambos os modelos"
	@echo "  make completo     - Compila apenas o modelo completo"
	@echo "  make simples      - Compila apenas o modelo simplificado"
	@echo "  make run-completo - Compila e executa o modelo completo"
	@echo "  make run-simples  - Compila e executa o modelo simplificado"
	@echo "  make clean        - Remove executáveis"
	@echo "  make clean-all    - Remove executáveis e dados CSV"
	@echo "  make help         - Mostra esta ajuda"

# Informações do sistema
info:
	@echo "🔧 Informações de compilação:"
	@echo "  Compilador: $(CXX)"
	@echo "  Flags: $(CXXFLAGS)"
	@echo "  Bibliotecas: $(LIBS)"
	@$(CXX) --version | head -1