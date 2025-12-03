# src/export/export_particles.py

from pathlib import Path
import json
from datetime import datetime
from src.fluid.builder import FluidBuilder
from src.boundaries.builder import BoundaryBuilder


def export_all_particles(
    boundary_param_file: str | Path,
    fluid_param_file: str | Path,
    output_dir: str | Path,
    output_filename: str = "initial_state.txt",
    output_logname: str = "initial_state_summary.json",
    include_boundary: bool = True,
    include_fluid: bool = True,
):
    """
    Genera y exporta todas las partículas (fluido + frontera) en formato unificado
    y crea un archivo JSON con el resumen de parámetros y geometría.

    Args:
        boundary_param_file: ruta al archivo JSON con las condiciones de frontera.
        fluid_param_file: ruta al archivo JSON con la región del fluido.
        output_dir: carpeta donde se guardará el archivo de salida.
        output_filename: nombre del archivo principal (TXT).
        output_logname: nombre del archivo resumen (JSON).
        include_boundary: si True, incluye partículas de frontera.
        include_fluid: si True, incluye partículas de fluido.
    """

    # --- Verificación y creación del directorio de salida ---
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    summary_path = output_dir / output_logname

    all_particles = []
    fluid_particles = []
    boundary_particles = []

    # ---------------------------------------------------------
    # 1. Construir fluido (primero, para obtener masa base)
    if include_fluid:
        print("[INFO] Generando partículas de fluido...")
        f_builder = FluidBuilder(config_path=fluid_param_file)
        fluid_particles = f_builder.build()
        all_particles.extend(fluid_particles)
        print(f"[✓] Fluido: {len(fluid_particles)} partículas")

    # Obtener masa y parámetros de referencia del fluido
    if fluid_particles:
        fluid_mass = fluid_particles[0]["mass"]
        fluid_rho = fluid_particles[0]["rho"]
        fluid_h = fluid_particles[0]["h"]
    else:
        fluid_mass = None
        fluid_rho = 1000.0
        fluid_h = None

    # ---------------------------------------------------------
    # 2. Construir frontera (usando misma masa que el fluido)
    if include_boundary:
        print("[INFO] Generando partículas de frontera...")
        b_builder = BoundaryBuilder(param_file=boundary_param_file)

        boundary_particles = b_builder.build(
            spacing=None,
            h=fluid_h,
            dx=None,
            dy=None,
            particle_type=1,
            ref_mass=fluid_mass,
            ref_rho=fluid_rho
        )

        all_particles = boundary_particles + fluid_particles
        print(f"[✓] Frontera: {len(boundary_particles)} partículas")

    # ---------------------------------------------------------
    # 3. Reasignar IDs globales
    for i, p in enumerate(all_particles):
        p["id"] = i

    # ---------------------------------------------------------
    # 4. Exportar archivo principal de partículas
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            "id posx posy velx vely accelx accely "
            "rho mass pressure h internalE type\n"
        )
        for p in all_particles:
            x, y = p["pos"]
            vx, vy = p["vel"]
            ax, ay = p["accel"]
            internalE = 0.0
            f.write(
                f"{p['id']} "
                f"{x:.10f} {y:.10f} "
                f"{vx:.10f} {vy:.10f} "
                f"{ax:.10f} {ay:.10f} "
                f"{p['rho']:.10f} "
                f"{p['mass']:.10f} "
                f"{p['pressure']:.10f} "
                f"{p['h']:.10f} "
                f"{internalE:.10f} "
                f"{p['type']}\n"
            )

    # ---------------------------------------------------------
    # 5. Calcular dimensiones del dominio total
    xs_all = [p["pos"][0] for p in all_particles]
    ys_all = [p["pos"][1] for p in all_particles]
    xmin_all, xmax_all = min(xs_all), max(xs_all)
    ymin_all, ymax_all = min(ys_all), max(ys_all)
    Lx_all, Ly_all = xmax_all - xmin_all, ymax_all - ymin_all

    # ---------------------------------------------------------
    # 6. Calcular dimensiones solo del fluido
    if fluid_particles:
        xs_f = [p["pos"][0] for p in fluid_particles]
        ys_f = [p["pos"][1] for p in fluid_particles]
        xmin_f, xmax_f = min(xs_f), max(xs_f)
        ymin_f, ymax_f = min(ys_f), max(ys_f)
        Lx_f, Ly_f = xmax_f - xmin_f, ymax_f - ymin_f
    else:
        xmin_f = xmax_f = ymin_f = ymax_f = Lx_f = Ly_f = None

    # ---------------------------------------------------------
    # 7. Crear resumen JSON
    summary_data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "output_file": str(output_path),
        "nParticles": len(all_particles),
        "nFluid": len(fluid_particles),
        "nBoundaries": len(boundary_particles),

        "bounds_total": {
            "Lx": Lx_all,
            "Ly": Ly_all,
            "xmin": xmin_all,
            "xmax": xmax_all,
            "ymin": ymin_all,
            "ymax": ymax_all,
        },

        "bounds_fluid": {
            "Lx": Lx_f,
            "Ly": Ly_f,
            "xmin": xmin_f,
            "xmax": xmax_f,
            "ymin": ymin_f,
            "ymax": ymax_f,
        },

        "fluid_mass": fluid_mass,
        "fluid_density": fluid_rho,
        "h": fluid_h,
        "include_fluid": include_fluid,
        "include_boundary": include_boundary,
        "fluid_param_file": str(fluid_param_file),
        "boundary_param_file": str(boundary_param_file),
    }

    with open(summary_path, "w", encoding="utf-8") as js:
        json.dump(summary_data, js, indent=4)

    # ---------------------------------------------------------
    print(f"[✓] Archivo de partículas exportado: {output_path}")
    print(f"[✓] Resumen JSON generado: {summary_path}")
    print(f"[INFO] Total partículas exportadas: {len(all_particles)}")

    return all_particles
