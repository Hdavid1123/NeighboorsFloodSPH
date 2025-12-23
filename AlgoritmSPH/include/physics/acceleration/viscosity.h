#pragma once
#include <vector>
#include "io/particle.h"

// Función de viscosidad artificial Liu
void viscosity(std::vector<Particle>& particles,
               double alpha, int nBoundary, int nParticles);