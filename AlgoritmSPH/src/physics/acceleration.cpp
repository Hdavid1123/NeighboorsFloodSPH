#include "physics/acceleration.h"
#include "physics/acceleration/navierStokes.h"
#include "physics/acceleration/viscosity.h"
#include "physics/acceleration/boundaryInteraction.h"
#include "physics/acceleration/meanVelocityXSPH.h"
#include <cmath>

// Por ahora solo llama a Navier-Stokes
void computeAcceleration(std::vector<Particle>& particles,
                         int nBoundary,
                         int nParticles,
                         int step,
                         double dt,
                         double g,
                         double dr,
                         double fluidHeight,
                         EOSType eosType)
{
    // 1. Navier-Stokes
    computeNavierStokes(particles, nBoundary, nParticles,
                        step, g, fluidHeight, eosType);

    // 2. Viscosidad del fluido.
    viscosity(particles, dr, nBoundary, nParticles);

    // 3. Interacción con fronteras.
    boundaryInteraction(particles, dr, nBoundary, nParticles);

    // 4. Corrección de velocidad XSPH
    meanVelocityXSPH(particles, nBoundary, nParticles);
}
