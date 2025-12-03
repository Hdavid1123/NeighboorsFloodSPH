#pragma once
#include <vector>
#include "io/particle.h"

// Tipos de densidad disponibles
enum class DensityType {
    RAW,
    NORMALIZED
};

// Densidad cruda (sin normalizar)
void computeRawDensity(std::vector<Particle>& particles,
                       int nParticles,
                       int nBoundary,
                       bool silent = false);

// Densidad normalizada (llama internamente a computeRawDensity con silent=true)
void computeNormalizedDensity(std::vector<Particle>& particles,
                              int nParticles,                          
                              int nBoundary);

// Función de interfaz: decide qué densidad calcular
void computeDensity(std::vector<Particle>& particles,
                    int nParticles,
                    int nBoundary,
                    DensityType type);

// Imprime las densidades de cada partícula en cada paso de tiempo
void exportDensityByTime(std::vector<Particle>& particles,
                         int nParticles,
                         double time,
                         const std::string& filename="test_results/density_by_time.txt");
