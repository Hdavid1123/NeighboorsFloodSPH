#pragma once
#include <vector>
#include "io/particle.h"

// --- Tipos de ecuación de estado disponibles ---
enum class EOSType {
    Monaghan,  // Monaghan (1992) - estándar
    Korzani    // Korzani (2014) - adaptado a caída libre
};

// --- Estructuras con parámetros de EoS ---
struct MonaghanParams {
    double B;      // Presión base
    double c;      // Velocidad del sonido
    double rho0;   // Densidad de referencia
    double gamma;  // Exponente
};

struct KorzaniParams {
    double ca_factor; // Factor de velocidad del sonido
    double rho0;      // Densidad de referencia
    double gamma;     // Exponente
};
// --- Funciones para configurar parámetros ---
void setMonaghanParams(double B, double c, double rho0, double gamma);
void setKorzaniParams(double ca_factor, double rho0, double gamma);

// --- Función principal de presión ---
void computePressure(std::vector<Particle>& particles,
                     int nBoundary,     // número de partículas frontera
                     int nParticles,    // total = nBoundary + nFluid
                     int step,          // paso actual de la simulación
                     double g,          // gravedad
                     double fluidHeight,// altura de la columna de fluido
                     EOSType eos);      // modelo EOS a utilizar
