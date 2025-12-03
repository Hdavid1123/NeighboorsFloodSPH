#pragma once
#include <vector>
#include "io/particle.h"

// Corrige la velocidad usando XSPH
void meanVelocityXSPH(std::vector<Particle>& particles,
                      int nBoundary,
                      int nParticles);
