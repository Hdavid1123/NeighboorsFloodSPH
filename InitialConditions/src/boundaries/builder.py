import json
from pathlib import Path
from src.domains.quadrilateral import Quadrilateral
from src.domains.composite import CompositeDomain
from src.boundaries.particleizer import BoundaryParticleizer

class BoundaryBuilder:
    def __init__(self, param_file: Path | str):
        """
        Inicializa el constructor de fronteras leyendo un archivo JSON.
        El parámetro 'param_file' es obligatorio.
        """
        self.param_path = Path(param_file).resolve()

        if not self.param_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de parámetros: {self.param_path}")

        with open(self.param_path, "r", encoding="utf-8") as f:
            self.params = json.load(f)
    
    # -------------------------------------------
    def build_geometry(self,
                       spacing: float = None) -> CompositeDomain:
        """
        Construye y devuelve un CompositeDomain con las geometrías
        definidas en el archivo de parámetros.
        """
        comp = CompositeDomain()

        # === 1. Cuadriláteros ===
        for i, quad_cfg in enumerate(self.params.get("quadrilateros", [])):
            cfg = quad_cfg.copy()
            if spacing is not None:
                cfg["spacing"] = spacing

            quad = Quadrilateral(
                d1=cfg["d1"],
                d2=cfg["d2"],
                d3=cfg["d3"],
                a1=cfg["a1"],
                a2=cfg["a2"],
                a3=cfg["a3"],
                spacing=cfg.get("spacing", 1),
                holes=[{**h} for h in cfg.get("agujeros", [])]
            )
            comp.add_domain(quad)

            # Registrar automáticamente los puntos A, B, C, D
            labels = ["A", "B", "C", "D"]
            for lbl, coords in zip(labels, quad.vertices()):
                name = f"{lbl}{i}" if len(self.params.get("quadrilateros", [])) > 1 else lbl
                comp.register_point(name, coords)

        # === 2. Conexiones ===
        for conn in self.params.get("connections", []):
            comp.add_connection(
                conn["p1"],
                conn["p2"],
                spacing=conn.get("spacing", 1.0)
            )
            
        # === 3. Líneas libres ===
        for fl in self.params.get("free_lines", []):
            comp.add_free_line(
                from_point=fl["from"],
                to_point=fl.get("to"),
                length=fl.get("length"),
                angle=fl.get("angle"),
                spacing=fl.get("spacing", 1.0),
                name=fl.get("name"),
            )
        comp.print_points()  # Imprime los puntos registrados para verificación
        return comp

    # --------------------------------------------------
    def build(self,
              spacing: float = None,
              particle_type: int = 1,
              h: float = None,
              dx: float = None,
              dy: float = None,
              ref_mass: float = None,
              ref_rho: float = None) -> list[dict]:
        """
        Construye la geometría de frontera y genera la lista de partículas SPH.
        Si se proporciona 'reference_mass', todas las partículas de frontera
        usarán ese mismo valor de masa (útil para igualarlas con las del fluido).
        """
        comp = self.build_geometry(spacing=spacing)
        rho0 = ref_rho or 1000.0  # Densidad típica del agua

        # Determinar espaciado base
        if spacing is None:
            if self.params.get("quadrilateros"):
                spacing = self.params["quadrilateros"][0].get("spacing", 1.0)
            elif self.params.get("free_lines"):
                spacing = self.params["free_lines"][0].get("spacing", 1.0)
            elif self.params.get("connections"):
                spacing = self.params["connections"][0].get("spacing", 1.0)
            else:
                spacing = 1.0

        # Si dx o dy no se pasan, se derivan del spacing
        dx = dx or spacing
        dy = dy or dx
        h = h or 1.1 * dx
        
        # Si se pasa una masa de referencia, usarla; si no, calcularla
        mass = ref_mass or (rho0 * dx * dy)

        particleizer = BoundaryParticleizer()
        all_particles = []
        
        for domain in comp.domains:
            # Cuadriláteros
            if isinstance(domain, Quadrilateral):
                normal_segments = domain.segments()
                particles_normal = particleizer.generate(
                    segments=normal_segments,
                    ptype=particle_type,
                    h=h,
                    dx=dx,
                    dy=dy,
                    mass=mass,
                    rho=rho0,
                )
                all_particles.extend(particles_normal)
                
            # Agujeros (si existen)
                if hasattr(domain, "_segments_holes"):
                    hole_segments = list(domain._segments_holes.values())
                    if hole_segments:
                        particles_hole = particleizer.generate(
                            segments=hole_segments,
                            ptype=-1,  # tipo especial para agujeros
                            h=h,
                            dx=dx,
                            dy=dy,
                            mass=mass,
                            rho=rho0,
                        )
                        all_particles.extend(particles_hole)
            
            # Otros tipos de dominios (líneas, conexiones, etc.)
            else:
                segments = domain.segments()
                particles = particleizer.generate(
                    segments=segments,
                    ptype=particle_type,
                    h=h,
                    dx=dx,
                    dy=dy,
                    mass=mass,
                    rho=rho0,
                )
                all_particles.extend(particles)
                
        extra_segments = comp.segments()
        if extra_segments:
            extra_particles = particleizer.generate(
                segments=extra_segments,
                ptype=particle_type,
                h=h,
                dx=dx,
                dy=dy,
                mass=mass,
                rho=rho0,
            )
            all_particles.extend(extra_particles)
        
        return all_particles