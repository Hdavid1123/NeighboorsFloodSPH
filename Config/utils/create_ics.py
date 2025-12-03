import subprocess
from pathlib import Path

def create_ics_txt(
    boundary: str,
    fluid: str,
    output_name: str,
    output_log: str,
    project_root: Path = None
):
    """
    Ejecuta main.py con los parámetros indicados.
    
    Parámetros:
        boundary (str): Nombre del archivo JSON de frontera.
        fluid (str): Nombre del archivo JSON de fluido.
        output_name (str): Nombre del archivo de salida (ej: "sim.txt").
        output_log (str): Nombre del archivo de resumen (ej: "log.json").
        project_root (Path, opcional): Ruta raíz del proyecto.
                                        Si no se especifica, se detecta automáticamente.
    """

    # --- 1. Detectar PROJECT_ROOT automáticamente ---
    if project_root is None:
        cwd = Path.cwd()
        project_root = cwd.parents[0] if cwd.name == "Config" else cwd

    # --- 2. Rutas principales ---
    main_script = project_root / "InitialConditions" / "main.py"
    boundary_path = project_root / "Config" / "parameters" / boundary
    fluid_path = project_root / "Config" / "parameters" / fluid
    output_dir = project_root / "Output" / "init_cond"

    # --- 3. Mostrar configuración ---
    print("[INFO] Ejecutando main.py con los siguientes parámetros:")
    print(f"  • Script principal:        {main_script}")
    print(f"  • Archivo de frontera:     {boundary_path}")
    print(f"  • Archivo de fluido:       {fluid_path}")
    print(f"  • Carpeta de salida:       {output_dir}")
    print(f"  • Nombre archivo salida:   {output_name}")
    print(f"  • Nombre archivo resumen:  {output_log}")

    # --- 4. Ejecutar main.py ---
    result = subprocess.run([
        "python", str(main_script),
        "export",
        "--boundary", str(boundary_path),
        "--fluid", str(fluid_path),
        "--output_dir", str(output_dir),
        "--output_file", output_name,
        "--output_logname", output_log
    ], capture_output=True, text=True)

    # --- 5. Mostrar resultados ---
    print("\n" + "="*60)
    if result.returncode == 0:
        print("[✓] Ejecución completada correctamente.")
        print(f"Archivo generado: {output_dir / output_name}")
    else:
        print("[✗] Error durante la ejecución.")
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
    print("="*60 + "\n")

    return result.returncode  # Para saber si todo salió bien
