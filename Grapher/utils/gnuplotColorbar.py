import os
import glob

def color_bar_script_gnuplot(
    carpeta,
    variable_color="rho",
    vmin=None,
    vmax=None,
    lim=3000,
    retardo=0.001,
    nombre_salida="plot_animacion.gp"
):
    """
    Genera un script .gp con paleta tipo 'turbo' válida para gnuplot.
    La paleta se genera con N stops en valores absolutos entre cmin y cmax.
    """

    # -------------------------
    # 1) Mapear nombre -> columna
    # -------------------------
    columnas = {
        "id": 1,
        "posx": 2,
        "posy": 3,
        "velx": 4,
        "vely": 5,
        "accelx": 6,
        "accely": 7,
        "rho": 8,
        "densidad": 8,
        "mass": 9,
        "pressure": 10,
        "presion": 10,
        "h": 11,
        "internalE": 12,
        "type": 13
    }

    if variable_color not in columnas:
        raise ValueError(f"Propiedad no reconocida: {variable_color}")

    col_gp = columnas[variable_color]

    # -------------------------
    # 2) Listar archivos y detectar rango (si no definido)
    # -------------------------
    archivos = sorted(glob.glob(os.path.join(carpeta, "state_*.txt")))
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos state_XXXX.txt")

    # Si vmin/vmax se pasan, no hace falta leer todo
    if vmin is None or vmax is None:
        valores_min = None
        valores_max = None
        # Lee sólo un subconjunto para acelerar si hay muchos archivos:
        # aquí muestreamos cada k-ésimo archivo hasta 300 archivos muestreados
        MAX_SAMPLE_FILES = 300
        step = max(1, len(archivos) // MAX_SAMPLE_FILES)
        sample_files = archivos[::step]

        for arch in sample_files:
            with open(arch) as f:
                for line in f.readlines()[1:]:
                    if not line.strip():
                        continue
                    cols = line.split()
                    try:
                        val = float(cols[col_gp - 1])
                    except Exception:
                        continue
                    if valores_min is None or val < valores_min:
                        valores_min = val
                    if valores_max is None or val > valores_max:
                        valores_max = val

        cmin = vmin if vmin is not None else valores_min
        cmax = vmax if vmax is not None else valores_max
    else:
        cmin = vmin
        cmax = vmax

    if cmin is None or cmax is None:
        raise RuntimeError("No se pudo determinar cmin/cmax. Pasa vmin/vmax o asegúrate de tener archivos legibles.")

    # -------------------------
    # 3) Palette 'turbo-like' como lista de hex colors
    #    (stops tomados del turbo-like que usamos antes)
    # -------------------------
    turbo_hex = [
        "#30123B", "#32296E", "#1F60A5", "#2C82BC",
        "#57B3A3", "#93CC70", "#C7D71C", "#F1C40F",
        "#FA9827", "#F3604C", "#D03365", "#A01669",
        "#690C50"
    ]
    N = len(turbo_hex)

    # Generar stops en valores absolutos entre cmin y cmax
    stops = []
    for i, hexcol in enumerate(turbo_hex):
        t = i / (N - 1)  # 0..1
        valor = cmin + t * (cmax - cmin)
        # Formato con suficiente precisión (evitar notación exponencial si es posible)
        stops.append((valor, hexcol))

    # Construir cadena válida para gnuplot:
    # set palette defined (v0 "col0", v1 "col1", ... )
    palette_entries = ", ".join(f'{v:.12g} "{col}"' for v, col in stops)
    palette_txt = f"set palette defined ({palette_entries})"

    # -------------------------
    # 4) Leer primer archivo para detectar grupos por tipo
    # -------------------------
    with open(archivos[0], "r") as f_in:
        lineas = f_in.readlines()

    datos = [linea.strip().split() for linea in lineas[1:] if linea.strip()]
    tipos = [int(linea[-1]) for linea in datos]

    grupos = []
    inicio = 0
    tipo_actual = tipos[0]
    for i, t in enumerate(tipos):
        if t != tipo_actual:
            grupos.append((tipo_actual, inicio, i - 1))
            inicio = i
            tipo_actual = t
    grupos.append((tipo_actual, inicio, len(tipos) - 1))

    colores_fijos = {1: "black", -1: "gray"}

    # -------------------------
    # 5) Construir bloque plot
    # -------------------------
    plot_lines = []
    primera = True

    # expr para la columna de color (en gnuplot se usa $N)
    expr_color = f"${col_gp}"

    for idx, (tipo, ini, fin) in enumerate(grupos):
        prefix = "plot file " if primera else '     "" '
        if tipo == 0:
            linea = (f'{prefix}every ::{ini}::{fin} '
                     f'u 2:3:({expr_color}) w p ps 1 pt 7 palette not')
        else:
            color = colores_fijos.get(tipo, "black")
            linea = (f'{prefix}every ::{ini}::{fin} '
                     f'u 2:3 w p ps 1 pt 5 lc rgb "{color}" not')

        if idx < len(grupos) - 1:
            linea += ",\\"
        plot_lines.append(linea)
        primera = False

    bloque_plot = "\n  ".join(plot_lines)

    # -------------------------
    # 6) Escribir script .gp final
    # -------------------------
    contenido = f"""lim = {lim}
retardo = {retardo}

set terminal qt size 800,800 enhanced font 'Verdana,10'
set size square

# Paleta TURBO-like
{palette_txt}
set cbrange [{cmin}:{cmax}]
set colorbox vertical

do for [i=0:lim] {{
  titulo = sprintf("paso = %.4d - tiempo = %.5f", i, i*5e-5)
  set title titulo

  file = sprintf("{carpeta}/state_%.4d.txt", i)

  {bloque_plot}

  pause retardo
}}
"""
    with open(nombre_salida, "w") as f_out:
        f_out.write(contenido)

    print("\nScript Gnuplot generado correctamente:", nombre_salida)
    print(f"\nVariable usada para color: {variable_color} (columna ${col_gp})")
    print(f"\nRango usado para colorbar: [{cmin}, {cmax}]")
    print("\nPaleta: TURBO-like (stops generados en valores absolutos)")
