# src/boundaries/particleizer.py
from typing import List, Dict, Any, Tuple
from src.core.base_particleizer import BaseParticleizer

Point = Tuple[float, float]
Segment = List[Point]


class BoundaryParticleizer(BaseParticleizer):
    """
    Convierte segmentos de frontera en partículas SPH.
    """

    def generate(self,
             segments: List[Segment],
             ptype: int = 1,
             h: float = 0.01,
             dx: float = 0.01,
             dy: float = 0.01,
             mass: float = 1.0,
             rho: float = 1000.0) -> List[Dict[str, Any]]:

        seen: set[Tuple[float, float]] = set()
        particles: List[Dict[str, Any]] = []
        mass = mass or (self.rho0 * dx * dy)

        pid = 0
        for seg in segments:
            for x, y in seg:
                key = (round(x, 8), round(y, 8))
                if key in seen:
                    continue
                seen.add(key)
                particles.append({
                    "id": pid,
                    "pos": [x, y],
                    "vel": [0.0, 0.0],
                    "accel": [0.0, 0.0],
                    "rho": rho,
                    "mass": mass,
                    "pressure": 0.0,
                    "h": h,
                    "type": ptype
                })
                pid += 1
        return particles
