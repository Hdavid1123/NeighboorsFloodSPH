#include <vector>
#include "io/particle.h"
#include "physics/acceleration/pressure.h"

// Computa Navier-Stokes con gravedad y presión SPH
void computeNavierStokes(std::vector<Particle>& particles,
                         int nBoundary,
                         int nParticles,
                         int step,
                         double g,
                         double fluidHeight,
                         EOSType eosType)
{
    // 1. Calcular presión usando el EOS seleccionado
    computePressure(particles, nBoundary, nParticles, step, g, fluidHeight, eosType);

    // 2. Loop sobre partículas de fluido
    for (int i = nBoundary; i < nParticles; i++) {
        Particle& pi = particles[i];
        if (pi.type != Particle::Fluid) continue;

        pi.accel[0] = 0.0;
        pi.accel[1] = g; // gravedad, incluir signo en params
        pi.dinternalE = 0.0;

        // 3. Loop sobre vecinos
        for (size_t k = 0; k < pi.neighbors.size(); k++) {
            int j = pi.neighbors[k];
            Particle& pj = particles[j];

            if (pj.type != Particle::Fluid) continue;      // Las fronteras no aportan al cálculo de presión.

            double pij = (pi.pressure / (pi.rho * pi.rho)) +
                         (pj.pressure / (pj.rho * pj.rho));

            pi.accel[0] -= pj.mass * pij * pi.dWx[k];
            pi.accel[1] -= pj.mass * pij * pi.dWy[k];

            double vdw = (pi.vel[0] - pj.vel[0]) * pi.dWx[k] +
                         (pi.vel[1] - pj.vel[1]) * pi.dWy[k];

            pi.dinternalE += 0.5 * pj.mass * pij * vdw;
        }
    }
}
