#pragma once
#include <vector>
#include <string>
#include "io/particle.h"

// Guarda el estado completo de todas las partículas en un archivo por step
void printState(const std::vector<Particle>& particles, int step,
                const std::string& output_dir);

