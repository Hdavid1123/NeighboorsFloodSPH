# test_composite.py

import numpy as np
import pytest
from src.domains.composite import CompositeDomain
from src.domains.quadrilateral import Quadrilateral

def test_add_domain_y_segments():
    c = CompositeDomain()
    q = Quadrilateral(4, 3, 2, 0, 45, -45)
    c.add_domain(q)
    segs = c.segments()
    assert len(segs) >= 4  # por el cuadrilátero

def test_register_y_resolve_point():
    c = CompositeDomain()
    c.register_point("A", [1, 2])
    assert np.allclose(c.resolve_point("A"), [1, 2])
    with pytest.raises(ValueError):
        c.resolve_point("B")  # no registrado

def test_add_connection_con_nombres():
    c = CompositeDomain()
    c.register_point("P1", [0, 0])
    c.register_point("P2", [3, 4])  # distancia 5
    c.add_connection("P1", "P2", spacing=1.0)
    assert len(c.connections) == 1
    seg = c.connections[0]
    assert np.allclose(seg[0], [0, 0])
    assert np.allclose(seg[-1], [3, 4])

def test_add_free_line_por_longitud_y_angulo():
    c = CompositeDomain()
    c.register_point("O", [0, 0])
    name = c.add_free_line("O", length=10, angle=0, spacing=1.0)
    assert name in c.named_points
    p2 = c.named_points[name]
    assert np.allclose(p2, [10, 0])

def test_add_free_line_con_to_point():
    c = CompositeDomain()
    c.register_point("O", [0, 0])
    c.register_point("P", [0, 5])
    c.add_free_line("O", to_point="P", spacing=1.0)
    assert len(c.connections) == 1
    seg = c.connections[0]
    assert np.allclose(seg[-1], [0, 5])
