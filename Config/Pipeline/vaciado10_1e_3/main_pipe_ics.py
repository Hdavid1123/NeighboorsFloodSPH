import sys
from pathlib import Path

CONFIG_ROOT = Path(__file__).resolve().parents[3]
if str(CONFIG_ROOT) not in sys.path:
    sys.path.insert(0, str(CONFIG_ROOT))

from Config.Pipeline.vaciado10_1e_3.create_folders import create_project_structure
from Config.Pipeline.vaciado10_1e_3.create_jsons import create_fluid_json, create_boundary_json
from Config.Pipeline.vaciado10_1e_3.generate_ics import generate_ics
from Config.Pipeline.vaciado10_1e_3.visualize import show_ics_and_confirm


def files_for_N_exist(paths, N):
    files = [
        paths["json"] / f"fluid_{N}.json",
        paths["json"] / f"boundary_{N}.json",
        paths["txt"]  / f"ics_{N}.txt",
        paths["txt"]  / f"ics_{N}_log.json",
    ]
    return any(f.exists() for f in files)


def run_ics_pipeline():

    DEFAULT_BASE = CONFIG_ROOT / "Output"

    base_input = input(
        f"Ruta base del proyecto [default={DEFAULT_BASE}]: "
    ).strip()

    base = Path(base_input) if base_input else DEFAULT_BASE

    if not base.exists():
        print(f"[ERROR] La ruta base no existe: {base}")
        return

    DEFAULT_NAME = "EstAnalysisRhoNtree"

    name = input(
        f"Nombre del proyecto [default={DEFAULT_NAME}]: "
    ).strip() or DEFAULT_NAME

    # Crear estructura base
    paths = create_project_structure(base, name)
    project_dir = paths["root"]

    # Leer N (UNA sola vez)
    try:
        N = int(input("Valor N (Nx = Ny): "))
    except ValueError:
        print("[ERROR] N debe ser un entero.")
        return

    # Crear carpeta N_xxx
    N_dir = project_dir / f"N_{N}"
    N_dir.mkdir(parents=True, exist_ok=True)

    # Crear subcarpetas dentro de N_xxx
    paths_N = {
        "json": N_dir / "json",
        "txt":  N_dir / "txt",
    }

    for p in paths_N.values():
        p.mkdir(parents=True, exist_ok=True)

    # Chequeo de archivos existentes (por N)
    if files_for_N_exist(paths_N, N):
        print(f"\nYa existen archivos para N = {N}")
        op = input("¿Deseas sobrescribirlos? (Y/N): ").strip().upper()
        if op != "Y":
            print("Ejecución cancelada.")
            return

    # Crear JSONs e ICS
    fluid_path = paths_N["json"] / f"fluid_{N}.json"
    esp = create_fluid_json(N, fluid_path)

    boundary_path = paths_N["json"] / f"boundary_{N}.json"
    create_boundary_json(esp, boundary_path)

    txt_path = paths_N["txt"] / f"ics_{N}.txt"
    log_path = paths_N["txt"] / f"ics_{N}_log.json"

    if not generate_ics(boundary_path, fluid_path, txt_path, log_path):
        print("Error generando ICS.")
        return

    # Visualización
    try:
        particle_size = float(
            input("Tamaño inicial de partícula para visualización [default=6]: ")
            or 6
        )
    except ValueError:
        particle_size = 6

    if not show_ics_and_confirm(txt_path, particle_size):
        print("Cancelado por usuario. Eliminando archivos de este N...")
        for f in [txt_path, log_path, fluid_path, boundary_path]:
            if f.exists():
                f.unlink()
        return

    print("ICS aprobado. Continuar con la simulación...")

    return txt_path, project_dir, N_dir


if __name__ == "__main__":
    run_ics_pipeline()
