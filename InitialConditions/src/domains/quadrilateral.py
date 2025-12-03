import numpy as np
from typing import List
from domains.base import BoundaryShape, Point, Segment
from domains.utils import construir_trapecio, agregar_agujero

class Quadrilateral(BoundaryShape):
    def __init__(self,
                 d1: float, d2: float, d3: float,
                 a1: float, a2: float, a3: float,
                 spacing: float = 1.0,
                 holes: List[dict] = None):
        """
        Construye un cuadrilátero normalizado con muestreo de lados,
        opcionalmente le aplica agujeros.

        Parámetros:
        - d1, d2, d3: longitudes de los lados consecutivos
        - a1, a2, a3: ángulos (en grados)
        - spacing: separación entre puntos muestreados
        - holes: lista de dicts con {'lado': 'AB', 'tam': float, 'offset': float}
        """
        # Construir trapecio escalado
        lados, vertices = construir_trapecio(
            d1, d2, d3,
            a1, a2, a3,
            spacing
        )

        # Guardamos vértices con etiquetas A, B, C, D
        self._vertices: dict[str, np.ndarray] = vertices

        # Guardamos segmentos (cada lado tiene sus puntos muestreados)
        self._segments: dict[str, np.ndarray] = lados
        self._resolution: float = spacing

        # Agregar agujeros en lados si existen
        if holes:
            extremos = {
                "AB": ("A", "B"),
                "BC": ("B", "C"),
                "CD": ("C", "D"),
                "DA": ("D", "A")
            }
            self._segments_holes = {}  # almacenar agujeros por lado

            for h in holes:
                side = h["lado"]
                if side in extremos:
                    v1, v2 = extremos[side]
                    P1, P2 = vertices[v1], vertices[v2]

                    # obtener puntos normales y de agujero
                    border, hole = agregar_agujero(
                        P1, P2,
                        longitud=h["tam"],
                        offset=h["offset"],
                        spacing=spacing
                    )

                    self._segments[side] = border       # borde normal
                    self._segments_holes[side] = hole   # agujero (type = -1)

    # -------------------------
    # Métodos públicos
    # -------------------------
    def segments(self) -> List[Segment]:
        """Devuelve solo los segmentos de borde normales"""
        return list(self._segments.values())

    def segments_with_holes(self) -> List[Segment]:
        """Devuelve tanto los segmentos normales como los de agujero"""
        segs = list(self._segments.values())
        if hasattr(self, "_segments_holes"):
            segs += list(self._segments_holes.values())
        return segs

    def vertices(self) -> List[Point]:
        return [tuple(self._vertices[k]) for k in ["A", "B", "C", "D"]]

    def vertex_dict(self) -> dict[str, Point]:
        return {k: tuple(v) for k, v in self._vertices.items()}