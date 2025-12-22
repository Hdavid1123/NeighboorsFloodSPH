#include <vector>
#include <cmath>
#include <iostream>
#include <fstream>
#include <cstdlib>   
#include <ctime>     
#include <iomanip>   
#include <filesystem> 
#include "kernel/cubicSplineKernel.h"
#include "core/tree_vecinos.h"
#include "io/particle.h"
#include <sstream>

// kappa = radio de búsqueda relativo al h
constexpr double KAPPA = 2.0;
constexpr double EPSILON = 1e-10;

void findNeighborsBruteForce(std::vector<Particle>& particles, int nParticles, int nBoundary, int nFluid) {
    
    std::cout << "[findNeighborsBruteForce] Buscando vecinos (Fuerza Bruta)...\n";
    std::cout << "Total partículas: " << nParticles << ", Fluido: " << nFluid << "\n";
    
    // El ciclo comienza en nBoundary porque primero están las fronteras
    for (int i = nBoundary; i < nParticles; i++){
        Particle& pi = particles[i];

        // Liberar buffers (equivalente a free en C)
        std::vector<int>().swap(pi.neighbors);
        std::vector<double>().swap(pi.dx);
        std::vector<double>().swap(pi.dy);
        std::vector<double>().swap(pi.r);
        std::vector<double>().swap(pi.W);
        std::vector<double>().swap(pi.dWx);
        std::vector<double>().swap(pi.dWy);

        // Buscar vecinos
        for (int j = 0; j < nParticles; j++) {
            if (i == j) continue; // no compararse consigo mismo

            const Particle& pj = particles[j];

            const double xij = pi.pos[0] - pj.pos[0];
            const double yij = pi.pos[1] - pj.pos[1];
            const double rij = std::hypot(xij, yij);// sqrt(x^2 + y^2)
            const double hij = 0.5 * (pi.h + pj.h);

            if (rij < KAPPA * hij + EPSILON) {
                // guardar vecino
                pi.neighbors.push_back(static_cast<int>(j)); // cast si neighbors es int
                pi.dx.push_back(xij);
                pi.dy.push_back(yij);
                pi.r.push_back(rij);

                // kernel y derivadas (tus funciones)
                double Wij = cubicSplineKernel(rij, hij);
                auto gradW = dCubicSplineKernel(rij, xij, yij, hij); // devuelve {dWx,dWy}

                pi.W.push_back(Wij);
                pi.dWx.push_back(gradW[0]);
                pi.dWy.push_back(gradW[1]);
            }
        }
    }
    std::cout << "Búsqueda de vecinos completada ✅\n\n";
}

// Búsqueda usando árbol quadtree (aún no implementada)
void findNeighborsQuadtree(std::vector<Particle>& particles,
                           int nParticles, int nBoundary, int nFluid)
{
    std::cout << "[findNeighborsQuadTree] Buscando vecinos (Quadtree)...\n";
    std::cout << "Total partículas: " << nParticles 
              << ", Fluido: " << nFluid << "\n";

    // -----------------------------------------
    // 1. Construcción del array normalizado pts
    // -----------------------------------------
    std::vector<particula> pts;
    pts.resize(nParticles);

    const float xmin = 0.0e-1f;
    const float ymin = -1.5e-1f;
    const float Lx = 2e-1f;
    const float Ly = Lx;
    const float invLx = 1.0f / Lx;
    const float invLy = 1.0f / Ly;

    for (int i = 0; i < nParticles; i++) {
        const auto& src = particles[i];
        auto& dest = pts[i];

        dest.pos[0] = (src.pos[0] - xmin) * invLx;
        dest.pos[1] = (src.pos[1] - ymin) * invLy;
    }

    // -----------------------------------------
    // 2. Construcción del Quadtree
    // -----------------------------------------
    NeighborSearch ns(pts, 1.0f);
    ns.build_tree();

    std::vector<vecinos_list> neigh(nParticles);

    // -----------------------------------------
    // 3. Búsqueda de vecinos
    // -----------------------------------------
    for (int i = 0; i < nParticles; i++)
    {
        Particle& pi = particles[i];
        const double hij = pi.h;

        // radio normalizado
        const float r_original = KAPPA * hij + EPSILON;
        const float r_normal = r_original / Lx;
        // -----------------------------------------
        // 3.1 Reset de estructuras sin liberar memoria
        // -----------------------------------------
        pi.neighbors.clear();
        pi.dx.clear();
        pi.dy.clear();
        pi.r.clear();
        pi.W.clear();
        pi.dWx.clear();
        pi.dWy.clear();
        // reservar memoria estimada para minimizar realocaciones
        pi.neighbors.reserve(48);
        pi.dx.reserve(48);
        pi.dy.reserve(48);
        pi.r.reserve(48);
        pi.W.reserve(48);
        pi.dWx.reserve(48);
        pi.dWy.reserve(48);

        neigh[i].nnei = 0;
        buscar_vecinos(
            ns.root_ptr(),
            pts.data(),
            i,
            r_normal,
            neigh[i].id_nei,
            &neigh[i].nnei
        );

        // -----------------------------------------
        // 3.2 Procesar vecinos
        // -----------------------------------------
        for (int j = 0; j < neigh[i].nnei; j++)
        {
            int id = neigh[i].id_nei[j];
            const Particle& pj = particles[id];

            const double xij = pi.pos[0] - pj.pos[0];
            const double yij = pi.pos[1] - pj.pos[1];
            const double rij = std::sqrt(xij*xij + yij*yij);

            pi.neighbors.push_back(id);
            pi.dx.push_back(xij);
            pi.dy.push_back(yij);
            pi.r.push_back(rij);

            // Kernel
            const double Wij = cubicSplineKernel(rij, hij);
            const auto gradW = dCubicSplineKernel(rij, xij, yij, hij);

            pi.W.push_back(Wij);
            pi.dWx.push_back(gradW[0]);
            pi.dWy.push_back(gradW[1]);
        }
    }

    std::cout << "Búsqueda de vecinos completada ✅\n\n";
}
    


void testNeighbors(const std::vector<Particle>& particles,
                   int nBoundary, int nFluid,
                   const std::string& output_dir) {
    namespace fs = std::filesystem;

    fs::create_directories(output_dir);
    std::string filepath = output_dir + "/NN_test.output";

    std::cout << "[testNeighbors] Ejecución test de vecinos...\n";

    std::ofstream fTest(filepath);
    if (!fTest.is_open()) {
        throw std::runtime_error("No se pudo abrir " + filepath);
    }

    std::srand(std::time(nullptr)); // semilla aleatoria

    for (int k = 0; k < 30; k++) {
        int i = nBoundary + (std::rand() % nFluid);
        const Particle& pi = particles[i];

        std::cout << "particle " << pi.id
                  << " tipo: " << pi.type
                  << " con " << pi.neighbors.size() << " vecinos\n";

        // escribir partícula principal
        fTest << std::setw(16) << pi.id
              << std::setw(16) << std::fixed << std::setprecision(10) << pi.pos[0]
              << std::setw(16) << pi.pos[1] << "\n";

        // escribir todos sus vecinos
        for (size_t j = 0; j < pi.neighbors.size(); j++) {
            int neighborIdx = pi.neighbors[j];
            const Particle& pj = particles[neighborIdx];
            fTest << std::setw(16) << pj.id
                  << std::setw(16) << pj.pos[0]
                  << std::setw(16) << pj.pos[1] << "\n";
        }

        fTest << "\n"; // salto entre bloques
    }

    fTest.close();
    std::cout << "Resultados de testNeighbors escritos en " << filepath << " ✅\n\n";
}

// Registro del número de vecinos para cada tiempo
void exportNeighborCountsByTime(std::vector<Particle>& particles,
                                int nParticles,
                                int nBoundary,
                                double time,
                                const std::string& output_dir) {
    namespace fs = std::filesystem;

    fs::create_directories(output_dir);
    std::string filename = output_dir + "/neighbor_counts.txt";

    // Leer el archivo existente (si existe)
    std::ifstream fin(filename);
    std::vector<std::vector<std::string>> data;
    std::vector<std::string> prevTimes;
    bool fileExists = fin.is_open();
    
    if (fileExists) {
        std::string line;
        while (std::getline(fin, line)) {
            if (line.empty()) continue;
            if (line[0] == '#') {
                std::istringstream iss(line);
                std::string val;
                iss >> val; // "#"
                iss >> val; // "ID"
                while (iss >> val) prevTimes.push_back(val);
            } else {
                std::istringstream iss(line);
                std::vector<std::string> row;
                std::string val;
                while (iss >> val) row.push_back(val);
                data.push_back(row);
            }            
        }
        fin.close();
    }

    if (!fileExists) {
        data.resize(nParticles - nBoundary);
        for (int i = nBoundary; i < nParticles; i++) {
            data[i - nBoundary].push_back(std::to_string(particles[i].id));
        }
    }

    for (int i = nBoundary; i < nParticles; i++) {
        data[i - nBoundary].push_back(std::to_string(particles[i].neighbors.size()));
    }

    prevTimes.push_back(std::to_string(time));

    std::ofstream fout(filename);
    if (!fout.is_open()) {
        throw std::runtime_error("No se pudo abrir " + filename);
    }

    fout << "# ID";
    for (const auto& t : prevTimes) fout << " " << t;
    fout << "\n";

    for (const auto& row : data) {
        for (size_t j = 0; j < row.size(); j++) {
            fout << row[j] << (j + 1 < row.size() ? " " : "");
        }
        fout << "\n";
    }

    fout.close();
    std::cout << "Número de vecinos exportado para tiempo t=" << time
              << " en " << filename << " ✅\n\n";
}