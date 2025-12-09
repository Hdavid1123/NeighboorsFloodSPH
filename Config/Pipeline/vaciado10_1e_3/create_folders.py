from pathlib import Path

def create_project_structure(base_path: str, name: str):
    root = Path(base_path) / name
    root.mkdir(parents=True, exist_ok=True)

    paths = {
        "root": root,
        "init": root / "init_cond",
        "json": root / "init_cond" / "config_geometryJSON",
        "txt": root / "init_cond" / "txt_geometry"
    }

    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)

    return paths
