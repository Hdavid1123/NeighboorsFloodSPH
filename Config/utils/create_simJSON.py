# Config/utils/create_simJSON.py
import json
from pathlib import Path


def create_simulation_config(
    experiment_name: str,
    input_file: str,
    base_json: str,
    B: float,
    c: float,
    steps: int,
    neighbor_method: str = None,
    output_tests: str = None,
    project_root: Path = None,
    project_dir: Path = None
):
    """
    Genera params.json dentro de un experimento perteneciente a un proyecto.
    """

    # --- 1. Validaciones ---
    if project_root is None:
        raise ValueError("[ERROR] project_root es obligatorio.")

    if project_dir is None:
        raise ValueError("[ERROR] project_dir es obligatorio.")

    project_root = Path(project_root).resolve()
    project_dir = Path(project_dir).resolve()

    # --- 2. JSON base (SIEMPRE desde el repo) ---
    base_json_path = (
        project_root
        / "Config"
        / "parameters"
        / "simulation"
        / base_json
    )

    if not base_json_path.exists():
        raise FileNotFoundError(
            f"[ERROR] No existe el JSON base: {base_json_path}"
        )

    # --- 3. Carpeta del experimento ---
    experiment_root = project_dir / experiment_name
    experiment_root.mkdir(parents=True, exist_ok=True)

    # --- 4. Leer JSON base ---
    with open(base_json_path, "r") as f:
        base_params = json.load(f)

    params = json.loads(json.dumps(base_params))  # copia profunda

    # --- 5. Modificar parámetros ---
    params["physics"]["eos_params"]["monaghan"]["B"] = float(B)
    params["physics"]["eos_params"]["monaghan"]["c"] = float(c)
    params["integrator"]["n_steps"] = int(steps)

    if neighbor_method is not None:
        params["neighbors"]["search_method"] = str(neighbor_method)

    if output_tests is not None:
        params["kernel"]["output_dir"] = str(output_tests)

    # --- 6. IO ---
    sim_output_dir = experiment_root / "Output"
    sim_output_dir.mkdir(parents=True, exist_ok=True)

    params["io"]["input_file"] = str(input_file)
    params["io"]["output_dir_simulation"] = str(sim_output_dir)

    # --- 7. Guardar params.json ---
    param_file = experiment_root / "params.json"
    with open(param_file, "w") as f:
        json.dump(params, f, indent=2)

    print(f"✅ params.json generado: {param_file.relative_to(project_dir)}")

    return param_file
