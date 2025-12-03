import subprocess
from pathlib import Path
import time

def run_single_simulation(
    experiment_dir: Path,
    sim_executable: Path,
    timeout_seconds: int = 6000,
    project_root: Path = None
):
    """
    Ejecuta una sola simulación ubicada en experiment_dir.
    Se espera que dentro exista 'params.json'.

    Parámetros:
        experiment_dir (Path): Carpeta que contiene params.json.
        sim_executable (Path): Ruta al ejecutable de simulación.
        timeout_seconds (int): Tiempo máximo permitido.
        project_root (Path): Carpeta donde se ejecuta la simulación.
    """

    # --- 1. Definir directorio raíz del proyecto ---
    if project_root is None:
        project_root = Path().resolve().parent

    param_file = experiment_dir / "params.json"

    if not param_file.exists():
        print(f"❌ No se encontró params.json en {experiment_dir}")
        return

    run_name = experiment_dir.name
    print(f"\n🚀 Ejecutando simulación: {run_name}\n")

    # Rutas para logs
    stdout_path = experiment_dir / "stdout.txt"
    stderr_path = experiment_dir / "stderr.txt"

    err_log = open(stderr_path, "w")

    cmd = [str(sim_executable), str(param_file)]
    start_time = time.time()

    # Función interna para manejar el timeout
    def run_with_timeout(proc, timeout):
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise

    try:
        # --- 2. Ejecutar simulación ---
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        # --- 3. Leer stdout en tiempo real ---
        with open(stdout_path, "w") as out_file:
            for line in iter(proc.stdout.readline, ""):
                print(line, end="")
                out_file.write(line)

        # --- 4. Leer stderr al final ---
        stderr_output = proc.stderr.read()
        if stderr_output:
            print("\n[STDERR]\n" + stderr_output)
            err_log.write(stderr_output)

        # --- 5. Timeout ---
        run_with_timeout(proc, timeout_seconds)

        elapsed = time.time() - start_time

        if proc.returncode == 0:
            print(f"\n  ✅ Simulación completada ({elapsed:.1f} s)\n")
        else:
            print(f"\n  ⚠️ Terminó con código {proc.returncode} ({elapsed:.1f} s)\n")

    except subprocess.TimeoutExpired:
        print(f"\n  ❌ TIMEOUT: simulación detenida tras {timeout_seconds}s")
        err_log.write(f"\n[ERROR] Timeout a los {timeout_seconds}s\n")

    finally:
        err_log.close()

import subprocess
from pathlib import Path
import time


def run_all_simulations(
    experiment_root: Path,
    sim_executable: Path,
    timeout_seconds: int = 6000,
    pattern: str = "experiment_B*/params.json",
    project_root: Path = None
):
    """
    Ejecuta todas las simulaciones encontradas dentro de experiment_root,
    leyendo stdout en tiempo real, guardando logs y manejando timeout.

    Parámetros:
        experiment_root (Path): Carpeta donde están los experimentos.
        sim_executable (Path): Ruta al ejecutable de simulación.
        timeout_seconds (int): Tiempo máximo de ejecución.
        pattern (str): Patrón glob para detectar params.json.
        project_root (Path): Directorio donde se corre el ejecutable.
                             Si no se da, usa el directorio del proyecto.
    """

    # --- 1. Resolver project_root automáticamente ---
    if project_root is None:
        project_root = Path().resolve().parent

    # --- 2. Encontrar .json de simulación ---
    param_files = sorted(experiment_root.glob(pattern))

    print(f"\n🔍 Se encontraron {len(param_files)} simulaciones para ejecutar.\n")
    if not param_files:
        return

    def run_with_timeout(proc, timeout):
        """Maneja el timeout de Popen."""
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise

    # --- 3. Ejecutar todas las simulaciones ---
    for param_file in param_files:
        run_dir = param_file.parent
        run_name = run_dir.name

        print(f"\n🚀 Ejecutando {run_name} ...\n")

        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"

        err_log = open(stderr_path, "w")

        cmd = [str(sim_executable), str(param_file)]
        start_time = time.time()

        try:
            # Iniciar proceso
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=project_root
            )

            # ---- Lectura de STDOUT en tiempo real ----
            with open(stdout_path, "w") as out_file:
                for line in iter(proc.stdout.readline, ""):
                    print(line, end="")      # Mostrar en consola
                    out_file.write(line)     # Guardar en archivo

            # ---- Lectura final de STDERR ----
            stderr_output = proc.stderr.read()
            if stderr_output:
                print("\n[STDERR]\n" + stderr_output)
                err_log.write(stderr_output)

            # ---- Manejo del timeout ----
            run_with_timeout(proc, timeout_seconds)
            elapsed = time.time() - start_time

            if proc.returncode == 0:
                print(f"\n  ✅ Finalizado correctamente ({elapsed:.1f} s)\n")
            else:
                print(f"\n  ⚠️ Código de salida {proc.returncode} ({elapsed:.1f} s)\n")

        except subprocess.TimeoutExpired:
            print(f"\n  ❌ TIMEOUT tras {timeout_seconds}s — simulación detenida")
            err_log.write(f"\n[ERROR] Timeout tras {timeout_seconds}s\n")

        finally:
            err_log.close()
