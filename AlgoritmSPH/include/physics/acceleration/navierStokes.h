#pragma once
#include <vector>
#include "io/particle.h"
#include "physics/acceleration/pressure.h"

// Computa las aceleraciones SPH usando Navier-Stokes, presión y gravedad
void computeNavierStokes(std::vector<Particle>& particles,
                         int nBoundary,       
                         int nParticles,      
                         int step,            
                         double g,            
                         double fluidHeight,  // altura de la columna de fluido
                         EOSType eosType);    // tipo de EOS a usar (Monaghan o Korzani)
