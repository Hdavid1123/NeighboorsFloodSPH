#include "io/outputParticles.h"
#include <fstream>
#include <iomanip>
#include <sstream>
#include <filesystem>
#include <stdexcept>

void printState(const std::vector<Particle>& particles,
                int step,
                const std::string& output_dir) {
    namespace fs = std::filesystem;

    fs::create_directories(output_dir);

    std::ostringstream filename;
    filename << output_dir << "/state_" 
             << std::setw(4) << std::setfill('0') << step 
             << ".txt";

    std::ofstream out(filename.str());
    if (!out) {
        throw std::runtime_error("No se pudo abrir archivo " +
             filename.str());
    }

    // Configurar formato numérico: 10 cifras decimales, notación fija
    out << std::fixed << std::setprecision(10);

    out << "id posx posy velx vely accelx accely "
        << "rho mass pressure h internalE type\n";

    for (const auto& p : particles) {
        out << p.id << " "
            << p.pos[0] << " "
            << p.pos[1] << " "
            << p.vel[0] << " "
            << p.vel[1] << " "
            << p.accel[0] << " "
            << p.accel[1] << " "
            << p.rho << " "
            << p.mass << " "
            << p.pressure << " "
            << p.h << " "
            << p.internalE << " "
            << p.type << "\n";
    }

    out.close();
}
