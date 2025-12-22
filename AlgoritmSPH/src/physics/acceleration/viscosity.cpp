#include "physics/acceleration/viscosity.h"
#include <cmath>

void viscosity(std::vector<Particle>& particles, double dr,
               int nBoundary, int nParticles) {
    double alphapi = 1.0e-2;
    double betapi  = 1.0e-2;
    double eps2 = 0.01 * dr * dr;

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

            if (vijrij < 0.0) {
                double hij = 0.5 * (pi.h + pj.h);
                double phiij = hij * vijrij / (xij*xij + yij*yij + eps2);
                double cij = 0.5 * (pi.soundVel + pj.soundVel);
                double rhoij = 0.5 * (pi.rho + pj.rho);

                double Piij = (-alphapi*cij*phiij + betapi*phiij*phiij) / rhoij;

                pi.accel[0] -= pj.mass * Piij * pi.dWx[k];
                pi.accel[1] -= pj.mass * Piij * pi.dWy[k];

                double vdw = vxij * pi.dWx[k] + vyij * pi.dWy[k];
                pi.dinternalE += 0.5 * pj.mass * Piij * vdw;
            }
        }
    }
}
