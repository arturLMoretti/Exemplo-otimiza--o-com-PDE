#include "adsorption_optimization.h"
#include <iostream>
#include <fstream>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <numeric>

AdsorptionOptimizer::AdsorptionOptimizer(const AdsorptionParams& params) : params_(params) {}

SimulationResult AdsorptionOptimizer::simulate() {
    SimulationResult result;
    
    // Inicializar malha radial
    std::vector<double> r(params_.Nr);
    double dr = params_.R / (params_.Nr - 1);
    for (int i = 0; i < params_.Nr; i++) {
        r[i] = i * dr;
    }
    
    // Inicializar concentrações
    std::vector<double> C(params_.Nr, 0.0);
    std::vector<double> q(params_.Nr, 0.0);
    std::vector<double> C_new(params_.Nr);
    
    // Condições iniciais
    double C_ext = params_.C_0;
    
    // Parâmetros numéricos
    int Nt = static_cast<int>(params_.t_final / params_.dt) + 1;
    double alpha = params_.D_eff * params_.dt / (dr * dr);
    
    // Inicializar vetores de resultado
    result.time.reserve(Nt);
    result.uptake_total.reserve(Nt);
    result.C_external.reserve(Nt);
    result.C.resize(Nt, std::vector<double>(params_.Nr));
    result.q.resize(Nt, std::vector<double>(params_.Nr));
    
    std::cout << "Iniciando simulação de adsorção..." << std::endl;
    std::cout << "Parâmetros:" << std::endl;
    std::cout << "  R = " << params_.R << " m" << std::endl;
    std::cout << "  D_eff = " << params_.D_eff << " m²/s" << std::endl;
    std::cout << "  k_L = " << params_.k_L << " m³/kg" << std::endl;
    std::cout << "  q_max = " << params_.q_max << " kg/kg" << std::endl;
    
    // Loop temporal
    for (int n = 0; n < Nt; n++) {
        double t = n * params_.dt;
        
        // Decaimento exponencial da concentração externa (exemplo)
        C_ext = params_.C_0 * std::exp(-0.1 * t);
        
        // Resolver PDE usando diferenças finitas implícitas
        solve_pde_step(C, C_new, C_ext, r, dr, alpha, t);
        
        // Atualizar concentração adsorvida
        update_adsorbed_concentration(q, C);
        
        // Calcular uptake total
        double uptake = calculate_total_uptake(q);
        
        // Armazenar resultados
        result.time.push_back(t);
        result.uptake_total.push_back(uptake);
        result.C_external.push_back(C_ext);
        result.C[n] = C;
        result.q[n] = q;
        
        // Atualizar concentração
        C = C_new;
        
        // Progresso
        if (n % (Nt / 10) == 0) {
            std::cout << "Progresso: " << (100.0 * n / Nt) << "%" << std::endl;
        }
    }
    
    result.final_uptake = result.uptake_total.back();
    result.converged = true;
    
    std::cout << "Simulação concluída. Uptake final: " << result.final_uptake << " kg/kg" << std::endl;
    
    return result;
}

void AdsorptionOptimizer::solve_pde_step(const std::vector<double>& C_old,
                                       std::vector<double>& C_new,
                                       double C_ext,
                                       const std::vector<double>& r,
                                       double dr,
                                       double alpha,
                                       double t) {
    int Nr = params_.Nr;
    
    // Sistema tridiagonal para método implícito
    std::vector<double> a(Nr), b(Nr), c(Nr), d(Nr);
    
    // Centro (r = 0): condição de simetria dC/dr = 0
    b[0] = 1.0 + 6.0 * alpha;
    c[0] = -6.0 * alpha;
    d[0] = C_old[0];
    
    // Pontos internos
    for (int i = 1; i < Nr - 1; i++) {
        double r_i = r[i];
        double coef1 = alpha * (1.0 + dr / (2.0 * r_i));
        double coef2 = alpha * (1.0 - dr / (2.0 * r_i));
        
        a[i] = -coef2;
        b[i] = 1.0 + 2.0 * alpha + params_.dt * params_.rho_p * langmuir_derivative(C_old[i]);
        c[i] = -coef1;
        d[i] = C_old[i] + params_.dt * params_.rho_p * 
               (langmuir_isotherm(C_old[i]) - C_old[i] * langmuir_derivative(C_old[i]));
    }
    
    // Condição de contorno externa (r = R)
    int last = Nr - 1;
    double Bi = params_.k_f * params_.R / params_.D_eff; // Número de Biot
    
    a[last] = -1.0;
    b[last] = 1.0 + Bi * dr / params_.R;
    d[last] = Bi * dr * C_ext / params_.R;
    
    // Resolver sistema tridiagonal
    solve_tridiagonal(a, b, c, d, C_new);
}

void AdsorptionOptimizer::solve_tridiagonal(const std::vector<double>& a,
                                          const std::vector<double>& b,
                                          const std::vector<double>& c,
                                          const std::vector<double>& d,
                                          std::vector<double>& x) {
    int n = b.size();
    std::vector<double> c_star(n), d_star(n);
    
    // Forward sweep
    c_star[0] = c[0] / b[0];
    d_star[0] = d[0] / b[0];
    
    for (int i = 1; i < n; i++) {
        double denominator = b[i] - a[i] * c_star[i-1];
        c_star[i] = c[i] / denominator;
        d_star[i] = (d[i] - a[i] * d_star[i-1]) / denominator;
    }
    
    // Back substitution
    x[n-1] = d_star[n-1];
    for (int i = n-2; i >= 0; i--) {
        x[i] = d_star[i] - c_star[i] * x[i+1];
    }
}

double AdsorptionOptimizer::langmuir_isotherm(double C) const {
    return (params_.q_max * params_.k_L * C) / (1.0 + params_.k_L * C);
}

double AdsorptionOptimizer::langmuir_derivative(double C) const {
    double denominator = 1.0 + params_.k_L * C;
    return (params_.q_max * params_.k_L) / (denominator * denominator);
}

void AdsorptionOptimizer::update_adsorbed_concentration(std::vector<double>& q, 
                                                      const std::vector<double>& C) {
    for (size_t i = 0; i < q.size(); i++) {
        q[i] = langmuir_isotherm(C[i]);
    }
}

double AdsorptionOptimizer::calculate_total_uptake(const std::vector<double>& q) const {
    double total = 0.0;
    double dr = params_.R / (params_.Nr - 1);
    
    // Integração usando regra do trapézio em coordenadas esféricas
    for (int i = 0; i < params_.Nr - 1; i++) {
        double r1 = i * dr;
        double r2 = (i + 1) * dr;
        double vol_shell = (4.0/3.0) * M_PI * (r2*r2*r2 - r1*r1*r1);
        total += 0.5 * (q[i] + q[i+1]) * vol_shell;
    }
    
    double total_volume = (4.0/3.0) * M_PI * params_.R * params_.R * params_.R;
    return total / total_volume;
}

double AdsorptionOptimizer::objective_function(const std::vector<double>& parameters,
                                             const ExperimentalData& exp_data) {
    // Atualizar parâmetros
    auto old_params = params_;
    update_parameters(parameters);
    
    // Executar simulação
    auto result = simulate();
    
    // Calcular erro quadrático médio
    double mse = 0.0;
    int n_points = 0;
    
    for (size_t i = 0; i < exp_data.time.size(); i++) {
        // Interpolar resultado simulado no tempo experimental
        double sim_uptake = interpolate_uptake(result, exp_data.time[i]);
        double error = sim_uptake - exp_data.uptake[i];
        mse += error * error;
        n_points++;
    }
    
    // Restaurar parâmetros originais
    params_ = old_params;
    
    return n_points > 0 ? std::sqrt(mse / n_points) : 1e6;
}

double AdsorptionOptimizer::interpolate_uptake(const SimulationResult& result, double target_time) {
    if (target_time <= result.time.front()) return result.uptake_total.front();
    if (target_time >= result.time.back()) return result.uptake_total.back();
    
    // Interpolação linear
    for (size_t i = 0; i < result.time.size() - 1; i++) {
        if (target_time >= result.time[i] && target_time <= result.time[i+1]) {
            double t1 = result.time[i];
            double t2 = result.time[i+1];
            double u1 = result.uptake_total[i];
            double u2 = result.uptake_total[i+1];
            
            return u1 + (u2 - u1) * (target_time - t1) / (t2 - t1);
        }
    }
    
    return result.uptake_total.back();
}

void AdsorptionOptimizer::update_parameters(const std::vector<double>& new_params) {
    if (new_params.size() >= 1) params_.D_eff = new_params[0];
    if (new_params.size() >= 2) params_.k_L = new_params[1];
    if (new_params.size() >= 3) params_.q_max = new_params[2];
    if (new_params.size() >= 4) params_.k_f = new_params[3];
}

void AdsorptionOptimizer::save_results(const SimulationResult& result, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo: " << filename << std::endl;
        return;
    }
    
    file << "# Resultados da Simulação de Adsorção" << std::endl;
    file << "# Tempo(s), Uptake_Total(kg/kg), C_Externa(kg/m³)" << std::endl;
    file << std::scientific << std::setprecision(6);
    
    for (size_t i = 0; i < result.time.size(); i++) {
        file << result.time[i] << ", " 
             << result.uptake_total[i] << ", "
             << result.C_external[i] << std::endl;
    }
    
    file.close();
    std::cout << "Resultados salvos em: " << filename << std::endl;
}