# test_quadrilateral.py

import numpy as np
from src.domains.quadrilateral import Quadrilateral

def test_quadrilateral_basico():
    q = Quadrilateral(4, 3, 2, 0, 45, -45, spacing=1.0)
    vertices = q.vertex_dict()
    assert set(vertices.keys()) == {"A", "B", "C", "D"}
    # Los segmentos deben tener 4 lados
    segs = q.segments()
    assert len(segs) == 4
    # Cada lado debe tener al menos 2 puntos
    assert all(len(s) >= 2 for s in segs)

def test_quadrilateral_con_agujero():
    q = Quadrilateral(
        4, 3, 2, 0, 45, -45,
        spacing=1.0,
        holes=[{"lado": "AB", "tam": 1.0, "offset": 1.0}]
    )
    segs = q.segments()
    # Lado AB debe tener menos puntos que sin agujero
    seg_largo = np.linalg.norm(q._vertices["B"] - q._vertices["A"])
    puntos_sin_agujero = int(np.ceil(seg_largo / q._resolution))
    puntos_con_agujero = len(q._segments["AB"])
    assert puntos_con_agujero < puntos_sin_agujero
