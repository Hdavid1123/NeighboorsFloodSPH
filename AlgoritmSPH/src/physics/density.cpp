#include <vector>
#include <cmath>
#include <iostream>
#include <fstream>      
#include <sstream>      
#include <filesystem>   
#include "kernel/cubicSplineKernel.h"
#include "physics/density.h"
#include "io/particle.h"


// Función base: densidad sin normalizar
void computeRawDensity(std::vector<Particle>& particles,
    int nParticles,
    int nBoundary,
    bool silent) {

    for (int i = nBoundary; i < nParticles; ++i) {
        Particle& pi = particles[i];

        double wii = cubicSplineKernel(0.0, pi.h);
        pi.rho = pi.mass * wii; // auto-contribución

        // Contribución de los vecinos
        for (size_t j = 0; j < pi.neighbors.size(); ++j) {
            int neighborIdx = pi.neighbors[j];
            Particle& pj = particles[neighborIdx];
            pi.rho += pj.mass * pi.W[j];
        }
    }
    if (!silent) {
        std::cout << "Uso densidad cruda\n\n";
    }
}

// Densidad SPH normalizada (Liu 2003 4.35) partículas de fluido
// rho_i = sum_j m_j * W_ij / (sum_j (m_j / rho_j) * W_ij)
void computeNormalizedDensity(std::vector<Particle>& particles,
    int nParticles,
    int nBoundary) {
    
    computeRawDensity(particles, nParticles, nBoundary, true);

    for (int i = nBoundary; i < nParticles; ++i) {
        Particle& pi = particles[i];
        double wii = cubicSplineKernel(0.0, pi.h);
        double norm = (pi.mass / pi.rho) * wii;

        for (size_t j = 0; j < pi.neighbors.size(); ++j) {
            int neighborIdx = pi.neighbors[j];
            Particle& pj = particles[neighborIdx];
            norm += (pj.mass / pj.rho) * pi.W[j];
        }

        pi.rho /= norm;
    }
    std::cout << "Uso densidad normalizada\n\n";
}

// Función orquestadora
void computeDensity(std::vector<Particle>& particles,
                    int nParticles,
                    int nBoundary,
                    DensityType type) 
{
    switch (type) {
        case DensityType::RAW:
            computeRawDensity(particles, nParticles, nBoundary);
            break;
        case DensityType::NORMALIZED:
            computeNormalizedDensity(particles, nParticles, nBoundary);
            break;
    }
}

// Registro de densidades (todas las partículas) en función del tiempo
void exportDensityByTime(std::vector<Particle>& particles,
                         int nParticles,
                         double time,
                         const std::string& filename) {
    std::filesystem::create_directories("test_results");

    // Leer archivo existente si ya hay datos
    std::ifstream fin(filename);
    std::vector<std::vector<std::string>> data;
    std::vector<std::string> prevTimes;
    bool fileExists = fin.is_open();

    if (fileExists) {
        std::string line;
        while (std::getline(fin, line)) {
            if (line.empty()) continue;

            if (line[0] == '#') {
                // Guardamos tiempos anteriores
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

    // Si el archivo no existía, inicializar filas con IDs
    if (!fileExists) {
        data.resize(nParticles);
        for (int i = 0; i < nParticles; i++) {
            data[i].push_back(std::to_string(particles[i].id));
        }
    }

    // Añadir nueva columna con la densidad rho de cada partícula
    double rhoSum = 0.0;
    for (int i = 0; i < nParticles; i++) {
        data[i].push_back(std::to_string(particles[i].rho));
        rhoSum += particles[i].rho;
    }

    // Guardar también el tiempo actual en la cabecera
    prevTimes.push_back(std::to_string(time));

    // Escribir archivo completo de nuevo
    std::ofstream fout(filename);
    if (!fout.is_open()) {
        throw std::runtime_error("No se pudo abrir " + filename);
    }

    // Cabecera
    fout << "# ID";
    for (const auto& t : prevTimes) fout << " " << t;
    fout << "\n";

    // Datos
    for (const auto& row : data) {
        for (size_t j = 0; j < row.size(); j++) {
            fout << row[j] << (j + 1 < row.size() ? " " : "");
        }
        fout << "\n";
    }

    fout.close();

    // Calcular y mostrar densidad promedio
    double rhoAvg = rhoSum / static_cast<double>(nParticles);
    std::cout << "Densidades exportadas para tiempo t=" << time << " ✅\n";
    std::cout << "Densidad promedio en t=" << time << " : " << rhoAvg << "\n\n";
}

