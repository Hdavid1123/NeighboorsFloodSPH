# src/core/base_particleizer.py
class BaseParticleizer:
    """
    Clase base para particleizers SPH.
    Sirve solo para compartir parámetros globales como densidad de referencia.
    """
    def __init__(self, rho0: float = 1000.0):
        self.rho0 = rho0
