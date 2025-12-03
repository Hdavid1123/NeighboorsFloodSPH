# test_base.py

from src.domains.base import BoundaryShape
import pytest

def test_boundaryshape_is_abstract():
    """Verifica que no se pueda instanciar directamente."""
    with pytest.raises(TypeError):
        BoundaryShape()
