#pragma once
#include <vector>
#include "io/particle.h"  // Para la definición de Particle

// Interacción repulsiva con partículas de frontera
void boundaryInteraction(std::vector<Particle>& particles,
                         double dr,
                         int nBoundary,
                         int nParticles);
