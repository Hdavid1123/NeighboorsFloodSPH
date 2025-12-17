import json
from pathlib import Path
from typing import Union

def rescale_boundary_from_file(
    json_path: Union[str, Path],
    factor: int
) -> dict:
    """
    Carga una geometría de frontera desde un archivo JSON y reescala
    parámetros geométricos específicos.

    Args:
        json_path: Ruta al archivo .json
        factor: Factor entero de reescalamiento

    Returns:
        dict: Geometría reescalada
    """

    SCALE_KEYS = {"d1", "d2", "d3", "tam", "offset", "spacing", "length"}

    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {json_path}")

    if factor <= 0:
        raise ValueError("El factor de escala debe ser positivo")

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    def recursive_scale(obj):
        if isinstance(obj, dict):
            return {
                k: (v * factor if k in SCALE_KEYS and isinstance(v, (int, float))
                    else recursive_scale(v))
                for k, v in obj.items()
            }

        elif isinstance(obj, list):
            return [recursive_scale(item) for item in obj]

        else:
            return obj

    return recursive_scale(data)


def rescale_fluid_from_file(
    json_path: Union[str, Path],
    factor: int
) -> dict:
    """
    Reescala completamente la geometría del fluido usando
    el mismo factor que la frontera sólida.
    """

    json_path = Path(json_path)

    if factor <= 0:
        raise ValueError("El factor debe ser positivo")

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Reescala espaciado
    data["espaciado"] *= factor

    # Reescala vértices
    for name, coords in data["vertices"].items():
        data["vertices"][name] = [
            coords[0] * factor,
            coords[1] * factor
        ]

    return data

def rescale_simulation_geometry(
    solid_geometry_path: Union[str, Path],
    fluid_geometry_path: Union[str, Path],
    factor: int,
    output_dir: Union[str, Path] = "scaled"
) -> tuple[dict, dict]:
    """
    Reescala de forma consistente la geometría sólida y la del fluido
    usando un único factor de escala.

    Args:
        solid_geometry_path: Ruta al JSON de la geometría sólida
        fluid_geometry_path: Ruta al JSON de la geometría del fluido
        factor: Factor entero de reescalamiento
        output_dir: Directorio donde guardar los JSON reescalados

    Returns:
        (solid_geometry, fluid_geometry)
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Reescalado
    solid_scaled = rescale_boundary_from_file(
        solid_geometry_path,
        factor
    )

    fluid_scaled = rescale_fluid_from_file(
        fluid_geometry_path,
        factor
    )

    # Guardado
    solid_out = output_dir / Path(solid_geometry_path).name
    fluid_out = output_dir / Path(fluid_geometry_path).name

    with solid_out.open("w", encoding="utf-8") as f:
        json.dump(solid_scaled, f, indent=2)

    with fluid_out.open("w", encoding="utf-8") as f:
        json.dump(fluid_scaled, f, indent=2)

    return solid_scaled, fluid_scaled
