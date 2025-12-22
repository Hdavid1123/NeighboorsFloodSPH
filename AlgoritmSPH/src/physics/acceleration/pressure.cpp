#include <vector>
#include <cmath>
#include <iostream>
#include "physics/acceleration/pressure.h"
#include "io/particle.h"

// --- Variables globales de configuración ---
static MonaghanParams g_monaghanParams;
static KorzaniParams g_korzaniParams;

// --- Funciones setter ---
void setMonaghanParams(double B, double c, double rho0, double gamma) {
    g_monaghanParams = {B, c, rho0, gamma};
}

void setKorzaniParams(double ca_factor, double rho0, double gamma) {
    g_korzaniParams = {ca_factor, rho0, gamma};
}

// --- Implementación de EoS de Monaghan ---
// p = B * ((rho / rho0)^gamma - 1)
static void computeMonaghanPressure(std::vector<Particle>& particles,
                                    int nBoundary,
                                    int nParticles,
                                    int step)
{
    const auto& params = g_monaghanParams;

    // Inicializar presión en fronteras
    if (step == 0) {
        for (int i = 0; i < nBoundary; ++i) {
            Particle& pi = particles[i];
            pi.soundVel = params.c;
            pi.pressure = 0.0;
        }
    }

    // Presión en partículas de fluido
    for (int i = nBoundary; i < nParticles; ++i) {
        Particle& pi = particles[i];
        pi.soundVel = params.c;
        pi.pressure = params.B * (std::pow(pi.rho / params.rho0, params.gamma) - 1.0);
    }
}

// ----- NO USADA FINALMENTE -------

// --- Implementación de EoS de Korzani (2014) --- 
// p = rho0 * ca^2/gamma ((rho/rho0)^gamma -1)
static void computeKorzaniPressure(std::vector<Particle>& particles,
                                   int nBoundary,
                                   int nParticles,
                                   int step,
                                   double g,
                                   double fluidHeight)
{
    const auto& params = g_korzaniParams;

    double v_max = std::sqrt(2.0 * g * fluidHeight);
    double ca = params.ca_factor * v_max;

    if (step == 0) {
        for (int i = 0; i < nBoundary; ++i) {
            Particle& pi = particles[i];
            pi.soundVel = ca;
            pi.pressure = 0.0;
        }
    }

    double factor = params.rho0 * ca * ca / params.gamma;
    for (int i = nBoundary; i < nParticles; ++i) {
        Particle& pi = particles[i];
        pi.soundVel = ca;
        pi.pressure = factor * (std::pow(pi.rho / params.rho0, params.gamma) - 1.0);
    }
}

// --- Orquestador principal ---
void computePressure(std::vector<Particle>& particles,
                     int nBoundary,
                     int nParticles,
                     int step,
                     double g,
                     double fluidHeight,
                     EOSType eos)
{
    if (eos == EOSType::Monaghan)
        computeMonaghanPressure(particles, nBoundary, nParticles, step);
    else
        computeKorzaniPressure(particles, nBoundary, nParticles, step, g, fluidHeight);
}
