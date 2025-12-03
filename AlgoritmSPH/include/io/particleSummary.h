#pragma once
#include <vector>
#include "particle.h"   // Asegúrate de incluir la definición de Particle

struct ParticleStats {
    int nParticles;
    int nFluid;
    int nBoundary;
    double fluidWidth;
    double fluidHeight;
    double boundaryWidth;
    double boundaryHeight;
};

// Calcula las estadísticas sin imprimir
ParticleStats computeParticleSummary(const std::vector<Particle>& particles);

// Imprime el resumen en consola
void printParticleSummary(const std::vector<Particle>& particles);