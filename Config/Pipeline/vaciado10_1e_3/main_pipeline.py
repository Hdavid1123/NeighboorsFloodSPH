import sys
from pathlib import Path

CONFIG_ROOT = Path(__file__).resolve().parents[2]
if str(CONFIG_ROOT) not in sys.path:
    sys.path.insert(0, str(CONFIG_ROOT))

from Pipeline.vaciado10_1e_3.create_folders import create_project_structure
from Pipeline.vaciado10_1e_3.create_jsons import create_fluid_json, create_boundary_json
from Pipeline.vaciado10_1e_3.generate_ics import generate_ics
from Pipeline.vaciado10_1e_3.visualize import show_ics_and_confirm

def run_pipeline():

    base = input("Ruta base: ")
    name = input("Nombre del proyecto: ")
    paths = create_project_structure(base, name)

    N = int(input("Valor N: "))

    fluid_path = paths["json"] / f"fluid_{N}.json"
    esp = create_fluid_json(N, fluid_path)

    boundary_path = paths["json"] / f"boundary_{N}.json"
    create_boundary_json(esp, boundary_path)

    main_script = input("Ruta a main.py de condiciones inciales: ")

    txt_path = paths["txt"] / f"ics_{N}.txt"
    log_path = paths["txt"] / f"ics_{N}_log.json"

    if not generate_ics(boundary_path, fluid_path, txt_path, log_path, main_script):
        print("Error generando ICS.")
        return

    try:
        particle_size = float(
            input("Tamaño inicial de partícula para visualización [default=6]: ")
            or 6
        )
    except ValueError:
        particle_size = 6

    if not show_ics_and_confirm(txt_path, particle_size):
        print("Cancelado por usuario.")
        for f in [txt_path, log_path, fluid_path, boundary_path]:
            if f.exists():
                f.unlink()
        return

    print("ICS aprobado. Continuar con la simulación...")


if __name__ == "__main__":
    run_pipeline()