import sys
import argparse
import subprocess
from pathlib import Path

# --- Asegurar acceso a src ---
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# --- Importar exportador principal ---
from src.core.export import export_all_particles


def run_tests():
    """
    Ejecuta todos los tests con pytest.
    """
    print("[INFO] Ejecutando test suite...")
    test_dir = PROJECT_ROOT / "test"
    result = subprocess.run(["pytest", str(test_dir), "-v"], check=False)
    if result.returncode == 0:
        print("[✓] Todos los tests pasaron correctamente.")
    else:
        print("[✗] Algunos tests fallaron.")
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="CLI principal del generador de condiciones iniciales SPH"
    )

    parser.add_argument(
        "command",
        choices=["export", "test"],
        help="Acción a ejecutar: export o test"
    )

    # --- Parámetros específicos del comando 'export' ---
    parser.add_argument(
        "--boundary",
        type=str,
        required=False,
        help="Ruta al archivo JSON con las condiciones de frontera"
    )
    parser.add_argument(
        "--fluid",
        type=str,
        required=False,
        help="Ruta al archivo JSON con la región del fluido"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=False,
        help="Carpeta donde se guardará el archivo de salida"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="initial_state.txt",
        help="Nombre del archivo de salida principal (por defecto: initial_state.txt)"
    )
    parser.add_argument(
        "--output_logname",
        type=str,
        default="initial_state_summary.json",
        help="Nombre del archivo JSON de resumen (por defecto: initial_state_summary.json)"
    )

    args = parser.parse_args()

    # -------------------------------------------------------------
    # 1️⃣ Comando: export
    if args.command == "export":
        if not args.boundary or not args.fluid or not args.output_dir:
            print(
                "[ERROR] Debes especificar las rutas de los archivos de parámetros y la carpeta de salida.\n"
                "Uso esperado:\n"
                "  python main.py export "
                "--boundary data/parameters/boundary_conditions.json "
                "--fluid data/parameters/fluid_region.json "
                "--output_dir data/output/"
            )
            sys.exit(1)

        export_all_particles(
            boundary_param_file=args.boundary,
            fluid_param_file=args.fluid,
            output_dir=args.output_dir,
            output_filename=args.output_file,
            output_logname=args.output_logname,
        )

        print(f"\n[✓] Export completado con éxito.\n"
              f"  → Archivo de partículas: {args.output_file}\n"
              f"  → Resumen JSON: {args.output_logname}")

    # -------------------------------------------------------------
    # 2️⃣ Comando: test
    elif args.command == "test":
        sys.exit(run_tests())


if __name__ == "__main__":
    main()
