# src/fluid/builder.py

import json
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
from src.fluid.particleizer import FluidParticleizer


class FluidBuilder:
    """
    Construye la nube de partículas de fluido a partir de un archivo JSON
    que define la región fluida y el espaciado de partículas.
    """

    def __init__(self, config_path: Path | str):
        """
        Inicializa el constructor del fluido.
        El parámetro 'config_path' es obligatorio.
        """
        self.config_path = Path(config_path).resolve()

        if not self.config_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.spacing = self.config.get("espaciado", 1.0)
        self.vertices = self._parse_vertices()

    # ---------------------------------------------------------
    def _parse_vertices(self):
        """Convierte los vértices del JSON en arrays numpy."""
        v = self.config["vertices"]
        return {
            "inf-izq": np.array(v["inf-izq"], dtype=float),
            "inf-der": np.array(v["inf-der"], dtype=float),
            "sup-der": np.array(v["sup-der"], dtype=float),
            "sup-izq": np.array(v["sup-izq"], dtype=float),
        }

    # ---------------------------------------------------------
    def _generate_points(self):
        """Genera los puntos 2D dentro del dominio cuadrilátero definido."""
        v = self.vertices
        xs, ys = zip(*v.values())
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        if self.config.get("flag_N", False):
            nx, ny = self.config["nx"], self.config["ny"]
            x_vals = np.linspace(min_x, max_x, nx)
            y_vals = np.linspace(min_y, max_y, ny)
        else:
            spacing = self.spacing
            x_vals = np.arange(min_x, max_x + spacing, spacing)
            y_vals = np.arange(min_y, max_y + spacing, spacing)

        xx, yy = np.meshgrid(x_vals, y_vals)
        return np.vstack((xx.ravel(), yy.ravel())).T

    # ---------------------------------------------------------
    def _filter_overlap(self, points: np.ndarray, border_points: np.ndarray | None):
        """Elimina puntos de fluido demasiado cercanos a las fronteras."""
        if border_points is None or len(border_points) == 0:
            return points

        tree_border = cKDTree(border_points)
        dist, _ = tree_border.query(points, k=1)
        mask = dist > self.spacing / 2
        return points[mask]

    # ---------------------------------------------------------
    def build(self, border_particles: list[dict] | None = None, debug: bool = False) -> list[dict]:
        """
        Construye todas las partículas de fluido, eliminando posibles solapamientos
        con las partículas de frontera si se proveen.
        """
        border_points = None
        if border_particles:
            border_points = np.array([p["pos"] for p in border_particles])

        raw_points = self._generate_points()
        n_inicial = raw_points.shape[0]

        if debug:
            print(f"[DEBUG] Puntos iniciales generados: {n_inicial}")
            y_vals_before = np.unique(np.round(raw_points[:, 1], 6))
            x_vals_before = np.unique(np.round(raw_points[:, 0], 6))

        filtered_points = self._filter_overlap(raw_points, border_points)
        n_final = filtered_points.shape[0]

        if debug:
            print(f"[DEBUG] Puntos después del filtrado: {n_final}")
            y_vals_after = np.unique(np.round(filtered_points[:, 1], 6))
            x_vals_after = np.unique(np.round(filtered_points[:, 0], 6))

            filas_perdidas = sorted(set(y_vals_before) - set(y_vals_after))
            columnas_perdidas = sorted(set(x_vals_before) - set(x_vals_after))

            if filas_perdidas:
                print(f"[DEBUG] Filas eliminadas (y): {filas_perdidas}")
            if columnas_perdidas:
                print(f"[DEBUG] Columnas eliminadas (x): {columnas_perdidas}")

            self.debug_info = {
                "n_inicial": n_inicial,
                "n_final": n_final,
                "filas_perdidas": filas_perdidas,
                "columnas_perdidas": columnas_perdidas,
            }

        # Generar partículas completas
        particleizer = FluidParticleizer()
        particles = particleizer.generate(filtered_points, espaciado=self.spacing)
        return particles

    # ---------------------------------------------------------
    def save_debug_info(self, output_dir: Path | str):
        """Guarda las estadísticas de construcción en un archivo JSON."""
        if not self.debug_info:
            print("[INFO] No hay información de depuración para guardar.")
            return

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "fluid_debug_info.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.debug_info, f, indent=4)

        print(f"[✓] Archivo de depuración guardado en: {output_file}")
