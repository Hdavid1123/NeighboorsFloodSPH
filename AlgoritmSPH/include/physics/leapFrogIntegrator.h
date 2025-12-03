#pragma once
#include <vector>
#include "io/particle.h"
#include "physics/acceleration.h"

// Integrador Leap-Frog completo
void integrateStep(std::vector<Particle>& particles,
                   int nBoundary,
                   int nParticles,
                   int step,
                   double dt,
                   double g,
                   double dr,
                   double fluidHeight,
                   EOSType eosType);
