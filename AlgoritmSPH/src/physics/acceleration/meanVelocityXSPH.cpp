#include "physics/acceleration/meanVelocityXSPH.h"
#include <vector>
#include "io/particle.h"

void meanVelocityXSPH(std::vector<Particle>& particles,
                      int nBoundary,
                      int nParticles)
{
    double epsilon = 0.3; // Parámetro XSPH

    // Iterar solo sobre partículas de fluido
    for (int i = nBoundary; i < nParticles; i++) {
        Particle& pi = particles[i];
        if (pi.type != Particle::Fluid) continue;

        double vxMean = 0.0;
        double vyMean = 0.0;

        for (size_t k = 0; k < pi.neighbors.size(); k++) {
            int j = pi.neighbors[k];
            Particle& pj = particles[j];

            double rhoij = 0.5 * (pi.rho + pj.rho);

            vxMean += (pj.mass / rhoij) * (pi.vel[0] - pj.vel[0]) * pi.W[k];
            vyMean += (pj.mass / rhoij) * (pi.vel[1] - pj.vel[1]) * pi.W[k];
        }

        pi.vel[0] -= epsilon * vxMean;
        pi.vel[1] -= epsilon * vyMean;
    }
}
