#pragma once
#include <vector>
#include "io/particle.h"

// Función de viscosidad artificial Liu
void viscosity(std::vector<Particle>& particles, double dr,
               int nBoundary, int nParticles);