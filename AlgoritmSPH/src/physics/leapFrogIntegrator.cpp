#include "physics/leapFrogIntegrator.h"
#include "physics/acceleration.h"
#include "io/particle.h"

// Funciones internas privadas al archivo
static void drift(std::vector<Particle>& particles, double dt)
{
    for (auto& p : particles) {
        if (p.type != Particle::Fluid) continue;
        p.pos[0] += 0.5 * p.vel[0] * dt;
        p.pos[1] += 0.5 * p.vel[1] * dt;
        //p.internalE += 0.5 * dt * p.dinternalE;
    }
}

static void kick(std::vector<Particle>& particles, double dt)
{
    for (auto& p : particles) {
        if (p.type != Particle::Fluid) continue;
        // Se agrega una pequeña velocidad en x
        p.vel[0] += p.accel[0] * dt + 1e-10;
        p.vel[1] += p.accel[1] * dt;
    }
}

// Integrador Leap-Frog
void integrateStep(std::vector<Particle>& particles,
                   int nBoundary,
                   int nParticles,
                   int step,
                   double dt,
                   double g,
                   double alpha,
                   double fluidHeight,
                   EOSType eosType)
{
    // 1. Drift inicial (medio paso)
    drift(particles, dt);

    // 2. Cálculo de las aceleraciones (NS, Viscosity, Boundary Interaction, etc.)
    computeAcceleration(particles, nBoundary, nParticles,
                        step, dt, g, alpha, fluidHeight, eosType);
    
    // 3. Aporte de la aceleración en la velocidad
    kick(particles, dt);
    
    // 4. Segunda parte drift
    drift(particles, dt);
}
