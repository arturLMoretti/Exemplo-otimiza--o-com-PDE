#include "adsorption_optimization.h"
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <iomanip>

// Função para gerar dados experimentais sintéticos
ExperimentalData generate_synthetic_data() {
    ExperimentalData data;
    
    // Parâmetros "verdadeiros" para gerar dados sintéticos
    AdsorptionParams true_params = {
        0.001,      // R = 1 mm
        1e-10,      // D_eff = 1e-10 m²/s
        100.0,      // k_L = 100 m³/kg
        0.5,        // q_max = 0.5 kg/kg
        1.0,        // C_0 = 1.0 kg/m³
        1500.0,     // rho_p = 1500 kg/m³
        0.4,        // epsilon = 0.4
        1e-5,       // k_f = 1e-5 m/s
        50,         // Nr = 50 pontos
        3600.0,     // t_final = 1 hora
        10.0        // dt = 10 s
    };
    
    AdsorptionOptimizer optimizer(true_params);
    auto result = optimizer.simulate();
    
    // Extrair pontos experimentais com ruído
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> noise(0.0, 0.02); // 2% de ruído
    
    for (size_t i = 0; i < result.time.size(); i += 10) { // Cada 10º ponto
        data.time.push_back(result.time[i]);
        double noisy_uptake = result.uptake_total[i] * (1.0 + noise(gen));
        data.uptake.push_back(std::max(0.0, noisy_uptake)); // Garantir não-negatividade
    }
    
    std::cout << "Dados experimentais sintéticos gerados (" << data.time.size() << " pontos)" << std::endl;
    return data;
}

// Função para salvar dados experimentais
void save_experimental_data(const ExperimentalData& data, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo: " << filename << std::endl;
        return;
    }
    
    file << "# Dados Experimentais de Adsorção" << std::endl;
    file << "# Tempo(s), Uptake(kg/kg)" << std::endl;
    file << std::scientific << std::setprecision(6);
    
    for (size_t i = 0; i < data.time.size(); i++) {
        file << data.time[i] << ", " << data.uptake[i] << std::endl;
    }
    
    file.close();
    std::cout << "Dados experimentais salvos em: " << filename << std::endl;
}

// Algoritmo de otimização Nelder-Mead simplificado
std::vector<double> nelder_mead_optimization(AdsorptionOptimizer& optimizer,
                                           const ExperimentalData& exp_data,
                                           const std::vector<double>& initial_guess,
                                           const std::vector<double>& lower_bounds,
                                           const std::vector<double>& upper_bounds) {
    
    int n_params = initial_guess.size();
    double tolerance = 1e-6;
    int max_iterations = 100;
    
    // Criar simplex inicial
    std::vector<std::vector<double>> simplex(n_params + 1);
    std::vector<double> f_values(n_params + 1);
    
    simplex[0] = initial_guess;
    f_values[0] = optimizer.objective_function(initial_guess, exp_data);
    
    // Vértices do simplex
    for (int i = 1; i <= n_params; i++) {
        simplex[i] = initial_guess;
        simplex[i][i-1] *= 1.1; // Perturbação de 10%
        
        // Verificar limites
        for (int j = 0; j < n_params; j++) {
            simplex[i][j] = std::max(lower_bounds[j], 
                           std::min(upper_bounds[j], simplex[i][j]));
        }
        
        f_values[i] = optimizer.objective_function(simplex[i], exp_data);
    }
    
    std::cout << "Iniciando otimização Nelder-Mead..." << std::endl;
    std::cout << "Função objetivo inicial: " << f_values[0] << std::endl;
    
    for (int iter = 0; iter < max_iterations; iter++) {
        // Ordenar simplex
        std::vector<int> indices(n_params + 1);
        std::iota(indices.begin(), indices.end(), 0);
        std::sort(indices.begin(), indices.end(), 
                 [&](int a, int b) { return f_values[a] < f_values[b]; });
        
        // Verificar convergência
        double range = f_values[indices.back()] - f_values[indices[0]];
        if (range < tolerance) {
            std::cout << "Convergência atingida na iteração " << iter << std::endl;
            break;
        }
        
        // Centroide (excluindo o pior ponto)
        std::vector<double> centroid(n_params, 0.0);
        for (int i = 0; i < n_params; i++) {
            for (int j = 0; j < n_params; j++) {
                centroid[j] += simplex[indices[i]][j];
            }
        }
        for (int j = 0; j < n_params; j++) {
            centroid[j] /= n_params;
        }
        
        // Reflexão
        std::vector<double> reflected(n_params);
        int worst_idx = indices.back();
        for (int j = 0; j < n_params; j++) {
            reflected[j] = centroid[j] + (centroid[j] - simplex[worst_idx][j]);
            reflected[j] = std::max(lower_bounds[j], 
                          std::min(upper_bounds[j], reflected[j]));
        }
        
        double f_reflected = optimizer.objective_function(reflected, exp_data);
        
        if (f_reflected < f_values[indices[0]]) {
            // Expansão
            std::vector<double> expanded(n_params);
            for (int j = 0; j < n_params; j++) {
                expanded[j] = centroid[j] + 2.0 * (reflected[j] - centroid[j]);
                expanded[j] = std::max(lower_bounds[j], 
                             std::min(upper_bounds[j], expanded[j]));
            }
            
            double f_expanded = optimizer.objective_function(expanded, exp_data);
            if (f_expanded < f_reflected) {
                simplex[worst_idx] = expanded;
                f_values[worst_idx] = f_expanded;
            } else {
                simplex[worst_idx] = reflected;
                f_values[worst_idx] = f_reflected;
            }
        } else if (f_reflected < f_values[indices[n_params-1]]) {
            simplex[worst_idx] = reflected;
            f_values[worst_idx] = f_reflected;
        } else {
            // Contração
            std::vector<double> contracted(n_params);
            for (int j = 0; j < n_params; j++) {
                contracted[j] = centroid[j] + 0.5 * (simplex[worst_idx][j] - centroid[j]);
            }
            
            double f_contracted = optimizer.objective_function(contracted, exp_data);
            if (f_contracted < f_values[worst_idx]) {
                simplex[worst_idx] = contracted;
                f_values[worst_idx] = f_contracted;
            } else {
                // Redução
                for (int i = 1; i <= n_params; i++) {
                    for (int j = 0; j < n_params; j++) {
                        simplex[i][j] = simplex[indices[0]][j] + 
                                       0.5 * (simplex[i][j] - simplex[indices[0]][j]);
                    }
                    f_values[i] = optimizer.objective_function(simplex[i], exp_data);
                }
            }
        }
        
        // Progresso
        if (iter % 10 == 0) {
            double best_f = *std::min_element(f_values.begin(), f_values.end());
            std::cout << "Iteração " << iter << ", melhor função objetivo: " << best_f << std::endl;
        }
    }
    
    // Retornar melhor solução
    int best_idx = std::min_element(f_values.begin(), f_values.end()) - f_values.begin();
    std::cout << "Otimização concluída. Função objetivo final: " << f_values[best_idx] << std::endl;
    
    return simplex[best_idx];
}

int main() {
    std::cout << "=== OTIMIZAÇÃO DE PARÂMETROS DE ADSORÇÃO ===" << std::endl;
    std::cout << "PDE: Difusão em partícula esférica com isoterma de Langmuir" << std::endl << std::endl;
    
    // 1. Gerar dados experimentais sintéticos
    auto exp_data = generate_synthetic_data();
    save_experimental_data(exp_data, "dados_experimentais.csv");
    
    // 2. Configurar parâmetros iniciais para otimização
    AdsorptionParams initial_params = {
        0.001,      // R = 1 mm (fixo)
        5e-11,      // D_eff inicial (para otimizar)
        50.0,       // k_L inicial (para otimizar)
        0.3,        // q_max inicial (para otimizar)
        1.0,        // C_0 = 1.0 kg/m³ (fixo)
        1500.0,     // rho_p = 1500 kg/m³ (fixo)
        0.4,        // epsilon = 0.4 (fixo)
        5e-6,       // k_f inicial (para otimizar)
        50,         // Nr = 50 pontos
        3600.0,     // t_final = 1 hora
        10.0        // dt = 10 s
    };
    
    AdsorptionOptimizer optimizer(initial_params);
    
    // 3. Executar simulação com parâmetros iniciais
    std::cout << "\n=== SIMULAÇÃO COM PARÂMETROS INICIAIS ===" << std::endl;
    auto initial_result = optimizer.simulate();
    optimizer.save_results(initial_result, "simulacao_inicial.csv");
    
    // 4. Configurar otimização
    std::vector<double> initial_guess = {5e-11, 50.0, 0.3, 5e-6}; // D_eff, k_L, q_max, k_f
    std::vector<double> lower_bounds = {1e-12, 1.0, 0.1, 1e-7};
    std::vector<double> upper_bounds = {1e-9, 500.0, 1.0, 1e-4};
    
    // 5. Executar otimização
    std::cout << "\n=== OTIMIZAÇÃO ===" << std::endl;
    auto optimal_params = nelder_mead_optimization(optimizer, exp_data, 
                                                  initial_guess, lower_bounds, upper_bounds);
    
    // 6. Simulação com parâmetros otimizados
    std::cout << "\n=== SIMULAÇÃO COM PARÂMETROS OTIMIZADOS ===" << std::endl;
    optimizer.update_parameters(optimal_params);
    auto optimized_result = optimizer.simulate();
    optimizer.save_results(optimized_result, "simulacao_otimizada.csv");
    
    // 7. Mostrar resultados
    std::cout << "\n=== RESULTADOS DA OTIMIZAÇÃO ===" << std::endl;
    std::cout << "Parâmetros otimizados:" << std::endl;
    std::cout << "  D_eff = " << std::scientific << optimal_params[0] << " m²/s" << std::endl;
    std::cout << "  k_L   = " << std::scientific << optimal_params[1] << " m³/kg" << std::endl;
    std::cout << "  q_max = " << std::scientific << optimal_params[2] << " kg/kg" << std::endl;
    std::cout << "  k_f   = " << std::scientific << optimal_params[3] << " m/s" << std::endl;
    
    double final_error = optimizer.objective_function(optimal_params, exp_data);
    std::cout << "Erro final (RMSE): " << final_error << std::endl;
    
    // 8. Salvar comparação
    std::ofstream comparison("comparacao_resultados.csv");
    comparison << "# Comparação: Experimental vs Simulado Otimizado" << std::endl;
    comparison << "# Tempo(s), Uptake_Exp(kg/kg), Uptake_Sim(kg/kg), Erro_Abs" << std::endl;
    
    for (size_t i = 0; i < exp_data.time.size(); i++) {
        double sim_uptake = 0.0;
        // Interpolar resultado simulado
        for (size_t j = 0; j < optimized_result.time.size() - 1; j++) {
            if (exp_data.time[i] >= optimized_result.time[j] && 
                exp_data.time[i] <= optimized_result.time[j+1]) {
                double t1 = optimized_result.time[j];
                double t2 = optimized_result.time[j+1];
                double u1 = optimized_result.uptake_total[j];
                double u2 = optimized_result.uptake_total[j+1];
                sim_uptake = u1 + (u2 - u1) * (exp_data.time[i] - t1) / (t2 - t1);
                break;
            }
        }
        
        double error = std::abs(exp_data.uptake[i] - sim_uptake);
        comparison << std::scientific << exp_data.time[i] << ", " 
                   << exp_data.uptake[i] << ", " << sim_uptake << ", " << error << std::endl;
    }
    comparison.close();
    
    std::cout << "\nArquivos gerados:" << std::endl;
    std::cout << "  - dados_experimentais.csv" << std::endl;
    std::cout << "  - simulacao_inicial.csv" << std::endl;
    std::cout << "  - simulacao_otimizada.csv" << std::endl;
    std::cout << "  - comparacao_resultados.csv" << std::endl;
    
    return 0;
}