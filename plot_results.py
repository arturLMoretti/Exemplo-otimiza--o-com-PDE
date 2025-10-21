#!/usr/bin/env python3
"""
Script de plotagem de alta qualidade para resultados de otimização de adsorção
Compara dados experimentais vs simulados com formatação para publicação

Autor: Sistema de Otimização com PDE
Data: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import argparse
import sys
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Configuração global para plots de qualidade de publicação
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'axes.linewidth': 1.2,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.figsize': (10, 8),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'lines.linewidth': 2,
    'lines.markersize': 8,
    'grid.alpha': 0.3,
    'text.usetex': False  # Mude para True se tiver LaTeX instalado
})

def load_data(filename: str) -> pd.DataFrame:
    """
    Carrega dados de arquivo CSV, lidando com diferentes formatos
    """
    try:
        # Tentar diferentes delimitadores
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(filename, sep=sep, comment='#', skipinitialspace=True)
                if len(df.columns) >= 2:
                    return df
            except:
                continue
        
        # Se nenhum delimitador funcionou, tentar espaços
        df = pd.read_csv(filename, delim_whitespace=True, comment='#')
        return df
    
    except Exception as e:
        print(f"❌ Erro ao carregar {filename}: {e}")
        return None

def calculate_statistics(exp_data: np.ndarray, sim_data: np.ndarray) -> dict:
    """
    Calcula estatísticas de ajuste entre dados experimentais e simulados
    """
    # Remover valores NaN
    mask = ~(np.isnan(exp_data) | np.isnan(sim_data))
    exp_clean = exp_data[mask]
    sim_clean = sim_data[mask]
    
    if len(exp_clean) == 0:
        return {}
    
    # Métricas de erro
    rmse = np.sqrt(np.mean((exp_clean - sim_clean)**2))
    mae = np.mean(np.abs(exp_clean - sim_clean))
    mape = np.mean(np.abs((exp_clean - sim_clean) / exp_clean)) * 100
    
    # Coeficiente de determinação (R²)
    ss_res = np.sum((exp_clean - sim_clean)**2)
    ss_tot = np.sum((exp_clean - np.mean(exp_clean))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Coeficiente de correlação de Pearson
    correlation = np.corrcoef(exp_clean, sim_clean)[0, 1] if len(exp_clean) > 1 else 0
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape,
        'R²': r_squared,
        'Correlação': correlation,
        'N_pontos': len(exp_clean)
    }

def plot_comparison(exp_data: pd.DataFrame, sim_data: pd.DataFrame, 
                   output_file: str = 'comparacao_adsorcao.png') -> None:
    """
    Cria plot de comparação entre dados experimentais e simulados
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Preparar dados para interpolação
    time_exp = exp_data.iloc[:, 0].values
    uptake_exp = exp_data.iloc[:, 1].values
    time_sim = sim_data.iloc[:, 0].values
    uptake_sim = sim_data.iloc[:, 1].values
    
    # Interpolar dados simulados nos tempos experimentais
    uptake_sim_interp = np.interp(time_exp, time_sim, uptake_sim)
    
    # 1. Comparação temporal
    ax1.plot(time_sim/60, uptake_sim, 'b-', linewidth=2.5, 
             label='Modelo Simulado', alpha=0.8)
    ax1.scatter(time_exp/60, uptake_exp, c='red', s=60, marker='o', 
                label='Dados Experimentais', zorder=5, edgecolors='black', linewidth=1)
    
    ax1.set_xlabel('Tempo (min)')
    ax1.set_ylabel('Captação total (kg/kg)')
    ax1.set_title('Comparação Temporal: Experimental vs Simulado', fontweight='bold', pad=20)
    ax1.legend(frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3)
    
    # Adicionar estatísticas no gráfico
    stats = calculate_statistics(uptake_exp, uptake_sim_interp)
    textstr = f"R² = {stats.get('R²', 0):.4f}\nRMSE = {stats.get('RMSE', 0):.4f}\nN = {stats.get('N_pontos', 0)}"
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=11,
             verticalalignment='top', bbox=props)
    
    # 2. Gráfico de paridade (1:1)
    max_val = max(np.max(uptake_exp), np.max(uptake_sim_interp))
    min_val = min(np.min(uptake_exp), np.min(uptake_sim_interp))
    
    ax2.scatter(uptake_exp, uptake_sim_interp, c='blue', s=80, alpha=0.7, 
                edgecolors='black', linewidth=1)
    ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
             label='Linha de Paridade (1:1)')
    
    # Bandas de confiança
    error_band = 0.1 * max_val
    ax2.fill_between([min_val, max_val], 
                     [min_val - error_band, max_val - error_band],
                     [min_val + error_band, max_val + error_band],
                     alpha=0.2, color='red', label='±10% de erro')
    
    ax2.set_xlabel('Uptake Experimental (kg/kg)')
    ax2.set_ylabel('Uptake Simulado (kg/kg)')
    ax2.set_title('Gráfico de Paridade', fontweight='bold', pad=20)
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal', adjustable='box')
    
    # 3. Resíduos
    residuals = uptake_exp - uptake_sim_interp
    ax3.scatter(uptake_sim_interp, residuals, c='green', s=60, alpha=0.7,
                edgecolors='black', linewidth=1)
    ax3.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax3.axhline(y=np.std(residuals), color='orange', linestyle=':', 
                linewidth=1.5, label=f'±1σ = ±{np.std(residuals):.4f}')
    ax3.axhline(y=-np.std(residuals), color='orange', linestyle=':', linewidth=1.5)
    
    ax3.set_xlabel('Uptake Simulado (kg/kg)')
    ax3.set_ylabel('Resíduos (Exp - Sim)')
    ax3.set_title('Análise de Resíduos', fontweight='bold', pad=20)
    ax3.legend(frameon=True, fancybox=True, shadow=True)
    ax3.grid(True, alpha=0.3)
    
    # 4. Distribuição dos resíduos
    ax4.hist(residuals, bins=10, alpha=0.7, color='skyblue', 
             edgecolor='black', linewidth=1)
    ax4.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Média = 0')
    ax4.axvline(x=np.mean(residuals), color='orange', linestyle='-', 
                linewidth=2, label=f'Média real = {np.mean(residuals):.4f}')
    
    ax4.set_xlabel('Resíduos (kg/kg)')
    ax4.set_ylabel('Frequência')
    ax4.set_title('Distribuição dos Resíduos', fontweight='bold', pad=20)
    ax4.legend(frameon=True, fancybox=True, shadow=True)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=3.0)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de comparação salvo: {output_file}")

def plot_detailed_analysis(comp_data: pd.DataFrame, 
                          output_file: str = 'analise_detalhada.png') -> None:
    """
    Cria análise detalhada da comparação experimental vs simulado
    """
    if comp_data is None or len(comp_data.columns) < 3:
        print("❌ Dados de comparação insuficientes para análise detalhada")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    time = comp_data.iloc[:, 0].values / 60  # Converter para minutos
    exp_uptake = comp_data.iloc[:, 1].values
    sim_uptake = comp_data.iloc[:, 2].values
    
    if len(comp_data.columns) >= 4:
        abs_error = comp_data.iloc[:, 3].values
    else:
        abs_error = np.abs(exp_uptake - sim_uptake)
    
    # 1. Séries temporais com banda de erro
    ax1.plot(time, sim_uptake, 'b-', linewidth=3, label='Simulado', alpha=0.8)
    ax1.scatter(time, exp_uptake, c='red', s=80, marker='o', 
                label='Experimental', zorder=5, edgecolors='black', linewidth=1)
    
    # Banda de erro
    ax1.fill_between(time, sim_uptake - abs_error, sim_uptake + abs_error,
                     alpha=0.2, color='blue', label='Banda de erro')
    
    ax1.set_xlabel('Tempo (min)')
    ax1.set_ylabel('Captação (kg/kg)')
    ax1.set_title('Evolução Temporal com Bandas de Erro', fontweight='bold', pad=20)
    ax1.legend(frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3)
    
    # 2. Erro absoluto vs tempo
    ax2.plot(time, abs_error, 'go-', linewidth=2, markersize=6, 
             label='Erro absoluto', alpha=0.8)
    ax2.axhline(y=np.mean(abs_error), color='red', linestyle='--', 
                linewidth=2, label=f'Erro médio = {np.mean(abs_error):.4f}')
    
    ax2.set_xlabel('Tempo (min)')
    ax2.set_ylabel('Erro absoluto (kg/kg)')
    ax2.set_title('Evolução do Erro Absoluto', fontweight='bold', pad=20)
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3)
    
    # 3. Erro relativo vs tempo
    rel_error = np.abs((exp_uptake - sim_uptake) / exp_uptake) * 100
    ax3.plot(time, rel_error, 'mo-', linewidth=2, markersize=6, 
             label='Erro relativo', alpha=0.8)
    ax3.axhline(y=np.mean(rel_error), color='red', linestyle='--', 
                linewidth=2, label=f'Erro médio = {np.mean(rel_error):.2f}%')
    
    ax3.set_xlabel('Tempo (min)')
    ax3.set_ylabel('Erro relativo (%)')
    ax3.set_title('Evolução do Erro Relativo', fontweight='bold', pad=20)
    ax3.legend(frameon=True, fancybox=True, shadow=True)
    ax3.grid(True, alpha=0.3)
    
    # 4. Boxplot dos erros
    error_data = [abs_error, rel_error / 100 * np.max(exp_uptake)]
    ax4.boxplot(error_data, labels=['Erro Absoluto', 'Erro Relativo\n(escalonado)'],
                patch_artist=True, boxprops=dict(facecolor='lightblue', alpha=0.7))
    
    ax4.set_ylabel('Magnitude do erro')
    ax4.set_title('Distribuição dos Erros', fontweight='bold', pad=20)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=3.0)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Análise detalhada salva: {output_file}")

def generate_report(exp_data: pd.DataFrame, sim_data: pd.DataFrame,
                   comp_data: Optional[pd.DataFrame] = None) -> None:
    """
    Gera relatório estatístico detalhado
    """
    print("\n" + "="*60)
    print("📊 RELATÓRIO ESTATÍSTICO DA COMPARAÇÃO")
    print("="*60)
    
    # Preparar dados
    time_exp = exp_data.iloc[:, 0].values
    uptake_exp = exp_data.iloc[:, 1].values
    time_sim = sim_data.iloc[:, 0].values
    uptake_sim = sim_data.iloc[:, 1].values
    
    # Interpolar
    uptake_sim_interp = np.interp(time_exp, time_sim, uptake_sim)
    
    # Calcular estatísticas
    stats = calculate_statistics(uptake_exp, uptake_sim_interp)
    
    print(f"📈 Número de pontos experimentais: {stats.get('N_pontos', 0)}")
    print(f"📊 Coeficiente de determinação (R²): {stats.get('R²', 0):.6f}")
    print(f"📏 Coeficiente de correlação: {stats.get('Correlação', 0):.6f}")
    print(f"🎯 Erro quadrático médio (RMSE): {stats.get('RMSE', 0):.6f} kg/kg")
    print(f"📐 Erro absoluto médio (MAE): {stats.get('MAE', 0):.6f} kg/kg")
    print(f"📊 Erro percentual médio (MAPE): {stats.get('MAPE', 0):.2f}%")
    
    # Análise adicional
    residuals = uptake_exp - uptake_sim_interp
    print(f"\n🔍 ANÁLISE DE RESÍDUOS:")
    print(f"   Média dos resíduos: {np.mean(residuals):.6f} kg/kg")
    print(f"   Desvio padrão: {np.std(residuals):.6f} kg/kg")
    print(f"   Valor mínimo: {np.min(residuals):.6f} kg/kg")
    print(f"   Valor máximo: {np.max(residuals):.6f} kg/kg")
    
    # Interpretação da qualidade do ajuste
    r_squared = stats.get('R²', 0)
    print(f"\n🎯 INTERPRETAÇÃO DO AJUSTE:")
    if r_squared > 0.95:
        print("   ✅ Excelente ajuste (R² > 0.95)")
    elif r_squared > 0.90:
        print("   ✅ Muito bom ajuste (R² > 0.90)")
    elif r_squared > 0.80:
        print("   ⚠️  Bom ajuste (R² > 0.80)")
    elif r_squared > 0.70:
        print("   ⚠️  Ajuste razoável (R² > 0.70)")
    else:
        print("   ❌ Ajuste pobre (R² < 0.70)")
    
    print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description='Plotagem de alta qualidade para resultados de adsorção',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python plot_results.py                           # Usar arquivos padrão
  python plot_results.py --exp dados_exp.csv      # Especificar arquivo experimental
  python plot_results.py --all-plots              # Gerar todos os tipos de gráficos
  python plot_results.py --output meus_plots      # Prefixo personalizado
        """
    )
    
    parser.add_argument('--exp', default='Resultados/dados_experimentais.csv',
                       help='Arquivo de dados experimentais (padrão: Resultados/dados_experimentais.csv)')
    parser.add_argument('--sim', default='Resultados/simulacao_otimizada.csv',
                       help='Arquivo de simulação (padrão: Resultados/simulacao_otimizada.csv)')
    parser.add_argument('--comp', default='Resultados/comparacao_resultados.csv',
                       help='Arquivo de comparação (padrão: Resultados/comparacao_resultados.csv)')
    parser.add_argument('--output', default='Resultados/resultado',
                       help='Prefixo dos arquivos de saída (padrão: Resultados/resultado)')
    parser.add_argument('--all-plots', action='store_true',
                       help='Gerar todos os tipos de gráficos')
    parser.add_argument('--no-report', action='store_true',
                       help='Não gerar relatório estatístico')
    
    args = parser.parse_args()
    
    print("🎨 Iniciando plotagem de alta qualidade...")
    print(f"📂 Arquivos de entrada:")
    print(f"   Experimental: {args.exp}")
    print(f"   Simulação: {args.sim}")
    print(f"   Comparação: {args.comp}")
    
    # Criar diretório de resultados se não existir
    import os
    os.makedirs('Resultados', exist_ok=True)
    
    # Carregar dados
    exp_data = load_data(args.exp)
    sim_data = load_data(args.sim)
    comp_data = load_data(args.comp) if Path(args.comp).exists() else None
    
    if exp_data is None or sim_data is None:
        print("❌ Erro: Não foi possível carregar os dados necessários")
        sys.exit(1)
    
    # Gerar plots
    plot_comparison(exp_data, sim_data, f"{args.output}_comparacao.png")
    
    if args.all_plots and comp_data is not None:
        plot_detailed_analysis(comp_data, f"{args.output}_analise_detalhada.png")
    
    # Gerar relatório
    if not args.no_report:
        generate_report(exp_data, sim_data, comp_data)
    
    print(f"\n✅ Plotagem concluída! Arquivos salvos com prefixo '{args.output}'")

if __name__ == "__main__":
    main()