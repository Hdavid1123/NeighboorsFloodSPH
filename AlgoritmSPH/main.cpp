#include <iostream>
#include <fstream>
#include <chrono>
#include <nlohmann/json.hpp>

#include "io/readParticles.h"
#include "io/particleSummary.h"
#include "io/outputParticles.h"
#include "kernel/cubicSplineKernel.h"
#include "core/neighbors.h"
#include "physics/density.h"
#include "physics/leapFrogIntegrator.h"
#include "physics/acceleration/pressure.h"

using json = nlohmann::json;

int main(int argc, char* argv[]) {
     
    try {
        
        // 1. Validación de argumento de línea de comandos
        if (argc != 2) {
            std::cerr << "Uso: " << argv[0] << " <ruta_al_archivo_JSON>\n";
            std::cerr << "Ejemplo: ./simulacion config/params.json\n";
            return 1;
        }

        std::string config_path = argv[1];
        std::cout << "[INFO] Leyendo parámetros desde: " << config_path << "\n";

        // 2. Cargar archivo JSON
        std::ifstream file(config_path);
        if (!file.is_open())
            throw std::runtime_error("No se pudo abrir el archivo JSON: " + config_path);

        json params;
        file >> params;
        file.close();

        // 3. Extraer parámetros principales
        std::string filename             = params["io"]["input_file"];
        std::string output_dir_sim       = params["io"]["output_dir_simulation"];
        
        double h_factor                  = params["kernel"]["h_factor"];
        bool enable_kernel_test          = params["kernel"]["test_enabled"];
        std::string kernel_output_dir    = params["kernel"]["output_dir"];
        
        double dt                        = params["integrator"]["dt"];
        int nSteps                       = params["integrator"]["n_steps"];
        double alpha                     = params["viscosity"]["alpha"];
        double g                         = params["physics"]["gravity_magnitude"];
        bool enable_neighbor_test        = params["simulation"]["enable_neighbor_test"];
        
        std::string test_NN_output_dir   = params["neighbors"]["test_NN_output_dir"];
        std::string neighbor_method      = params["neighbors"]["search_method"];
        std::string density_type_str = params["physics"]["density_type"];
        std::string eos_type_str = params["physics"]["EoS"];

        // Convertir el tipo de densidad desde string a enum
        DensityType density_type;
        if (density_type_str == "raw") {
        density_type = DensityType::RAW;
        } 
        else if (density_type_str == "normalized") {
            density_type = DensityType::NORMALIZED;
        } 
        else {
            throw std::runtime_error("Tipo de densidad desconocido: " + density_type_str +
                                    ". Opciones válidas: 'raw' o 'normalized'.");
        }

        // Convertir el tipo de EoS desde string a enum
        EOSType eos_type;
        if (eos_type_str == "Adami") {
            eos_type = EOSType::Adami;
        } 
        else if (eos_type_str == "Korzani") {
            eos_type = EOSType::Korzani;
        } 
        else {
            throw std::runtime_error("Tipo de EoS desconocido: " + eos_type_str +
                                    ". Opciones válidas: 'Adami' o 'Korzani'.");
        }

        // 4. Leer parámetros físicos del bloque "eos_params"
        json eos_params = params["physics"]["eos_params"];
        double rho0 = eos_params.value("rho0", 1000.0);
        double gamma = eos_params.value("gamma", 7.0);

        if (eos_type == EOSType::Adami) {
            double B    = eos_params["Adami"].value("B", 1.0);
            double c    = eos_params["Adami"].value("c", 0.01);
            setAdamiParams(B, c, rho0, gamma);
            std::cout << "[INFO] Configurada EoS Adami con parámetros:\n"
              << "       B=" << B << ", c=" << c << ", rho0=" << rho0 
              << ", gamma=" << gamma << "\n";
        }
        else if (eos_type == EOSType::Korzani) {
            double ca_factor = eos_params["korzani"].value("ca_factor", 10.0);
            setKorzaniParams(ca_factor, rho0, gamma);
            std::cout << "[INFO] Configurada EoS Korzani con parámetros:\n"
                      << "       ca_factor=" << ca_factor 
                      << ", rho0=" << rho0 
                      << ", gamma=" << gamma << "\n";
        }

        // 5. Leer partículas iniciales
        std::vector<Particle> particles = readParticlesFromFile(filename);
        std::cout << "Se leyeron " << particles.size() 
                  << " partículas desde el archivo " << filename << "\n";

        // 5. Calcular estadísticas
        ParticleStats stats = computeParticleSummary(particles);
        double nFluid = stats.nFluid;
        double nBoundary = stats.nBoundary;
        double nParticles = stats.nParticles;
        double fluidHeight = stats.fluidHeight;
        double dr = particles[0].h / h_factor;    // Separación inicial partículas
        
        printParticleSummary(particles);
        
        // 6. Test de Kernel
        if (enable_kernel_test) {
            std::cout << "[INFO] Ejecutando test del kernel...\n";
            testKernel(kernel_output_dir);
        } else {
            std::cout << "[INFO] Test del kernel deshabilitado.\n";
        }

        // 7. Ciclo principal de simulación
        double time = 0.0;
        auto start_total = std::chrono::high_resolution_clock::now();

        for (int step = 0; step < nSteps; step++) {

            // 7.1. Busqueda inicial de vecinos y guarda el número de vecinos en un archivo
            if (neighbor_method == "brute_force") {
                findNeighborsBruteForce(particles, nParticles, nBoundary, nFluid);
            }
            else if (neighbor_method == "quadtree") {
                findNeighborsQuadtree(particles, nParticles, nBoundary, nFluid);
            } 
            else {
                throw std::runtime_error("Método de búsqueda de vecinos desconocido: " + neighbor_method);
            }
       
            // 7.2. Test de vecinos (primer step)
            if (enable_neighbor_test && step == 0)
             testNeighbors(particles, nBoundary, nFluid, test_NN_output_dir);

            // 7.3. Cálculo de densidad y guarda densidad por partícula
            computeDensity(particles, nParticles, nBoundary, density_type);
            //exportDensityByTime(particles, nParticles,time);

            // 7.4. Integración de fuerzas
            integrateStep(particles, nBoundary, nParticles, step,
                          dt, g, alpha, fluidHeight, eos_type);

            // 7.5. Guarda el estado actual
            printState(particles, step, output_dir_sim);

            // 7.6. Actualizar el tiempo
            time += dt;

            std::cout << "Step " << step << " completado, tiempo = " << time << "\n\n";
    }
    auto end_total = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed_total = end_total - start_total;
    std::cout << "Duración total del ciclo (" << nSteps 
              << " pasos) = " << elapsed_total.count() << " s\n\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}
