#include "physics/acceleration/viscosity.h"
#include <cmath>

void viscosity(std::vector<Particle>& particles,
               double alpha, int nBoundary, int nParticles) {
    //const double alpha = 0.1;
    const double eps = 0.01;

    for (int i = nBoundary; i < nParticles; i++) {
        Particle& pi = particles[i];
        if (pi.type != Particle::Fluid) continue;

        for (size_t k = 0; k < pi.neighbors.size(); k++) {
            int j = pi.neighbors[k];
            Particle& pj = particles[j];

            double xij = pi.pos[0] - pj.pos[0];
            double yij = pi.pos[1] - pj.pos[1];
            double vxij = pi.vel[0] - pj.vel[0];
            double vyij = pi.vel[1] - pj.vel[1];
           
            double vijrij = vxij*xij + vyij*yij;
            if (vijrij >= 0.0) continue;

            double r2 = xij*xij + yij*yij;
            double hij = 0.5 * (pi.h + pj.h);
            double cij = 0.5 * (pi.soundVel + pj.soundVel);
            double rhoij = pi.rho + pj.rho;

            double nu = 2.0 * alpha * hij * cij / rhoij;

            double Piij = -nu * vijrij / (r2 + eps * hij * hij);

            pi.accel[0] -= pj.mass * Piij * pi.dWx[k];
            pi.accel[1] -= pj.mass * Piij * pi.dWx[k];
        }
    }
}
