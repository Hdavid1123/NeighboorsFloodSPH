#pragma once

#include <vector>
#include <string>
#include "particle.h"

// Función que lee partículas desde un archivo y devuelve un vector de Particle
std::vector<Particle> readParticlesFromFile(const std::string& filename);
