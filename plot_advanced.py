#!/usr/bin/env python3
"""
Script auxiliar para gerar gráficos 3D e visualizações avançadas
dos perfis de concentração radial e temporal

Autor: Sistema de Otimização com PDE
Data: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from pathlib import Path
import argparse
import matplotlib.animation as animation
from matplotlib import cm
import seaborn as sns

# Configuração para plots 3D
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'figure.figsize': (12, 9),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def load_simulation_data(filename: str) -> pd.DataFrame:
    """Carrega dados de simulação completos"""
    try:
        df = pd.read_csv(filename, comment='#')
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar {filename}: {e}")
        return None

def plot_3d_concentration_profile(sim_data: pd.DataFrame, 
                                output_file: str = 'perfil_3d_concentracao.png') -> None:
    """
    Gera plot 3D da evolução do perfil de concentração
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Assumindo que temos dados de tempo e uptake total
    time = sim_data.iloc[:, 0].values / 60  # Converter para minutos
    uptake = sim_data.iloc[:, 1].values
    
    # Criar dados sintéticos de perfil radial (baseado no modelo)
    n_points = len(time)
    r_points = 20
    r = np.linspace(0, 1, r_points)  # Raio normalizado
    
    # Matriz para armazenar concentração
    C_matrix = np.zeros((n_points, r_points))
    
    # Modelo simplificado de difusão esférica para visualização
    D_eff = 1e-10  # Difusividade efetiva estimada
    R = 0.001      # Raio da partícula
    
    for i, t in enumerate(time * 60):  # Voltar para segundos
        for j, r_norm in enumerate(r):
            if r_norm == 0:
                # Centro da partícula
                C_matrix[i, j] = uptake[i] * 1.2  # Concentração central maior
            else:
                # Solução aproximada para difusão esférica
                # C(r,t) ≈ C_eq * (1 - exp(-D_eff*t/(r*R)²))
                tau = D_eff * t / (r_norm * R)**2
                C_matrix[i, j] = uptake[i] * (1 - np.exp(-tau)) if tau > 0 else 0
    
    # Criar meshgrid
    T, R_mesh = np.meshgrid(time, r, indexing='ij')
    
    # Plot de superfície
    surf = ax.plot_surface(T, R_mesh, C_matrix, cmap=cm.viridis, 
                          alpha=0.8, linewidth=0, antialiased=True)
    
    # Adicionar contornos na base
    contours = ax.contour(T, R_mesh, C_matrix, zdir='z', 
                         offset=np.min(C_matrix), cmap=cm.viridis, alpha=0.5)
    
    ax.set_xlabel('Tempo (min)', labelpad=10)
    ax.set_ylabel('Posição radial normalizada', labelpad=10)
    ax.set_zlabel('Concentração (kg/kg)', labelpad=10)
    ax.set_title('Evolução 3D do Perfil de Concentração\nDifusão em Partícula Esférica', 
                 fontweight='bold', pad=20)
    
    # Colorbar
    fig.colorbar(surf, shrink=0.5, aspect=30, label='Concentração (kg/kg)')
    
    # Ajustar visualização
    ax.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Plot 3D salvo: {output_file}")

def plot_parameter_sensitivity(output_file: str = 'sensibilidade_parametros.png') -> None:
    """
    Gera gráfico de sensibilidade dos parâmetros
    """
    # Parâmetros base
    params_base = {
        'D_eff': 1e-10,
        'k_L': 100.0,
        'q_max': 0.5,
        'k_f': 1e-5
    }
    
    # Variações percentuais
    variations = [-50, -25, -10, 0, 10, 25, 50]
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    colors = plt.cm.RdYlBu_r(np.linspace(0, 1, len(variations)))
    
    for idx, (param_name, base_value) in enumerate(params_base.items()):
        ax = axes[idx]
        
        for i, var in enumerate(variations):
            # Simulação simplificada para diferentes valores do parâmetro
            time = np.linspace(0, 60, 100)  # 60 minutos
            
            # Modelo simplificado de captação
            if param_name == 'D_eff':
                # Difusividade afeta a taxa inicial
                D_var = base_value * (1 + var/100)
                uptake = 0.5 * (1 - np.exp(-D_var * 1e8 * time))
            elif param_name == 'k_L':
                # Constante de Langmuir afeta a forma da curva
                k_var = base_value * (1 + var/100)
                uptake = 0.5 * k_var * time / (1 + k_var * time)
            elif param_name == 'q_max':
                # Capacidade máxima afeta o platô
                q_var = base_value * (1 + var/100)
                uptake = q_var * (1 - np.exp(-0.05 * time))
            else:  # k_f
                # Coeficiente de transferência externa afeta taxa inicial
                k_var = base_value * (1 + var/100)
                uptake = 0.5 * (1 - np.exp(-k_var * 1e4 * time))
            
            label = f'{var:+d}%' if var != 0 else 'Base'
            linestyle = '-' if var == 0 else '--'
            linewidth = 3 if var == 0 else 1.5
            
            ax.plot(time, uptake, color=colors[i], linestyle=linestyle, 
                   linewidth=linewidth, label=label, alpha=0.8)
        
        ax.set_xlabel('Tempo (min)')
        ax.set_ylabel('Captação (kg/kg)')
        ax.set_title(f'Sensibilidade: {param_name}', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    plt.suptitle('Análise de Sensibilidade dos Parâmetros', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Análise de sensibilidade salva: {output_file}")

def plot_adsorption_mechanisms(output_file: str = 'mecanismos_adsorcao.png') -> None:
    """
    Ilustra diferentes mecanismos de adsorção
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    time = np.linspace(0, 60, 200)
    
    # 1. Difusão intrapartícula dominante
    uptake_diffusion = 0.5 * (1 - np.exp(-0.05 * time))
    ax1.plot(time, uptake_diffusion, 'b-', linewidth=3, 
             label='Difusão intrapartícula')
    ax1.set_title('Difusão Intrapartícula Dominante', fontweight='bold')
    ax1.set_ylabel('Captação (kg/kg)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Transferência de massa externa dominante
    uptake_external = 0.5 * (1 - np.exp(-0.2 * time))
    ax2.plot(time, uptake_external, 'r-', linewidth=3, 
             label='Transferência externa')
    ax2.set_title('Transferência Externa Dominante', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Combinação de mecanismos
    uptake_combined = 0.5 * (1 - 0.5*np.exp(-0.2*time) - 0.5*np.exp(-0.05*time))
    ax3.plot(time, uptake_combined, 'g-', linewidth=3, 
             label='Mecanismos combinados')
    ax3.set_xlabel('Tempo (min)')
    ax3.set_ylabel('Captação (kg/kg)')
    ax3.set_title('Mecanismos Combinados', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Comparação de todos
    ax4.plot(time, uptake_diffusion, 'b-', linewidth=2.5, 
             label='Difusão intrapartícula', alpha=0.8)
    ax4.plot(time, uptake_external, 'r-', linewidth=2.5, 
             label='Transferência externa', alpha=0.8)
    ax4.plot(time, uptake_combined, 'g-', linewidth=2.5, 
             label='Combinado', alpha=0.8)
    
    ax4.set_xlabel('Tempo (min)')
    ax4.set_title('Comparação dos Mecanismos', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.suptitle('Mecanismos de Adsorção: Análise Comparativa', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Análise de mecanismos salva: {output_file}")

def plot_isotherms_comparison(output_file: str = 'isotermas_comparacao.png') -> None:
    """
    Compara diferentes isotermas de adsorção
    """
    C = np.linspace(0.01, 2.0, 100)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Parâmetros para diferentes isotermas
    q_max = 0.5
    k_L = 100.0
    k_F = 0.3
    n = 2.0
    
    # 1. Isotermas lineares vs não-lineares
    q_langmuir = q_max * k_L * C / (1 + k_L * C)
    q_freundlich = k_F * C**(1/n)
    q_linear = 0.2 * C
    
    ax1.plot(C, q_langmuir, 'b-', linewidth=3, label='Langmuir', alpha=0.8)
    ax1.plot(C, q_freundlich, 'r-', linewidth=3, label='Freundlich', alpha=0.8)
    ax1.plot(C, q_linear, 'g--', linewidth=3, label='Linear', alpha=0.8)
    
    ax1.set_xlabel('Concentração (kg/m³)')
    ax1.set_ylabel('Captação de equilíbrio (kg/kg)')
    ax1.set_title('Comparação de Isotermas', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Efeito dos parâmetros na isoterma de Langmuir
    k_L_values = [50, 100, 200]
    q_max_values = [0.3, 0.5, 0.7]
    
    colors_k = plt.cm.Blues(np.linspace(0.4, 1, len(k_L_values)))
    colors_q = plt.cm.Reds(np.linspace(0.4, 1, len(q_max_values)))
    
    # Variação de k_L
    for i, k in enumerate(k_L_values):
        q = 0.5 * k * C / (1 + k * C)
        ax2.plot(C, q, color=colors_k[i], linewidth=2.5, 
                label=f'k_L = {k}', linestyle='-')
    
    # Variação de q_max
    for i, q_m in enumerate(q_max_values):
        q = q_m * 100 * C / (1 + 100 * C)
        ax2.plot(C, q, color=colors_q[i], linewidth=2.5, 
                label=f'q_max = {q_m}', linestyle='--')
    
    ax2.set_xlabel('Concentração (kg/m³)')
    ax2.set_ylabel('Captação de equilíbrio (kg/kg)')
    ax2.set_title('Efeito dos Parâmetros (Langmuir)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comparação de isotermas salva: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Gera visualizações avançadas para análise de adsorção',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--sim-data', default='Resultados/simulacao_otimizada.csv',
                       help='Arquivo de dados de simulação')
    parser.add_argument('--output', default='Resultados/avancado',
                       help='Prefixo dos arquivos de saída')
    parser.add_argument('--all', action='store_true',
                       help='Gerar todos os gráficos avançados')
    parser.add_argument('--3d', action='store_true',
                       help='Gerar gráfico 3D')
    parser.add_argument('--sensitivity', action='store_true',
                       help='Análise de sensibilidade')
    parser.add_argument('--mechanisms', action='store_true',
                       help='Comparação de mecanismos')
    parser.add_argument('--isotherms', action='store_true',
                       help='Comparação de isotermas')
    
    args = parser.parse_args()
    
    print("🎨 Gerando visualizações avançadas...")
    
    # Criar diretório de resultados se não existir
    import os
    os.makedirs('Resultados', exist_ok=True)
    
    # Carregar dados se necessário
    sim_data = None
    if args.all or args._3d:
        sim_data = load_simulation_data(args.sim_data)
    
    # Gerar gráficos solicitados
    if args.all or args._3d:
        if sim_data is not None:
            plot_3d_concentration_profile(sim_data, f"{args.output}_perfil_3d.png")
        else:
            print("⚠️ Dados de simulação não encontrados para gráfico 3D")
    
    if args.all or args.sensitivity:
        plot_parameter_sensitivity(f"{args.output}_sensibilidade.png")
    
    if args.all or args.mechanisms:
        plot_adsorption_mechanisms(f"{args.output}_mecanismos.png")
    
    if args.all or args.isotherms:
        plot_isotherms_comparison(f"{args.output}_isotermas.png")
    
    print(f"✅ Visualizações avançadas concluídas!")

if __name__ == "__main__":
    main()