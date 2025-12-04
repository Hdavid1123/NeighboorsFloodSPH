import subprocess
from pathlib import Path
import pandas as pd

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



def clean_walls_ics(
    ruta_ics: Path,
    nombre_salida: str,
    project_root: Path,
    subcarpeta_salida="Output/init_cond"
):
    """
    Limpia un archivo ICS eliminando partículas con type == -1
    y escribe un nuevo archivo con formateo exacto.

    Parámetros:
    ----------
    ruta_ics : Path
        Ruta completa al archivo ICS original.
    nombre_salida : str
        Nombre del archivo ICS limpio a generar.
    project_root : Path
        Ruta raíz del proyecto donde se generará la carpeta Output/init_cond.
    subcarpeta_salida : str
        Carpeta relativa dentro del proyecto donde guardar el archivo.
    
    Retorna:
    --------
    Path : ruta completa al archivo generado.
    """

    ruta_ics = Path(ruta_ics)
    ruta_salida = project_root / subcarpeta_salida
    ruta_salida.mkdir(parents=True, exist_ok=True)

    ruta_final = ruta_salida / nombre_salida

    print(f"Leyendo archivo ICS: {ruta_ics}")
    df = pd.read_csv(str(ruta_ics), delim_whitespace=True)

    df_limpio = df[df["type"] != -1].copy()

    print(f"Partículas originales: {len(df)}")
    print(f"Partículas eliminadas (type == -1): {len(df) - len(df_limpio)}")
    print(f"Partículas restantes: {len(df_limpio)}")

    if (df_limpio["type"] == -1).any():
        print("❌ ERROR: aún quedan partículas con type == -1")
        return None
    else:
        print("✔ Verificación OK: no quedan partículas de tipo -1")

    print(f"💾 Guardando archivo limpio en: {ruta_final}")

    with open(ruta_final, "w") as f:
        
        # Cabecera
        f.write("id posx posy velx vely accelx accely rho mass pressure h internalE type\n")
        
        # Filas formateadas
        for _, row in df_limpio.iterrows():
            f.write(
                f"{int(row['id'])} "
                f"{row['posx']:.10f} "
                f"{row['posy']:.10f} "
                f"{row['velx']:.10f} "
                f"{row['vely']:.10f} "
                f"{row['accelx']:.10f} "
                f"{row['accely']:.10f} "
                f"{row['rho']:.10f} "
                f"{row['mass']:.10f} "
                f"{row['pressure']:.10f} "
                f"{row['h']:.10f} "
                f"{row['internalE']:.10f} "
                f"{int(row['type'])}\n"
            )

    print("🎉 Archivo ICS limpio generado correctamente.")
    return ruta_final
