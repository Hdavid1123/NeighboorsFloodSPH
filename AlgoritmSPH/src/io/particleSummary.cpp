#include <limits>
#include <algorithm>
#include <iostream>
#include "io/particleSummary.h" 

// ---------------------------------------------------
// Función para calcular resumen de partículas
// ---------------------------------------------------
ParticleStats computeParticleSummary(const std::vector<Particle>& particles) {
    ParticleStats stats{};
    stats.nParticles = static_cast<int>(particles.size());
    stats.nFluid = 0;
    stats.nBoundary = 0;

    double minXFluid = std::numeric_limits<double>::max();
    double maxXFluid = std::numeric_limits<double>::lowest();
    double minYFluid = std::numeric_limits<double>::max();
    double maxYFluid = std::numeric_limits<double>::lowest();

    double minXBoundary = std::numeric_limits<double>::max();
    double maxXBoundary = std::numeric_limits<double>::lowest();
    double minYBoundary = std::numeric_limits<double>::max();
    double maxYBoundary = std::numeric_limits<double>::lowest();

    for (const auto& p : particles) {
        if (p.type == Particle::Fluid) {
            stats.nFluid++;
            minXFluid = std::min(minXFluid, p.pos[0]);
            maxXFluid = std::max(maxXFluid, p.pos[0]);
            minYFluid = std::min(minYFluid, p.pos[1]);
            maxYFluid = std::max(maxYFluid, p.pos[1]);
        } 
        else if (p.type == Particle::Boundary || p.type == Particle::Hole) {
            stats.nBoundary++;
            minXBoundary = std::min(minXBoundary, p.pos[0]);
            maxXBoundary = std::max(maxXBoundary, p.pos[0]);
            minYBoundary = std::min(minYBoundary, p.pos[1]);
            maxYBoundary = std::max(maxYBoundary, p.pos[1]);
        }
    }

    stats.fluidWidth  = (stats.nFluid > 0)    ? maxXFluid - minXFluid : 0.0;
    stats.fluidHeight = (stats.nFluid > 0)    ? maxYFluid - minYFluid : 0.0;
    stats.boundaryWidth  = (stats.nBoundary > 0) ? maxXBoundary - minXBoundary : 0.0;
    stats.boundaryHeight = (stats.nBoundary > 0) ? maxYBoundary - minYBoundary : 0.0;

    return stats;
}

// ---------------------------------------------------
// Función para imprimir el resumen de partículas
// ---------------------------------------------------
void printParticleSummary(const std::vector<Particle>& particles) {
    ParticleStats stats = computeParticleSummary(particles);

    std::cout << "\n[particleSummary] Número total de partículas: " << stats.nParticles << "\n";
    std::cout << "Fluido: " << stats.nFluid 
              << ", Ancho: " << stats.fluidWidth 
              << ", Altura: " << stats.fluidHeight << "\n";
    std::cout << "Frontera: " << stats.nBoundary 
              << ", Ancho: " << stats.boundaryWidth 
              << ", Altura: " << stats.boundaryHeight << "\n";
}
