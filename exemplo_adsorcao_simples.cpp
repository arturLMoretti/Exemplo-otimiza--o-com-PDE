#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <random>
#include <algorithm>

// Estrutura para parâmetros do modelo simplificado
struct ModelParams {
    double k1;          // Constante de velocidade de adsorção (1/s)
    double k2;          // Constante de velocidade de dessorção (1/s)
    double D_eff;       // Difusividade efetiva (m²/s)
    double R;           // Raio da partícula (m)
    double q_max;       // Capacidade máxima (mg/g)
    double C0;          // Concentração inicial (mg/L)
};

// Dados experimentais
struct ExperimentalData {
    std::vector<double> time;
    std::vector<double> uptake;
    std::vector<double> concentration;
};

// Modelo simplificado de adsorção com cinética de primeira ordem
class SimpleAdsorptionModel {
private:
    ModelParams params;
    
public:
    SimpleAdsorptionModel(const ModelParams& p) : params(p) {}
    
    // Modelo cinético simplificado: dq/dt = k1*C*(q_max - q) - k2*q
    std::pair<std::vector<double>, std::vector<double>> simulate(double t_final, double dt) {
        int n_steps = static_cast<int>(t_final / dt) + 1;
        std::vector<double> time(n_steps);
        std::vector<double> uptake(n_steps);
        
        double q = 0.0;  // Uptake inicial
        double C = params.C0;  // Concentração inicial
        
        for (int i = 0; i < n_steps; i++) {
            time[i] = i * dt;
            uptake[i] = q;
            
            // Equação cinética simplificada
            double dqdt = params.k1 * C * (params.q_max - q) - params.k2 * q;
            
            // Balanço de massa (assumindo volume fixo)
            double volume_ratio = 1.0; // Simplificação
            double dCdt = -volume_ratio * dqdt;
            
            // Integração de Euler
            q += dqdt * dt;
            C += dCdt * dt;
            
            // Garantir valores físicos
            q = std::max(0.0, std::min(params.q_max, q));
            C = std::max(0.0, C);
        }
        
        return {time, uptake};
    }
    
    // Função objetivo para otimização
    double calculate_error(const ExperimentalData& exp_data) {
        auto [sim_time, sim_uptake] = simulate(exp_data.time.back(), 
                                             exp_data.time.back() / 100.0);
        
        double mse = 0.0;
        int count = 0;
        
        for (size_t i = 0; i < exp_data.time.size(); i++) {
            // Interpolar valor simulado
            double sim_value = interpolate(sim_time, sim_uptake, exp_data.time[i]);
            double error = sim_value - exp_data.uptake[i];
            mse += error * error;
            count++;
        }
        
        return count > 0 ? std::sqrt(mse / count) : 1e6;
    }
    
    void update_params(const std::vector<double>& new_params) {
        if (new_params.size() >= 4) {
            params.k1 = new_params[0];
            params.k2 = new_params[1];
            params.D_eff = new_params[2];
            params.q_max = new_params[3];
        }
    }
    
    ModelParams get_params() const { return params; }
    
private:
    double interpolate(const std::vector<double>& x, const std::vector<double>& y, double xi) {
        if (xi <= x.front()) return y.front();
        if (xi >= x.back()) return y.back();
        
        for (size_t i = 0; i < x.size() - 1; i++) {
            if (xi >= x[i] && xi <= x[i+1]) {
                double t = (xi - x[i]) / (x[i+1] - x[i]);
                return y[i] + t * (y[i+1] - y[i]);
            }
        }
        return y.back();
    }
};

// Gerar dados experimentais sintéticos
ExperimentalData generate_synthetic_data() {
    ModelParams true_params = {0.1, 0.001, 1e-9, 0.001, 50.0, 100.0};
    SimpleAdsorptionModel true_model(true_params);
    
    auto [time, uptake] = true_model.simulate(300.0, 1.0); // 5 minutos
    
    ExperimentalData data;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> noise(0.0, 0.05); // 5% de ruído
    
    // Selecionar pontos experimentais
    for (size_t i = 0; i < time.size(); i += 10) { // A cada 10 segundos
        data.time.push_back(time[i]);
        double noisy_uptake = uptake[i] * (1.0 + noise(gen));
        data.uptake.push_back(std::max(0.0, noisy_uptake));
    }
    
    std::cout << "Dados sintéticos gerados: " << data.time.size() << " pontos" << std::endl;
    std::cout << "Uptake final: " << data.uptake.back() << " mg/g" << std::endl;
    
    return data;
}

// Algoritmo de otimização por busca em grade
std::vector<double> grid_search_optimization(SimpleAdsorptionModel& model,
                                           const ExperimentalData& exp_data) {
    
    std::cout << "Iniciando otimização por busca em grade..." << std::endl;
    
    // Faixas de parâmetros
    std::vector<double> k1_values = {0.01, 0.05, 0.1, 0.2, 0.5};
    std::vector<double> k2_values = {0.0001, 0.001, 0.01, 0.05};
    std::vector<double> D_values = {1e-10, 1e-9, 1e-8, 1e-7};
    std::vector<double> q_values = {20.0, 30.0, 40.0, 50.0, 60.0};
    
    double best_error = 1e6;
    std::vector<double> best_params = {0.1, 0.001, 1e-9, 50.0};
    
    int total_combinations = k1_values.size() * k2_values.size() * 
                           D_values.size() * q_values.size();
    int current_combination = 0;
    
    for (double k1 : k1_values) {
        for (double k2 : k2_values) {
            for (double D : D_values) {
                for (double q_max : q_values) {
                    std::vector<double> params = {k1, k2, D, q_max};
                    model.update_params(params);
                    
                    double error = model.calculate_error(exp_data);
                    
                    if (error < best_error) {
                        best_error = error;
                        best_params = params;
                        std::cout << "Novo melhor: k1=" << k1 << ", k2=" << k2 
                                 << ", D=" << D << ", q_max=" << q_max 
                                 << ", erro=" << error << std::endl;
                    }
                    
                    current_combination++;
                    if (current_combination % 50 == 0) {
                        std::cout << "Progresso: " << (100.0 * current_combination / total_combinations) 
                                 << "%" << std::endl;
                    }
                }
            }
        }
    }
    
    std::cout << "Otimização concluída. Melhor erro: " << best_error << std::endl;
    return best_params;
}

// Salvar resultados
void save_results(const std::vector<double>& time,
                 const std::vector<double>& uptake,
                 const std::string& filename) {
    std::ofstream file(filename);
    file << "# Tempo(s), Uptake(mg/g)" << std::endl;
    file << std::fixed << std::setprecision(6);
    
    for (size_t i = 0; i < time.size(); i++) {
        file << time[i] << ", " << uptake[i] << std::endl;
    }
    file.close();
    std::cout << "Resultados salvos em: " << filename << std::endl;
}

void save_experimental_data(const ExperimentalData& data, const std::string& filename) {
    std::ofstream file(filename);
    file << "# Dados Experimentais" << std::endl;
    file << "# Tempo(s), Uptake(mg/g)" << std::endl;
    file << std::fixed << std::setprecision(6);
    
    for (size_t i = 0; i < data.time.size(); i++) {
        file << data.time[i] << ", " << data.uptake[i] << std::endl;
    }
    file.close();
    std::cout << "Dados experimentais salvos em: " << filename << std::endl;
}

int main() {
    std::cout << "=== OTIMIZAÇÃO DE ADSORÇÃO - MODELO SIMPLIFICADO ===" << std::endl;
    std::cout << "Modelo: Cinética de pseudo-segunda ordem" << std::endl;
    std::cout << "Isoterma: Langmuir simplificada" << std::endl << std::endl;
    
    // 1. Gerar dados experimentais
    auto exp_data = generate_synthetic_data();
    save_experimental_data(exp_data, "dados_experimentais_simples.csv");
    
    // 2. Configurar modelo inicial
    ModelParams initial_params = {0.05, 0.005, 1e-8, 30.0, 100.0, 100.0};
    SimpleAdsorptionModel model(initial_params);
    
    // 3. Simulação com parâmetros iniciais
    std::cout << "\n=== SIMULAÇÃO INICIAL ===" << std::endl;
    auto [time_initial, uptake_initial] = model.simulate(300.0, 1.0);
    save_results(time_initial, uptake_initial, "simulacao_inicial_simples.csv");
    double initial_error = model.calculate_error(exp_data);
    std::cout << "Erro inicial (RMSE): " << initial_error << " mg/g" << std::endl;
    
    // 4. Otimização
    std::cout << "\n=== OTIMIZAÇÃO ===" << std::endl;
    auto optimal_params = grid_search_optimization(model, exp_data);
    
    // 5. Simulação otimizada
    std::cout << "\n=== SIMULAÇÃO OTIMIZADA ===" << std::endl;
    model.update_params(optimal_params);
    auto [time_opt, uptake_opt] = model.simulate(300.0, 1.0);
    save_results(time_opt, uptake_opt, "simulacao_otimizada_simples.csv");
    double final_error = model.calculate_error(exp_data);
    
    // 6. Resultados
    std::cout << "\n=== RESULTADOS ===" << std::endl;
    std::cout << "Parâmetros otimizados:" << std::endl;
    std::cout << "  k1 (1/s):      " << std::scientific << optimal_params[0] << std::endl;
    std::cout << "  k2 (1/s):      " << std::scientific << optimal_params[1] << std::endl;
    std::cout << "  D_eff (m²/s):  " << std::scientific << optimal_params[2] << std::endl;
    std::cout << "  q_max (mg/g):  " << std::fixed << optimal_params[3] << std::endl;
    
    std::cout << "\\nErros:" << std::endl;
    std::cout << "  Inicial: " << std::fixed << std::setprecision(4) << initial_error << " mg/g" << std::endl;
    std::cout << "  Final:   " << std::fixed << std::setprecision(4) << final_error << " mg/g" << std::endl;
    std::cout << "  Melhoria: " << std::fixed << std::setprecision(1) 
              << (100.0 * (initial_error - final_error) / initial_error) << "%" << std::endl;
    
    // 7. Salvar comparação
    std::ofstream comparison("comparacao_simples.csv");
    comparison << "# Tempo(s), Experimental(mg/g), Inicial(mg/g), Otimizado(mg/g)" << std::endl;
    comparison << std::fixed << std::setprecision(6);
    
    for (size_t i = 0; i < exp_data.time.size(); i++) {
        double t = exp_data.time[i];
        double exp_val = exp_data.uptake[i];
        
        // Interpolar valores simulados
        double initial_val = 0.0, opt_val = 0.0;
        for (size_t j = 0; j < time_initial.size() - 1; j++) {
            if (t >= time_initial[j] && t <= time_initial[j+1]) {
                double alpha = (t - time_initial[j]) / (time_initial[j+1] - time_initial[j]);
                initial_val = uptake_initial[j] + alpha * (uptake_initial[j+1] - uptake_initial[j]);
                opt_val = uptake_opt[j] + alpha * (uptake_opt[j+1] - uptake_opt[j]);
                break;
            }
        }
        
        comparison << t << ", " << exp_val << ", " << initial_val << ", " << opt_val << std::endl;
    }
    comparison.close();
    
    std::cout << "\\nArquivos gerados:" << std::endl;
    std::cout << "  - dados_experimentais_simples.csv" << std::endl;
    std::cout << "  - simulacao_inicial_simples.csv" << std::endl;
    std::cout << "  - simulacao_otimizada_simples.csv" << std::endl;
    std::cout << "  - comparacao_simples.csv" << std::endl;
    
    return 0;
}