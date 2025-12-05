import json
import shutil
from pathlib import Path

def create_ics_configs(
    N_values,
    fluid_json_template: Path,
    boundary_json_template: Path,
    output_root: Path
):
    """
    Crea carpetas para cada N en N_values, modifica el JSON fluid y copia el JSON boundary.

    Params:
        N_values (iterable): lista de valores de N (nx, ny).
        fluid_json_template (Path): ruta al JSON base de fluid (vaciado10_45x45_fluid.json)
        boundary_json_template (Path): ruta al JSON base de boundary (vaciado10_45x45_boundary.json)
        output_root (Path): carpeta donde crear exp_N
    """
    
    output_root.mkdir(parents=True, exist_ok=True)

    created_folders = []

    # Cargar JSON base del fluid para modificarlo más adelante
    with open(fluid_json_template, "r") as f:
        fluid_base = json.load(f)

    for N in N_values:
        N = int(N)

        # Carpeta destino: exp_N5, exp_N10, ...
        exp_dir = output_root / f"exp_N{N}"
        exp_dir.mkdir(exist_ok=True)
        created_folders.append(exp_dir)

        # === 1) Modificar JSON fluid ===
        fluid_cfg = fluid_base.copy()
        fluid_cfg["nx"] = N
        fluid_cfg["ny"] = N

        fluid_out = exp_dir / f"vaciado10_{N}x{N}_fluid.json"
        with open(fluid_out, "w") as f_out:
            json.dump(fluid_cfg, f_out, indent=2)

        # === 2) Copiar JSON boundary sin modificar ===
        boundary_out = exp_dir / f"vaciado10_{N}x{N}_boundary.json"
        shutil.copy(boundary_json_template, boundary_out)

        print(f"✔ Config creada: {exp_dir}")

    return created_folders
