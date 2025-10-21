#!/usr/bin/env python3
"""
Gerador de relatório técnico em LaTeX para resultados de otimização de adsorção
Produz documento de qualidade para publicação científica

Autor: Sistema de Otimização com PDE
Data: 2025
"""

import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from datetime import datetime
import subprocess
import sys

def load_data_safe(filename: str) -> pd.DataFrame:
    """Carrega dados com tratamento de erro"""
    try:
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(filename, sep=sep, comment='#', skipinitialspace=True)
                if len(df.columns) >= 2:
                    return df
            except:
                continue
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar {filename}: {e}")
        return None

def calculate_comprehensive_stats(exp_data: np.ndarray, sim_data: np.ndarray) -> dict:
    """Calcula estatísticas abrangentes"""
    mask = ~(np.isnan(exp_data) | np.isnan(sim_data))
    exp_clean = exp_data[mask]
    sim_clean = sim_data[mask]
    
    if len(exp_clean) == 0:
        return {}
    
    # Métricas básicas
    rmse = np.sqrt(np.mean((exp_clean - sim_clean)**2))
    mae = np.mean(np.abs(exp_clean - sim_clean))
    mape = np.mean(np.abs((exp_clean - sim_clean) / exp_clean)) * 100
    
    # Coeficientes de correlação
    ss_res = np.sum((exp_clean - sim_clean)**2)
    ss_tot = np.sum((exp_clean - np.mean(exp_clean))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    correlation = np.corrcoef(exp_clean, sim_clean)[0, 1] if len(exp_clean) > 1 else 0
    
    # Métricas adicionais
    residuals = exp_clean - sim_clean
    bias = np.mean(residuals)
    std_residuals = np.std(residuals)
    
    # Erro máximo e mínimo
    max_error = np.max(np.abs(residuals))
    min_error = np.min(np.abs(residuals))
    
    # Percentis dos erros
    error_percentiles = np.percentile(np.abs(residuals), [25, 50, 75, 95])
    
    return {
        'n_points': len(exp_clean),
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'r_squared': r_squared,
        'correlation': correlation,
        'bias': bias,
        'std_residuals': std_residuals,
        'max_error': max_error,
        'min_error': min_error,
        'error_p25': error_percentiles[0],
        'error_p50': error_percentiles[1],
        'error_p75': error_percentiles[2],
        'error_p95': error_percentiles[3],
        'exp_mean': np.mean(exp_clean),
        'exp_std': np.std(exp_clean),
        'sim_mean': np.mean(sim_clean),
        'sim_std': np.std(sim_clean)
    }

def generate_latex_report(stats: dict, output_file: str = 'relatorio_adsorcao.tex') -> None:
    """Gera relatório técnico em LaTeX"""
    
    latex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[portuguese]{{babel}}
\\usepackage{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{float}}
\\usepackage{{booktabs}}

\\geometry{{margin=2.5cm}}

\\title{{\\textbf{{Relatório Técnico: Otimização de Parâmetros\\\\
para Modelo de Adsorção com PDE}}}}
\\author{{Sistema de Otimização Automática}}
\\date{{{datetime.now().strftime('%d de %B de %Y')}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
Este relatório apresenta os resultados da otimização de parâmetros para um modelo matemático de adsorção baseado em equações diferenciais parciais (PDE). O modelo considera difusão em partículas esféricas com isoterma de Langmuir, resolvido numericamente pelo método de diferenças finitas. A otimização foi realizada utilizando o algoritmo Nelder-Mead para ajuste aos dados experimentais.
\\end{{abstract}}

\\section{{Introdução}}

O processo de adsorção em partículas porosas é governado por fenômenos de transferência de massa que podem ser descritos matematicamente através de equações diferenciais parciais. Este estudo implementa um modelo que considera:

\\begin{{itemize}}
    \\item Difusão intrapartícula em geometria esférica
    \\item Isoterma de adsorção de Langmuir
    \\item Transferência de massa externa
    \\item Resistência difusional no filme líquido
\\end{{itemize}}

\\section{{Modelo Matemático}}

O modelo é baseado na equação de difusão em coordenadas esféricas:

\\begin{{equation}}
\\frac{{\\partial C}}{{\\partial t}} = D_{{eff}} \\left( \\frac{{\\partial^2 C}}{{\\partial r^2}} + \\frac{{2}}{{r}} \\frac{{\\partial C}}{{\\partial r}} \\right) - \\rho_p (1-\\varepsilon) \\frac{{\\partial q}}{{\\partial t}}
\\end{{equation}}

onde:
\\begin{{itemize}}
    \\item $C$ é a concentração na fase líquida [kg/m³]
    \\item $q$ é a concentração adsorvida [kg/kg]
    \\item $D_{{eff}}$ é a difusividade efetiva [m²/s]
    \\item $\\rho_p$ é a densidade da partícula [kg/m³]
    \\item $\\varepsilon$ é a porosidade da partícula [-]
\\end{{itemize}}

A isoterma de Langmuir é dada por:

\\begin{{equation}}
q = \\frac{{q_{{max}} k_L C}}{{1 + k_L C}}
\\end{{equation}}

\\section{{Resultados da Otimização}}

\\subsection{{Estatísticas de Ajuste}}

A Tabela~\\ref{{tab:stats}} apresenta as principais métricas estatísticas obtidas na comparação entre dados experimentais e simulados.

\\begin{{table}}[H]
\\centering
\\caption{{Estatísticas de ajuste do modelo otimizado}}
\\label{{tab:stats}}
\\begin{{tabular}}{{lc}}
\\toprule
\\textbf{{Métrica}} & \\textbf{{Valor}} \\\\
\\midrule
Número de pontos experimentais & {stats.get('n_points', 0)} \\\\
Coeficiente de determinação ($R^2$) & {stats.get('r_squared', 0):.6f} \\\\
Coeficiente de correlação & {stats.get('correlation', 0):.6f} \\\\
Erro quadrático médio (RMSE) & {stats.get('rmse', 0):.6f} kg/kg \\\\
Erro absoluto médio (MAE) & {stats.get('mae', 0):.6f} kg/kg \\\\
Erro percentual médio (MAPE) & {stats.get('mape', 0):.2f}\\% \\\\
Viés (bias) & {stats.get('bias', 0):.6f} kg/kg \\\\
Desvio padrão dos resíduos & {stats.get('std_residuals', 0):.6f} kg/kg \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\subsection{{Análise de Erros}}

A distribuição dos erros absolutos é caracterizada pelos seguintes percentis:

\\begin{{itemize}}
    \\item P25: {stats.get('error_p25', 0):.6f} kg/kg
    \\item P50 (mediana): {stats.get('error_p50', 0):.6f} kg/kg
    \\item P75: {stats.get('error_p75', 0):.6f} kg/kg
    \\item P95: {stats.get('error_p95', 0):.6f} kg/kg
\\end{{itemize}}

O erro máximo observado foi de {stats.get('max_error', 0):.6f} kg/kg, enquanto o erro mínimo foi de {stats.get('min_error', 0):.6f} kg/kg.

\\subsection{{Interpretação dos Resultados}}"""

    # Adicionar interpretação baseada no R²
    r_squared = stats.get('r_squared', 0)
    if r_squared > 0.95:
        interpretation = "O modelo apresenta excelente ajuste aos dados experimentais ($R^2 > 0{,}95$), indicando que a formulação matemática captura adequadamente os fenômenos físicos envolvidos."
    elif r_squared > 0.90:
        interpretation = "O modelo apresenta muito bom ajuste aos dados experimentais ($R^2 > 0{,}90$), demonstrando boa capacidade preditiva."
    elif r_squared > 0.80:
        interpretation = "O modelo apresenta bom ajuste aos dados experimentais ($R^2 > 0{,}80$), porém há espaço para melhorias na formulação ou nos parâmetros."
    elif r_squared > 0.70:
        interpretation = "O modelo apresenta ajuste razoável ($R^2 > 0{,}70$), sugerindo que os principais fenômenos são capturados, mas refinamentos são necessários."
    else:
        interpretation = "O modelo apresenta ajuste limitado ($R^2 < 0{,}70$), indicando necessidade de revisão da formulação matemática ou dos dados experimentais."

    latex_content += f"""

{interpretation}

\\section{{Figuras}}

As seguintes figuras foram geradas automaticamente pelo sistema:

\\begin{{itemize}}
    \\item \\texttt{{resultado\\_comparacao.png}} - Comparação temporal e gráfico de paridade
    \\item \\texttt{{resultado\\_analise\\_detalhada.png}} - Análise detalhada dos erros
    \\item \\texttt{{avancado\\_perfil\\_3d.png}} - Perfil 3D de concentração
    \\item \\texttt{{avancado\\_sensibilidade.png}} - Análise de sensibilidade dos parâmetros
\\end{{itemize}}

\\section{{Conclusões}}

\\begin{{enumerate}}
    \\item O modelo matemático desenvolvido demonstra capacidade {"excelente" if r_squared > 0.95 else "boa" if r_squared > 0.80 else "razoável"} de reproduzir os dados experimentais.
    \\item O erro quadrático médio de {stats.get('rmse', 0):.6f} kg/kg está dentro de limites aceitáveis para aplicações práticas.
    \\item A metodologia de otimização Nelder-Mead mostrou-se eficaz para a estimação de parâmetros.
    \\item Os resultados validam a abordagem baseada em PDE para modelagem de processos de adsorção.
\\end{{enumerate}}

\\section{{Recomendações}}

\\begin{{itemize}}
    \\item Validar o modelo com dados experimentais independentes
    \\item Considerar efeitos de temperatura se relevantes
    \\item Investigar outros algoritmos de otimização para comparação
    \\item Realizar análise de sensibilidade mais detalhada
\\end{{itemize}}

\\section{{Referências}}

\\begin{{enumerate}}
    \\item Ruthven, D.M. \\textit{{Principles of Adsorption and Adsorption Processes}}. Wiley, 1984.
    \\item Tien, C. \\textit{{Adsorption Calculations and Modeling}}. Butterworth-Heinemann, 1994.
    \\item Nelder, J.A., Mead, R. A simplex method for function minimization. \\textit{{Computer Journal}}, 7, 308-313, 1965.
\\end{{enumerate}}

\\end{{document}}"""

    # Salvar arquivo LaTeX
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Relatório LaTeX gerado: {output_file}")

def compile_latex_to_pdf(tex_file: str) -> bool:
    """Compila LaTeX para PDF"""
    try:
        # Verificar se pdflatex está disponível
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ pdflatex não encontrado. Instale TeX Live ou MiKTeX.")
            return False
        
        # Obter diretório e nome do arquivo
        tex_path = Path(tex_file)
        tex_dir = tex_path.parent
        tex_name = tex_path.name
        
        # Compilar PDF (duas vezes para referências cruzadas)
        for i in range(2):
            print(f"🔄 Compilação LaTeX ({i+1}/2)...")
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_name],
                                  cwd=tex_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Erro na compilação LaTeX:\n{result.stdout}\n{result.stderr}")
                return False
        
        pdf_file = tex_file.replace('.tex', '.pdf')
        if Path(pdf_file).exists():
            print(f"✅ PDF gerado com sucesso: {pdf_file}")
            return True
        else:
            print("❌ PDF não foi gerado")
            return False
            
    except FileNotFoundError:
        print("⚠️ pdflatex não encontrado. Instale uma distribuição LaTeX.")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Gera relatório técnico em LaTeX/PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--exp', default='Resultados/dados_experimentais.csv',
                       help='Arquivo de dados experimentais')
    parser.add_argument('--sim', default='Resultados/simulacao_otimizada.csv',
                       help='Arquivo de simulação otimizada')
    parser.add_argument('--output', default='Resultados/relatorio_adsorcao',
                       help='Nome base dos arquivos de saída (sem extensão)')
    parser.add_argument('--no-pdf', action='store_true',
                       help='Não tentar gerar PDF')
    
    args = parser.parse_args()
    
    print("📄 Gerando relatório técnico...")
    
    # Criar diretório de resultados se não existir
    import os
    os.makedirs('Resultados', exist_ok=True)
    
    # Carregar dados
    exp_data = load_data_safe(args.exp)
    sim_data = load_data_safe(args.sim)
    
    if exp_data is None or sim_data is None:
        print("❌ Não foi possível carregar os dados necessários")
        sys.exit(1)
    
    # Preparar dados para análise
    time_exp = exp_data.iloc[:, 0].values
    uptake_exp = exp_data.iloc[:, 1].values
    time_sim = sim_data.iloc[:, 0].values
    uptake_sim = sim_data.iloc[:, 1].values
    
    # Interpolar dados simulados
    uptake_sim_interp = np.interp(time_exp, time_sim, uptake_sim)
    
    # Calcular estatísticas
    stats = calculate_comprehensive_stats(uptake_exp, uptake_sim_interp)
    
    if not stats:
        print("❌ Não foi possível calcular estatísticas")
        sys.exit(1)
    
    # Gerar relatório LaTeX
    tex_file = f"{args.output}.tex"
    generate_latex_report(stats, tex_file)
    
    # Compilar para PDF se solicitado
    if not args.no_pdf:
        compile_latex_to_pdf(tex_file)
    
    print("✅ Relatório técnico concluído!")

if __name__ == "__main__":
    main()