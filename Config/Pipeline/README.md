# Pipeline de Generación de Condiciones Iniciales (ICS)

Pipeline interactivo para generar, visualizar y validar condiciones iniciales (ICS) de simulaciones SPH a partir de geometrías definidas en archivos JSON.

---

## 📁 Estructura del Proyecto (Config)

```
Config/
├── Pipeline/
│   └── vaciado10_1e_3/
│       ├── main_pipeline.py      # Orquestador del pipeline
│       ├── create_folders.py     # Creación de carpetas
│       ├── create_jsons.py       # JSON de fluido y frontera
│       ├── generate_ics.py       # Generación del archivo ICS (.txt)
│       ├── visualize.py          # Visualización y confirmación
│       └── __init__.py
│
├── utils/
│   ├── create_ics.py             # Wrapper InitialConditions/main.py
│   ├── plot_ics.py               # Graficador de partículas
│   ├── create_simJSON.py
│   ├── create_gnuplot.py
│   └── run_sim.py
│
├── parameters/
└── Output/
```

---

## 🚀 Ejecución

Desde el directorio `Pipeline/vaciado10_1e_3`:

```bash
python main_pipeline.py
```
---

## 🔄 Flujo del Pipeline

1. Crear estructura del proyecto  
2. Generar JSON de fluido y frontera  
3. Generar archivo ICS (.txt)  
4. Visualizar geometría  
5. Aceptar o cancelar  
6. (Futuro) Ejecutar simulación y post-procesado  
---

## 🧩 Etapas Principales

### 1. Creación de carpetas

Crea la estructura:
```
<proyecto>/
└── init_cond/
    ├── config_geometryJSON/
    └── txt_geometry/
```

```python
create_project_structure(base_path, project_name)
```
---

### 2. Generación de JSON

- Fluido:
  - nx = ny = N
  - espaciado = distancia / N
- Frontera:
  - spacing = espaciado_fluido / 2

```python
esp = create_fluid_json(N, fluid_json_path)
create_boundary_json(esp, boundary_json_path)
```

---

### 3. Generación del archivo ICS

Ejecuta InitialConditions/main.py vía wrapper.

Archivos generados:
```
ics_N.txt
ics_N_log.json
```

```python
generate_ics(boundary_json, fluid_json, txt_path, log_path, main_script)
```
---

### 4. Visualización interactiva

- type = 0 → Fluido  
- type = 1 → Frontera  
- type = -1 → Agujeros  
- Tamaño de partícula ajustable

```python
show_ics_and_confirm(txt_file)
```
---

### 5. Confirmación

- Y → continuar  
- N → eliminar archivos generados (no carpetas)

```python
txt_path.unlink()
log_path.unlink()
fluid_path.unlink()
boundary_path.unlink()
```
---

## ✅ Principios de Diseño

- Modularidad  
- Interacción explícita  
- Validación visual obligatoria  
- Fácil extensión (simulación, gnuplot, batch)