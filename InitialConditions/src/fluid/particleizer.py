# src/fluid/particleizer.py
import numpy as np
from typing import List, Dict, Any
from src.core.base_particleizer import BaseParticleizer


class FluidParticleizer(BaseParticleizer):
    """
    Genera partículas de fluido con formato estándar.
    """

    def generate(self,
                 points: np.ndarray,
                 espaciado: float,
                 ptype: int = 0,
                 h: float | None = None,
                 velocity: tuple[float, float] = (0.0, 0.0)) -> List[Dict[str, Any]]:

        dx = dy = espaciado
        h = h or 1.1 * dx
        mass = self.rho0 * dx * dy

        particles: List[Dict[str, Any]] = []
        for i, (x, y) in enumerate(points):
            particles.append({
                "id": i,
                "pos": [float(x), float(y)],
                "vel": [float(velocity[0]), float(velocity[1])],
                "accel": [0.0, 0.0],
                "rho": self.rho0,
                "mass": mass,
                "pressure": 0.0,
                "h": h,
                "type": ptype
            })
        return particles
