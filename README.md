# 🧪 Otimização de Parâmetros com PDE - Modelo de Adsorção

Este projeto implementa um sistema completo de **otimização de parâmetros** para modelos matemáticos baseados em **Equações Diferenciais Parciais (PDE)**, especificamente para processos de **adsorção em partículas esféricas**.

## 🎯 Características Principais

- **Modelo Matemático Rigoroso**: Difusão em geometria esférica com isoterma de Langmuir
- **Otimização Automática**: Algoritmo Nelder-Mead para estimação de parâmetros
- **Visualização Científica**: Gráficos de alta qualidade para publicação
- **Relatórios Técnicos**: Geração automática de documentos LaTeX/PDF
- **Análise Estatística Completa**: Métricas abrangentes de ajuste do modelo

## 📊 Visualizações Implementadas

### 📈 Gráficos de Comparação
- **Evolução temporal**: Experimental vs Simulado
- **Gráfico de paridade**: Correlação 1:1 com bandas de confiança
- **Análise de resíduos**: Distribuição e tendências dos erros
- **Estatísticas integradas**: R², RMSE, MAE, MAPE no próprio gráfico

### 🔬 Análises Avançadas
- **Perfis 3D**: Evolução espacial e temporal da concentração
- **Análise de sensibilidade**: Efeito dos parâmetros na resposta
- **Comparação de mecanismos**: Diferentes fenômenos de transferência
- **Isotermas de adsorção**: Comparação entre modelos (Langmuir, Freundlich, Linear)

### 📄 Relatórios Técnicos
- **Formato LaTeX/PDF**: Pronto para publicação científica
- **Estatísticas detalhadas**: Análise completa dos resultados
- **Interpretação automática**: Avaliação da qualidade do ajuste
- **Referências bibliográficas**: Incluídas automaticamente

## 🚀 Instalação e Uso

### Instalação Automática (Recomendado)

```bash
# Clone ou baixe o projeto
cd "Exemplo otimização com PDE"

# Execute o script de configuração
./setup.sh

# Ou execute análise completa diretamente
./run_analysis.sh
```

### Instalação Manual

```bash
# 1. Instalar dependências Python
pip3 install -r requirements.txt

# 2. Compilar o projeto
make install-deps
make all

# 3. Executar análise
make full-analysis
```

## 📋 Comandos Disponíveis

### 🔧 Configuração
```bash
make install-deps      # Instala todas as dependências
make setup-python      # Configura apenas ambiente Python
```

### ⚙️ Compilação
```bash
make all               # Compila ambos os modelos
make completo          # Modelo completo (PDE + Nelder-Mead)
make simples           # Modelo simplificado
```

### 🚀 Execução
```bash
make run-completo      # Compila e executa modelo completo
make run-with-plots    # Execução + plotagem automática
make full-analysis     # Análise completa (simulação + plots + relatório)
./run_analysis.sh      # Script de execução rápida
```

### 📊 Visualização
```bash
make plot              # Gráficos de comparação básicos
make plot-advanced     # Visualizações avançadas (3D, sensibilidade)
make plot-custom       # Plotagem personalizada completa
make report            # Relatório técnico em LaTeX/PDF
```

### 🧹 Limpeza
```bash
make clean             # Remove executáveis
make clean-all         # Remove executáveis e dados CSV
make clean-plots       # Remove apenas gráficos gerados
```

## 🔬 Estrutura do Projeto

```
📁 Exemplo otimização com PDE/
├── 🔧 Código Principal
│   ├── exemplo_adsorcao.cpp          # Implementação principal
│   ├── adsorption_optimization.h     # Headers do modelo
│   └── adsorption_optimization.cpp   # Implementação da otimização
│
├── 🎨 Visualização e Relatórios
│   ├── plot_results.py               # Gráficos de comparação
│   ├── plot_advanced.py              # Visualizações avançadas
│   ├── generate_report.py            # Relatórios técnicos
│   └── requirements.txt              # Dependências Python
│
├── ⚙️ Configuração e Build
│   ├── Makefile                      # Sistema de build
│   ├── setup.sh                      # Script de configuração
│   ├── run_analysis.sh               # Execução rápida
│   └── config.ini                    # Configurações
│
└── 📚 Documentação
    ├── README.md                     # Este arquivo
    └── test.sh                       # Testes
```

## 📈 Exemplo de Uso

```bash
# 1. Configuração inicial (uma vez)
./setup.sh

# 2. Análise completa
./run_analysis.sh

# 3. Ou passo a passo:
make completo                    # Compilar
./exemplo_adsorcao              # Executar simulação
python3 plot_results.py --all-plots    # Gerar gráficos
python3 generate_report.py     # Gerar relatório
```

## 📊 Arquivos de Saída

### Dados de Simulação
- `dados_experimentais.csv` - Dados experimentais sintéticos
- `simulacao_inicial.csv` - Resultados com parâmetros iniciais
- `simulacao_otimizada.csv` - Resultados otimizados
- `comparacao_resultados.csv` - Comparação experimental vs simulado

### Visualizações
- `resultado_comparacao.png` - Comparação temporal e paridade
- `resultado_analise_detalhada.png` - Análise detalhada dos erros
- `avancado_perfil_3d.png` - Perfil 3D de concentração
- `avancado_sensibilidade.png` - Análise de sensibilidade
- `avancado_mecanismos.png` - Comparação de mecanismos
- `avancado_isotermas.png` - Comparação de isotermas

### Relatórios
- `relatorio_tecnico.tex` - Relatório em LaTeX
- `relatorio_tecnico.pdf` - Relatório em PDF (se LaTeX disponível)

## 🔬 Modelo Matemático

O sistema resolve a seguinte PDE para difusão em partículas esféricas:

```
∂C/∂t = D_eff (∂²C/∂r² + 2/r ∂C/∂r) - ρ_p(1-ε) ∂q/∂t
```

Com isoterma de Langmuir:
```
q = (q_max × k_L × C) / (1 + k_L × C)
```

### Parâmetros Otimizados
- `D_eff` - Difusividade efetiva [m²/s]
- `k_L` - Constante de Langmuir [m³/kg]
- `q_max` - Capacidade máxima de adsorção [kg/kg]
- `k_f` - Coeficiente de transferência externa [m/s]

## 📊 Métricas de Avaliação

- **R²** - Coeficiente de determinação
- **RMSE** - Erro quadrático médio
- **MAE** - Erro absoluto médio
- **MAPE** - Erro percentual médio
- **Análise de resíduos** - Distribuição e tendências

## 🛠️ Dependências

### Sistema
- **C++17** - Compilador g++ ou clang++
- **Python 3.8+** - Para visualização e relatórios
- **LaTeX** (opcional) - Para geração de PDFs

### Bibliotecas Python
- **numpy** - Computação numérica
- **pandas** - Manipulação de dados
- **matplotlib** - Gráficos básicos
- **seaborn** - Gráficos estatísticos
- **scipy** (opcional) - Funções científicas

## 🎯 Casos de Uso

1. **Pesquisa Acadêmica**: Otimização de parâmetros para estudos de adsorção
2. **Engenharia de Processos**: Design e otimização de sistemas de separação
3. **Validação de Modelos**: Comparação entre diferentes formulações matemáticas
4. **Ensino**: Demonstração de métodos numéricos e otimização

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📚 Referências

1. **Ruthven, D.M.** - *Principles of Adsorption and Adsorption Processes*. Wiley, 1984.
2. **Tien, C.** - *Adsorption Calculations and Modeling*. Butterworth-Heinemann, 1994.
3. **Nelder, J.A., Mead, R.** - A simplex method for function minimization. *Computer Journal*, 7, 308-313, 1965.

---

**🎉 Desenvolvido com foco na qualidade científica e facilidade de uso!**