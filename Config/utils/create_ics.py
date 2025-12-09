import subprocess
from pathlib import Path
import pandas as pd

def create_ics_txt(
    boundary_path: str,
    fluid_path: str,
    output_path: str,
    output_log_path: str,
    main_script_path: str
):
    """
    Ejecuta main.py con rutas absolutas.
    
    Parámetros:
        boundary_path (str): Ruta absoluta del JSON de frontera.
        fluid_path (str): Ruta absoluta del JSON de fluido.
        output_path (str): Ruta absoluta del archivo .txt de salida.
        output_log_path (str): Ruta absoluta del archivo de log.
        main_script_path (str): Ruta absoluta del archivo main.py.
    """

    boundary_path = Path(boundary_path)
    fluid_path = Path(fluid_path)
    output_path = Path(output_path)
    output_log_path = Path(output_log_path)
    main_script_path = Path(main_script_path)

    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Ejecutando main.py con rutas absolutas:")
    print(f"  main.py:      {main_script_path}")
    print(f"  boundary:     {boundary_path}")
    print(f"  fluid:        {fluid_path}")
    print(f"  output txt:   {output_path}")
    print(f"  output log:   {output_log_path}")

    result = subprocess.run([
        "python", str(main_script_path),
        "export",
        "--boundary", str(boundary_path),
        "--fluid", str(fluid_path),
        "--output_dir", str(output_dir),
        "--output_file", output_path.name,
        "--output_logname", output_log_path.name
    ], capture_output=True, text=True)

    print("\n" + "="*60)
    if result.returncode == 0:
        print("[✓] Ejecución completada correctamente.")
    else:
        print("[✗] Error durante la ejecución.")
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
    print("="*60 + "\n")

    return result.returncode



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
