import json
from pathlib import Path
import numpy as np

def create_simulation_config(
    experiment_name: str,
    input_file: str,
    base_json: str,
    B: float,
    c: float,
    steps: int,
    neighbor_method: str = None,
    project_root: Path = None
):
    """
    Crea una carpeta de experimento y genera un archivo params.json
    modificando solo los parámetros indicados.

    Parámetros:
        experiment_name (str): Nombre de la carpeta donde se guardará el experimento.
        base_json (str): Nombre del archivo base dentro de Config/parameters/simulation/.
        B (float): Valor del parámetro B a modificar.
        c (float): Valor del parámetro c a modificar.
        steps (int): Número de pasos n_steps.
        project_root (Path, opcional): Si no se especifica, se detecta automáticamente.
    """

    # --- 1. Detectar la ruta raíz del proyecto ---
    if project_root is None:
        project_root = Path().resolve().parent

    base_json_path = project_root / "Config" / "parameters" / "simulation" / base_json

    # --- 2. Carpeta raíz donde se almacenan experimentos ---
    output_root = project_root / "Output"

    experiment_root = output_root / experiment_name
    experiment_root.mkdir(parents=True, exist_ok=True)

    # --- 3. Leer JSON base ---
    with open(base_json_path, "r") as f:
        base_params = json.load(f)

    # --- 4. Copia profunda del JSON ---
    params = json.loads(json.dumps(base_params))

    # --- 5. Modificar parámetros seleccionados ---
    params["physics"]["eos_params"]["monaghan"]["c"] = float(c)
    params["physics"]["eos_params"]["monaghan"]["B"] = float(B)
    params["integrator"]["n_steps"] = int(steps)
    params["neighbors"]["search_method"] = str(neighbor_method)

    # --- 6. Crear carpeta "Output" del experimento ---
    sim_output_dir = experiment_root / "Output"
    sim_output_dir.mkdir(parents=True, exist_ok=True)

    params["io"]["input_file"] = str(input_file)
    params["io"]["output_dir_simulation"] = str(sim_output_dir)

    # --- 7. Guardar params.json ---
    param_file = experiment_root / "params.json"
    with open(param_file, "w") as f:
        json.dump(params, f, indent=2)

    print(f"✅ Archivo generado: {param_file.relative_to(project_root)}")

    return param_file
