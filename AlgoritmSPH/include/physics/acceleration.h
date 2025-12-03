#pragma once
#include <vector>
#include "io/particle.h"
#include "physics/acceleration/navierStokes.h"
#include "physics/acceleration/viscosity.h"

// Orquestador de aceleraciones SPH
// Calcula: Navier-Stokes + (más adelante: viscosidad, repulsión de fronteras)
void computeAcceleration(std::vector<Particle>& particles,
                         int nBoundary,
                         int nParticles,
                         int step,
                         double dt,
                         double g,
                         double dr,
                         double fluidHeight,
                         EOSType eosType);
