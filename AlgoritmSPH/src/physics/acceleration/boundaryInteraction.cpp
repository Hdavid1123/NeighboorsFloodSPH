#include "physics/acceleration/boundaryInteraction.h"
#include <cmath>
#include <iostream>
#include <fstream>

void boundaryInteraction(std::vector<Particle>& particles, double dr,
                         int nBoundary, int nParticles)
{
    int n1 = 12, n2 = 4;
    double D  = 0; //0.01 para 1e-3, 1 para 0.1
    double r0 = 0.5 * dr;

    std::cout << "[INFO] El valor de D en boundaryInteraction es: " << D << "\n"; 

    // Iterar solo sobre partículas de fluido
    for (int i = nBoundary; i < nParticles; i++) {
        Particle& pi = particles[i];
        if (pi.type != Particle::Fluid) continue;

        for (size_t k = 0; k < pi.neighbors.size(); k++) {
            int j = pi.neighbors[k];
            Particle& pj = particles[j];
            if (pj.type != Particle::Boundary && pj.type != Particle::Hole) continue;

            double xij = pi.pos[0] - pj.pos[0];
            double yij = pi.pos[1] - pj.pos[1];
            double rij = std::sqrt(xij*xij + yij*yij);

            if (rij < r0) {
                double factor = D * (std::pow(r0/rij, n1) - std::pow(r0/rij, n2)) / (rij*rij);
                pi.accel[0] += factor * xij;
                pi.accel[1] += factor * yij;
            }
        }
    }
}