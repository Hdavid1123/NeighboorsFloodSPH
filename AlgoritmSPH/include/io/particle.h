#pragma once
#include <array>
#include <vector>

struct Particle {
    enum Type {
        Fluid = 0,
        Boundary = 1,
        Hole = -1
    };

    int id;
    std::array<double, 2> pos;     // posición (x,y)
    std::array<double, 2> vel;     // velocidad
    std::array<double, 2> accel;   // aceleración

    double mass;                   // masa
    double rho;                    // densidad actual
    double h;                      // longitud de suavizado
    double pressure;               // presión
    double soundVel;                      // velocidad del sonido local
    double internalE;                      // energía interna
    double dinternalE;                     // variación de energía

    // Los vector serán realocados dinámicamente
    std::vector<int> neighbors;    // índices de vecinos
    std::vector<double> dx;        // diferencia en x con vecinos
    std::vector<double> dy;        // diferencia en y con vecinos
    std::vector<double> r;         // distancia con vecinos
    std::vector<double> W;         // valores del kernel
    std::vector<double> dWx;       // derivadas parciales
    std::vector<double> dWy;

    Type type;                      // tipo de partícula (fluido 0, frontera 1)
};
