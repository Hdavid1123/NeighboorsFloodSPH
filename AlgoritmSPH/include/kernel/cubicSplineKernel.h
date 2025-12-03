#pragma once
#include <array>
#include <stdexcept>
#include <cmath>

// Función de kernel cúbico spline
double cubicSplineKernel(double r, double h);

// Derivada del kernel cúbico spline
std::array<double,2> dCubicSplineKernel(double r, double dx, double dy, double h);

// Función de prueba para verificar la implementación del kernel y su derivada
void testKernel(const std::string& output_dir);


