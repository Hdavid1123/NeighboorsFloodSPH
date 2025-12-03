#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <unordered_set>
#include <cmath>
#include "io/particle.h"

// -----------------------------
// Función de verificación
// -----------------------------
void verifyParticles(const std::vector<Particle>& particles) {
    if (particles.empty()) {
        std::cout << "No hay partículas para verificar.\n";
        return;
    }

    std::unordered_set<int> seenIDs;
    
    for (const auto& p : particles) {
        if (p.h <= 0.0) {
            std::cerr << "Error: h negativa o cero para partícula ID=" << p.id << "\n";
        }
        if (!std::isfinite(p.pos[0]) || !std::isfinite(p.pos[1])) {
            std::cerr << "Error: posición inválida para partícula ID=" << p.id << "\n";
        }
        /* if (p.type != Particle::Fluid && p.type != Particle::Boundary) {
            std::cerr << "Error: tipo desconocido para partícula ID=" << p.id << "\n";
        } */
        if (!seenIDs.insert(p.id).second) {
            std::cerr << "[verifyParticles] Advertencia: ID duplicado detectado: " << p.id << "\n";
        }
    }

    auto itBoundary = std::find_if(particles.begin(), particles.end(),
                                   [](const Particle& p){ return p.type == Particle::Boundary; });
    if (itBoundary != particles.end()) {
        std::cout << "Primera partícula de frontera:\n"
                  << "  ID: " << itBoundary->id
                  << " pos: (" << itBoundary->pos[0] << ", " << itBoundary->pos[1] << ")\n"
                  << "  tipo: " << (itBoundary->type == Particle::Boundary ? "Frontera" : "Fluido") 
                  << "\n h: " << itBoundary->h << "\n";
    }

    auto itFluid = std::find_if(particles.rbegin(), particles.rend(),
                                [](const Particle& p){ return p.type == Particle::Fluid; });
    if (itFluid != particles.rend()) {
        std::cout << "Última partícula de fluido:\n"
                  << "  ID: " << itFluid->id
                  << " pos: (" << itFluid->pos[0] << ", " << itFluid->pos[1] << ")\n"
                  << "  tipo: " << (itFluid->type == Particle::Boundary ? "Frontera" : "Fluido") 
                  << "\n h: " << itFluid->h << "\n";
    }
}

// -----------------------------
// Función principal de lectura
// -----------------------------
std::vector<Particle> readParticlesFromFile(const std::string& filename){
    
    std::cout << "Dentro de función de lectura de partículas\n";
    
    std::ifstream infile(filename);
    if (!infile) {
        throw std::runtime_error("No se pudo abrir el archivo: " + filename);
    }

    std::string line;
    std::getline(infile, line); // Saltar cabecera

    std::vector<Particle> particles;
    particles.reserve(1000); // reserva inicial (ajustable)

    bool printedFluidSep = false;
    bool printedBoundarySep = false;

    while (std::getline(infile, line)) {
        if (line.empty()) continue;

        std::istringstream iss(line);

        Particle p;
        double posx, posy, velx, vely, accelx, accely, rho, mass, pressure, h, internalE;
        int typeInt;

        if (!(iss >> p.id >> posx >> posy >> velx >> vely >> accelx >> accely
                  >> rho >> mass >> pressure >> h >> internalE >> typeInt)) {
            std::cerr << "Error en formato de línea: " << line << "\n";
            continue;
        }

        p.pos = {posx, posy};
        p.vel = {velx, vely};
        p.accel = {accelx, accely};
        p.rho = rho;
        p.mass = mass;
        p.pressure = pressure;
        p.h = h;
        p.soundVel = 0.0;
        p.internalE = internalE;
        p.dinternalE = 0.0;
        p.type = static_cast<Particle::Type>(typeInt);
        
        if (p.type == Particle::Fluid && !printedFluidSep) {
            std::cout << "Separación dx/dy de fluido: " << 0 << ", " << 0 << "\n"; // Si quieres, calcular real
            printedFluidSep = true;
        }
        if (p.type == Particle::Boundary && !printedBoundarySep) {
            std::cout << "Separación dx/dy de frontera: " << 0 << ", " << 0 << "\n";
            printedBoundarySep = true;
        }

        particles.push_back(p);
    }

    verifyParticles(particles);
    return particles;
}
