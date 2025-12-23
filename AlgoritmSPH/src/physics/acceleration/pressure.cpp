#include <vector>
#include <cmath>
#include <iostream>
#include "physics/acceleration/pressure.h"
#include "io/particle.h"

// --- Variables globales de configuración ---
static AdamiParams g_AdamiParams;
static KorzaniParams g_korzaniParams;

// --- Funciones setter ---
void setAdamiParams(double B, double c, double rho0, double gamma) {
    g_AdamiParams = {B, c, rho0, gamma};
}

void setKorzaniParams(double ca_factor, double rho0, double gamma) {
    g_korzaniParams = {ca_factor, rho0, gamma};
}

// --- Implementación de EoS de Tait con frontera de Adami (2012) ---
// p = B * ((rho / rho0)^gamma - 1)
// Hay que incluir el valor de la gravedad para la presión
static void computeAdamiPressure(std::vector<Particle>& particles,
                                    int nBoundary,
                                    int nParticles,
                                    double g)
{
    const auto& params = g_AdamiParams;

    // 1. Presión en partículas de fluido (EOS de Tait)
    for (int i = nBoundary; i < nParticles; ++i) {
        Particle& pi = particles[i];

        pi.soundVel = params.c;
        pi.pressure = params.B *
             (std::pow(pi.rho / params.rho0, params.gamma) - 1.0);
    }

    // 2. Presión en las fronteras, extrapolada del fluido
    for (int i = 0; i < nBoundary; ++i) {
        Particle& pi = particles[i];

        pi.soundVel = params.c;
        pi.rho = params.rho0;

        double pSum = 0.0;
        double wSum = 0.0;
        double hydroSum = 0.0;

        for (size_t k = 0; k < pi.neighbors.size(); k++){
            int j = pi.neighbors[k];
            Particle& pj = particles[j];

            if (pj.type != Particle::Fluid) continue; // Solo los vecinos de fluido aportan

            double W = pi.W[k];
            double ry = pi.pos[1] - pj.pos[1]; //Solo hay aceleración externa en y

            pSum += pj.pressure * W;
            hydroSum += pj.rho * g * ry * W;
            wSum += W;
        }
        
        pi.pressure = (wSum > 0.0) ? (pSum + hydroSum) / wSum : 0.0;
    
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
    if (eos == EOSType::Adami)
        computeAdamiPressure(particles, nBoundary, nParticles, g);
    else
        computeKorzaniPressure(particles, nBoundary, nParticles,
                               step, g, fluidHeight);
}
