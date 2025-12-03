#include <fstream>
#include <iomanip>
#include <iostream>
#include <cmath>
#include <filesystem>
#include "kernel/cubicSplineKernel.h"

double cubicSplineKernel(double r, double h) {
    if (r < 0 || h <= 0) throw std::runtime_error("r>=0 and h>0 required");

    double R = r / h;
    double alpha = 15.0 / (7.0 * M_PI * h * h); 

    if (R >= 0.0 && R < 1.0) {
        return alpha * ((2.0/3.0) - R*R + 0.5*R*R*R);
    } else if (R >= 1.0 && R < 2.0) {
        return alpha * ((1.0/6.0)*(2.0-R)*(2.0-R)*(2.0-R));
    } else {
        return 0.0;
    }
}

// Derivadas direccionales dWx y dWy (solo en 2D por ahora)
std::array<double,2> dCubicSplineKernel(double r, double dx, double dy, double h) {
    if (r <= 0 || h <= 0) return {0.0, 0.0}; // evita división por cero

    double R = r / h;
    double alpha = 15.0 / (7.0 * M_PI * h * h); // normalización 2D
    double factor = 0.0;

    if (R >= 0.0 && R < 1.0) {
        factor = alpha * (-2.0 + 1.5*R) / (h*h);
    } else if (R>= 1.0 && R < 2.0) {
        factor = alpha * (-0.5*(2.0-R)*(2.0-R)) / (h*h*R);
    } else {
        factor = 0.0;
    }

    double dWx = factor * dx;
    double dWy = factor * dy;

    return {dWx, dWy};
}

// Función de prueba del kernel cúbico
void testKernel(const std::string& output_dir) {
    double h = 1.0;  // <--- h fijo para análisis

    // Crear directorio de resultados
    std::filesystem::create_directories(output_dir);

    // Construir la ruta completa del archivo
    std::string output_file = output_dir + "/kernel_test.output";
    std::ofstream fKernelTest(output_file);
    if (!fKernelTest.is_open()) {
        throw std::runtime_error("No se pudo abrir " + output_file);
    }

    fKernelTest << std::setw(16) << "r"
                << std::setw(16) << "W"
                << std::setw(16) << "dWx"
                << std::setw(16) << "dWy" << "\n";

    for (double r = -3.0; r < 3.0; r += 0.1) {
        double rr = std::fabs(r);
        double w = cubicSplineKernel(rr, h);
        std::array<double,2> dw = dCubicSplineKernel(rr, r, 0.0, h);

        fKernelTest << std::setw(16) << std::fixed << std::setprecision(10) << r
                    << std::setw(16) << w
                    << std::setw(16) << dw[0]
                    << std::setw(16) << dw[1]
                    << "\n";
    }

    fKernelTest.close();
    std::cout << "Prueba del kernel completada.\n";
    std::cout << "Resultados guardados en: " << output_file << "\n";
}