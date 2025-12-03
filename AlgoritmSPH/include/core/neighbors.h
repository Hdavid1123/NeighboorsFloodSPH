#pragma once
#include <vector>
#include "io/particle.h"

// Declaración de la función para búsqueda de vecinos Fuerza Bruta
void findNeighborsBruteForce(std::vector<Particle>& particles,
                             int nParticles, int nBoundary, int nFluid);

void findNeighborsQuadtree(std::vector<Particle>& particles,
                           int nParticles, int nBoundary, int nFluid);


// Función de test de vecinos
void testNeighbors(const std::vector<Particle>& particles,
                   int nBoundary, int nFluid,
                   const std::string& output_dir);

// Función para registrar el número de vecinos por partícula en función del tiempo
void exportNeighborCountsByTime(std::vector<Particle>& particles, int nParticles, int nBoundary, double time,
                                const std::string& filename="test_results/neighbor_counts.txt");