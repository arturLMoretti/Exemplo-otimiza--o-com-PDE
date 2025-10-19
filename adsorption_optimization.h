#ifndef ADSORPTION_OPTIMIZATION_H
#define ADSORPTION_OPTIMIZATION_H

#include <vector>
#include <string>

// Estrutura para parâmetros do modelo de adsorção
struct AdsorptionParams {
    double R;           // Raio da partícula (m)
    double D_eff;       // Difusividade efetiva (m²/s)
    double k_L;         // Constante de Langmuir (m³/kg)
    double q_max;       // Capacidade máxima de adsorção (kg/kg)
    double C_0;         // Concentração inicial externa (kg/m³)
    double rho_p;       // Densidade da partícula (kg/m³)
    double epsilon;     // Porosidade
    double k_f;         // Coeficiente de transferência de massa externa (m/s)
    
    // Parâmetros numéricos
    int Nr;             // Número de pontos radiais
    double t_final;     // Tempo final (s)
    double dt;          // Passo de tempo (s)
};

// Estrutura para resultados da simulação
struct SimulationResult {
    std::vector<double> time;
    std::vector<double> uptake_total;       // Captação total
    std::vector<std::vector<double>> C;     // Concentração vs raio e tempo
    std::vector<std::vector<double>> q;     // Concentração adsorvida vs raio e tempo
    std::vector<double> C_external;        // Concentração externa vs tempo
    double final_uptake;
    bool converged;
};

// Estrutura para dados experimentais
struct ExperimentalData {
    std::vector<double> time;
    std::vector<double> uptake;
};

// Classe principal para simulação e otimização
class AdsorptionOptimizer {
public:
    AdsorptionOptimizer(const AdsorptionParams& params);
    
    // Simulação da PDE de difusão com adsorção
    SimulationResult simulate();
    
    // Função objetivo para otimização (erro quadrático médio)
    double objective_function(const std::vector<double>& parameters, 
                            const ExperimentalData& exp_data);
    
    // Otimização usando algoritmo de Nelder-Mead simplex
    std::vector<double> optimize(const ExperimentalData& exp_data,
                               const std::vector<double>& initial_guess,
                               const std::vector<double>& lower_bounds,
                               const std::vector<double>& upper_bounds);
    
    // Salvar resultados
    void save_results(const SimulationResult& result, const std::string& filename);
    void save_optimization_results(const std::vector<double>& optimal_params,
                                 const ExperimentalData& exp_data,
                                 const std::string& filename);
    
    // Atualizar parâmetros
    void update_parameters(const std::vector<double>& new_params);
    
    // Getters
    AdsorptionParams get_parameters() const { return params_; }

private:
    AdsorptionParams params_;
    
    // Métodos auxiliares para solução numérica
    void solve_pde_step(const std::vector<double>& C_old,
                       std::vector<double>& C_new,
                       double C_ext,
                       const std::vector<double>& r,
                       double dr,
                       double alpha,
                       double t);
    void solve_tridiagonal(const std::vector<double>& a,
                          const std::vector<double>& b,
                          const std::vector<double>& c,
                          const std::vector<double>& d,
                          std::vector<double>& x);
    double langmuir_isotherm(double C) const;
    double langmuir_derivative(double C) const;
    void update_adsorbed_concentration(std::vector<double>& q, const std::vector<double>& C);
    double calculate_total_uptake(const std::vector<double>& q) const;
    double interpolate_uptake(const SimulationResult& result, double target_time);
    
    // Métodos para otimização
    std::vector<std::vector<double>> create_simplex(const std::vector<double>& initial,
                                                   const std::vector<double>& step_size);
    std::vector<double> centroid(const std::vector<std::vector<double>>& simplex, int exclude);
    std::vector<double> reflect(const std::vector<double>& worst, 
                              const std::vector<double>& centroid, double alpha = 1.0);
    std::vector<double> expand(const std::vector<double>& reflected,
                             const std::vector<double>& centroid, double gamma = 2.0);
    std::vector<double> contract(const std::vector<double>& point,
                               const std::vector<double>& centroid, double rho = 0.5);
    bool check_bounds(const std::vector<double>& params,
                     const std::vector<double>& lower,
                     const std::vector<double>& upper);
};

#endif // ADSORPTION_OPTIMIZATION_H