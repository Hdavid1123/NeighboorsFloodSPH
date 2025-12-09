import json
from pathlib import Path
    
def create_fluid_json(N, output_path: Path):
    y_inf, y_sup = -4.5e-4, 4.5e-4
    heigh = y_sup - y_inf 
    esp = heigh / N

    data = {
        "nx": N,
        "ny": N,
        "flag_N": "True",
        "espaciado": esp,
        "vertices": {
            "inf-izq":  [5e-5,  -4.5e-4],
            "inf-der":  [9.5e-4, -4.5e-4],
            "sup-der":  [9.5e-4,  4.5e-4],
            "sup-izq":  [5e-5,   4.5e-4]
        }
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return esp


def create_boundary_json(esp_fluid, output_path: Path):
    spacing = esp_fluid / 2

    data = {
        "quadrilateros": [
            {
                "d1": 1e-3, "d2": 1e-3, "d3": 1e-3,
                "a1": -90, "a2": 0, "a3": 90,
                "spacing": spacing,
                "agujeros": [
                    {"lado": "DA", "tam": 1e-3, "offset": 0},
                    {"lado": "CD", "tam": 1e-4, "offset": 1.25e-5}
                ]
            }
        ],
        "free_lines": [
            {"from": "C", "length": 1e-3, "angle": -90, "spacing": spacing, "name": "E"},
            {"from": "E", "length": 1e-3, "angle": 0,   "spacing": spacing, "name": "F"},
            {"from": "F", "length": 1e-3, "angle": 90,  "spacing": spacing, "name": "G"}
        ]
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
