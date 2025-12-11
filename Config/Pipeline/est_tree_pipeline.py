# Config/Pipeline/est_tree_pipeline.py
import sys
import csv
import subprocess
import time
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Config.Pipeline.vaciado10_1e_3.main_pipe_ics import run_ics_pipeline
from Config.utils.create_simJSON import create_simulation_config

def logspace_1_4_7():
    mantissas = [1, 4, 7]
    decades = range(-5, 1)
    B = [m * 10**d for d in decades for m in mantissas]
    B.append(10)
    return B

C_VALUES = [1e-3, 1e-5, 1e-4, 1e-2, 1e-1]


def extract_last_step(stdout_text: str):
    matches = re.findall(r"[Ss]tep\s*[:=]?\s*(\d+)", stdout_text)
    return int(matches[-1]) if matches else None

def run_single_simulation(
    experiment_dir: Path,
    sim_executable: Path,
    timeout_seconds: int,
    project_root: Path
):
    param_file = experiment_dir / "params.json"
    stdout_path = experiment_dir / "stdout.txt"
    stderr_path = experiment_dir / "stderr.txt"

    start = time.time()

    proc = subprocess.Popen(
        [str(sim_executable), str(param_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_root
    )

    try:
        out, err = proc.communicate(timeout=timeout_seconds)
        timeout = False
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        timeout = True

    elapsed = time.time() - start

    stdout_path.write_text(out)
    stderr_path.write_text(err)

    last_step = extract_last_step(out)

    if timeout:
        return elapsed, last_step, "TIMEOUT", None

    return elapsed, last_step, "EXIT", proc.returncode

# Barrido B–c + estabilidad (DENTRO de N_dir)
def run_stability_sweep(
    project_dir: Path,      # <- ESTE es N_dir
    input_file: Path,
    sim_executable: Path,
    base_json: str,
    steps: int = 6000,
    timeout_seconds: int = 4000
):
    sweep_root = project_dir / "sweep_B_c"
    sweep_root.mkdir(parents=True, exist_ok=True)

    results = []
    B_values = logspace_1_4_7()

    for c in C_VALUES:

        print("\n" + "=" * 60)
        print(f"🔵 Iniciando barrido para c = {c:.1e}")
        print(f"   Total simulaciones: {len(B_values)}")
        print("=" * 60)

        if input("¿Continuar con este valor de c? (Y/N): ").strip().upper() != "Y":
            continue

        stable_count = 0
        unstable_count = 0
        times = []
        c_start_time = time.time()

        for B in B_values:

            exp_name = f"B_{B:.1e}_c_{c:.1e}"
            print(f"\n🧪 Ejecutando {exp_name}")

            param_file = create_simulation_config(
                experiment_name=exp_name,
                input_file=str(input_file),
                base_json=base_json,
                B=B,
                c=c,
                steps=steps,
                neighbor_method="quadtree",
                project_root=PROJECT_ROOT,   # <- para Config/
                project_dir=project_dir      # <- N_dir
            )

            elapsed, last_step, mode, return_code = run_single_simulation(
                experiment_dir=param_file.parent,
                sim_executable=sim_executable,
                timeout_seconds=timeout_seconds,
                project_root=PROJECT_ROOT
            )

            if last_step is None:
                status = "UNSTABLE_NO_OUTPUT"
            elif last_step >= steps:
                status = "STABLE"
            elif mode == "TIMEOUT":
                status = "UNSTABLE_TIMEOUT"
            elif return_code == -11:
                status = "UNSTABLE_SEGFAULT"
            else:
                status = "UNSTABLE_EARLY_STOP"

            if status == "STABLE":
                stable_count += 1
                times.append(elapsed)
            else:
                unstable_count += 1

            results.append({
                "B": B,
                "c": c,
                "status": status,
                "time": elapsed,
                "last_step": last_step,
                "exit_code": return_code
            })

            print(f"    → {status} | step={last_step} | time={elapsed:.2f}s")

        print("\n" + "-" * 60)
        print(f"Resumen c={c:.1e} | Estables={stable_count} | Inestables={unstable_count}")
        print(f"Tiempo total: {time.time() - c_start_time:.1f}s")
        print("-" * 60)

    return results, sweep_root

def save_results_csv(results, output_dir: Path):
    csv_file = output_dir / "stability_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["B", "c", "status", "time", "last_step", "exit_code"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\n📄 Resultados guardados en {csv_file}")


def main():

    res = run_ics_pipeline()
    if res is None:
        print("[ERROR] Falló la generación de ICS.")
        return

    input_file, project_dir, N_dir = res

    sim_executable = PROJECT_ROOT / "simulacion"

    results, sweep_root = run_stability_sweep(
        project_dir=N_dir,         
        input_file=input_file,
        sim_executable=sim_executable,
        base_json="AndresSimParams.json"
    )

    save_results_csv(results, sweep_root)
    print("\n✅ Pipeline completo finalizado")

if __name__ == "__main__":
    main()
