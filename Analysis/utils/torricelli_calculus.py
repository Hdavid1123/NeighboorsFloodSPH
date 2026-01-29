import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def analizar_altura_fluido(
    archivo_txt,
    delta_rel=0.01,
    particle_size=6,
    y_fondo=-0.5e-3,
    xlim=None,
    ylim=None,
    title=None,
    mostrar_plot=True
):
    """
    Calcula la altura del fluido y grafica la verificación geométrica.
    """

    df = pd.read_csv(archivo_txt, sep=r"\s+")

    df_fluid = df[df["type"] == 0]
    df_boundary = df[df["type"] == 1]
    df_hole = df[df["type"] == -1]

    y_max = df_fluid["posy"].max()
    
    delta_y = delta_rel * y_max

    df_superficie = df_fluid[df_fluid["posy"] >= (y_max - delta_y)]
    y_superficie_prom = df_superficie["posy"].mean()

    # 4. Altura del fluido
    altura_fluido = y_superficie_prom - y_fondo

    # 5. Gráfica de verificación
    if mostrar_plot:
        fig, ax = plt.subplots(figsize=(6, 8))

        ax.scatter(
            df_boundary["posx"], df_boundary["posy"],
            s=particle_size, c="black", label="Frontera (type=1)"
        )
        ax.scatter(
            df_fluid["posx"], df_fluid["posy"],
            s=particle_size, c="blue", label="Fluido (type=0)"
        )
        ax.scatter(
            df_hole["posx"], df_hole["posy"],
            s=particle_size, c="red", label="Agujero (type=-1)"
        )

        # Líneas de referencia
        ax.axhline(
            y_superficie_prom,
            color="green",
            linestyle="--",
            linewidth=2,
            label="Superficie promedio"
        )
        ax.axhline(
            y_fondo,
            color="purple",
            linestyle="--",
            linewidth=2,
            label="Fondo"
        )

        # Labels y título (MISMO ESTILO que plot_ics)
        ax.set_xlabel("x [m]", fontsize=15)
        ax.set_ylabel("y [m]", fontsize=15)

        ax.set_title(
            title if title is not None
            else "Altura del fluido – verificación geométrica",
            fontsize=16
        )

        # Ticks, leyenda y grilla
        ax.tick_params(axis="both", which="major", labelsize=13)
        ax.legend(fontsize=12)
        ax.grid(True)

        ax.set_aspect("equal", adjustable="datalim")

        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))

        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

        plt.show()


    return {
        "y_fondo": y_fondo,
        "y_sup_prom": y_superficie_prom,
        "altura_fluido": altura_fluido,
        "n_particulas_superficie": len(df_superficie)
    }
  

# ------------------------------------------------
# CALCULO DE LA VELOCIDAD INCIAL DE LAS PARTÍCULAS
# ------------------------------------------------

from pathlib import Path
import pandas as pd
import re

def extraer_trayectorias_particulas(
    path_states,
    df_particulas_inicial,
    pattern="state_*.txt"
):
    """
    Extrae la trayectoria de un conjunto de partículas SPH
    identificadas por su ID a lo largo de múltiples pasos temporales.

    Parámetros
    ----------
    path_states : str o Path
        Directorio donde están los archivos state_****.txt
    df_particulas_inicial : DataFrame
        DataFrame con las partículas a seguir (debe contener columna 'id')
    pattern : str
        Patrón de archivos (por defecto 'state_*.txt')

    Retorna
    -------
    DataFrame
        Columnas: step, id, posx, posy
    """
    path_states = Path(path_states)
    ids_seguidos = df_particulas_inicial["id"].unique()
    files = sorted(
        path_states.glob(pattern),
        key=lambda f: int(re.search(r"\d+", f.stem).group())
    )

    trayectorias = []

    for file in files:
        step = int(re.search(r"\d+", file.stem).group())

        df = pd.read_csv(file, sep=r"\s+")
        df_sel = df[df["id"].isin(ids_seguidos)]

        if df_sel.empty:
            continue

        trayectorias.append(
            df_sel[["id", "posx", "posy"]].assign(step=step)
        )

    if not trayectorias:
        return pd.DataFrame(columns=["step", "id", "posx", "posy"])

    return pd.concat(trayectorias, ignore_index=True)

import numpy as np

def cortar_trayectorias_en_minimo_y(
    df_trayectorias,
    tol=1e-6,
    min_steps=3
):
    """
    Corta cada trayectoria cuando y deja de decrecer
    (primer mínimo físico).

    Parámetros
    ----------
    df_trayectorias : DataFrame
        Columnas: step, id, posx, posy
    tol : float
        Tolerancia para ignorar ruido numérico
    min_steps : int
        Número mínimo de puntos antes de permitir el corte

    Retorna
    -------
    DataFrame
        Trayectorias cortadas
    """

    trayectorias_cortadas = []

    for pid, df_p in df_trayectorias.groupby("id"):
        df_p = df_p.sort_values("step").reset_index(drop=True)

        y = df_p["posy"].values
        dy = np.diff(y)

        # Buscar primer índice donde y empieza a crecer
        corte = None
        for i in range(min_steps - 1, len(dy)):
            if dy[i] > tol:
                corte = i + 1
                break

        if corte is None:
            trayectorias_cortadas.append(df_p)
        else:
            trayectorias_cortadas.append(df_p.iloc[:corte + 1])

    return pd.concat(trayectorias_cortadas, ignore_index=True)
