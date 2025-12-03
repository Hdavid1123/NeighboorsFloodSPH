# test_utils.py

import numpy as np
from src.domains.utils import segmentar_lado, construir_trapecio, agregar_agujero

def test_segmentar_lado_spacing():
    P1, P2 = np.array([0, 0]), np.array([10, 0])
    puntos = segmentar_lado(P1, P2, spacing=2)
    # Debe crear al menos 6 puntos (10 / 2 = 5 → +1)
    assert len(puntos) >= 6
    assert np.allclose(puntos[0], P1)
    assert np.allclose(puntos[-1], P2)

def test_construir_trapecio_vertices_y_lados():
    lados, vertices = construir_trapecio(4, 3, 2, 0, 45, -45, spacing=1)
    assert set(vertices.keys()) == {"A", "B", "C", "D"}
    assert all(isinstance(v, np.ndarray) for v in vertices.values())
    # Cada lado tiene al menos 2 puntos
    assert all(len(seg) >= 2 for seg in lados.values())

def test_agregar_agujero_elimina_puntos():
    P1, P2 = np.array([0, 0]), np.array([10, 0])
    sin_agujero = segmentar_lado(P1, P2, spacing=1)
    con_agujero = agregar_agujero(P1, P2, longitud=2, offset=4, spacing=1)
    # Debe tener menos puntos
    assert len(con_agujero) < len(sin_agujero)
    # Los extremos deben mantenerse
    assert np.allclose(con_agujero[0], P1)
    assert np.allclose(con_agujero[-1], P2)
