import os

def generar_script_gnuplot(ruta_archivo_base,
                           lim=3000,
                           retardo=0.001,
                           nombre_salida="plot_animacion.gp",
                           ruta_salida=None):

    # Leer archivo base
    with open(ruta_archivo_base, "r") as f_in:
        lineas = f_in.readlines()

    # Saltar encabezado (línea 0)
    datos = [linea.strip().split() for linea in lineas[1:] if linea.strip()]
    
    # Extraer tipos (última columna)
    tipos = [int(linea[-1]) for linea in datos]

    grupos = []
    inicio = 0
    tipo_actual = tipos[0]

    for i, t in enumerate(tipos):
        if t != tipo_actual:
            grupos.append((tipo_actual, inicio, i-1))
            inicio = i
            tipo_actual = t

    # Agregar el último grupo
    grupos.append((tipo_actual, inicio, len(tipos)-1))

    # Colores por tipo
    colores = {
        1: "black",
        0: "blue",
        -1: "red"
    }

    plot_lines = []
    primera = True

    for idx, (tipo, ini, fin) in enumerate(grupos):
        color = colores.get(tipo, "gray")
        prefix = 'plot file ' if primera else '     "" '

        # Si NO es el último grupo → agregar ",\"
        if idx < len(grupos) - 1:
            plot_lines.append(
                f'{prefix}every ::{ini}::{fin} u 2:3 w p ps 1 pt 7 lc rgb "{color}" not,\\'
            )
        else:
            # Último bloque (sin coma invertida)
            plot_lines.append(
                f'{prefix}every ::{ini}::{fin} u 2:3 w p ps 1 pt 7 lc rgb "{color}" not'
            )

        primera = False

    bloque_plot = "\n  ".join(plot_lines)

    carpeta = os.path.dirname(ruta_archivo_base)
    carpeta_padre = os.path.dirname(carpeta)

    contenido = f"""lim = {lim}
retardo = {retardo}

set terminal qt size 800,800 enhanced font 'Verdana,10'

do for [i=0:lim]{{
  titulo = sprintf("paso = %.4d - tiempo = %.5f", i, i*5e-5)
  set title titulo
  file = sprintf("{carpeta}/state_%.4d.txt", i)
  {bloque_plot}
  pause retardo
}}"""

    if ruta_salida is None:
        ruta_final = os.path.join(carpeta_padre, nombre_salida)
    else:
        os.makedirs(ruta_salida, exist_ok=True)
        ruta_final = os.path.join(ruta_salida, nombre_salida)
        
    with open(ruta_final, "w") as f_out:
        f_out.write(contenido)

    # Mensaje de confirmación
    print(f"✅ Script Gnuplot generado correctamente: {ruta_final}")
    print("📊 Rangos consecutivos detectados por tipo:")
    for tipo, ini, fin in grupos:
        print(f"  Tipo {tipo}: líneas {ini}–{fin} ({fin - ini + 1} partículas)")

# Ejemplo de uso:
# generar_script_gnuplot("Output/experiments_B/experiment_B2.069138/Output/state_0000.txt", lim=3000, retardo=0.001)
