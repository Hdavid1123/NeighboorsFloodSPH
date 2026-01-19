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

        ax.scatter(df_boundary["posx"], df_boundary["posy"],
                   s=particle_size, c="black", label="Frontera (type=1)")
        ax.scatter(df_fluid["posx"], df_fluid["posy"],
                   s=particle_size, c="blue", label="Fluido (type=0)")
        ax.scatter(df_hole["posx"], df_hole["posy"],
                   s=particle_size, c="red", label="Agujero (type=-1)")

        # Líneas de referencia
        ax.axhline(y_superficie_prom, color="green", linestyle="--",
                   linewidth=2, label="Superficie promedio")
        ax.axhline(y_fondo, color="purple", linestyle="--",
                   linewidth=2, label="Fondo")

        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")

        if title is not None:
            ax.set_title(title)
        else:
            ax.set_title("Altura del fluido – verificación geométrica")

        ax.legend()
        ax.grid(True)
        ax.set_aspect("equal", adjustable="datalim")

        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))

        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        plt.show()

    return {
        "y_fondo": y_fondo,
        "y_sup_prom": y_superficie_prom,
        "altura_fluido": altura_fluido,
        "n_particulas_superficie": len(df_superficie)
    }
    
  
def calcular_velocidad_salida(
    archivos_txt,
    h,
    dt,
    x_hole=None,
    id_particula=None,
    min_puntos=6
):
    """
    Calcula la velocidad inicial de salida mediante ajuste cuadrático
    y(t) = a t^2 + b t + c
    """

    dfs = []
    for i, archivo in enumerate(archivos_txt):
        df = pd.read_csv(archivo, sep=r"\s+")
        df["step"] = i
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)

    # =========================
    # 2. Determinar x_hole
    # =========================
    if x_hole is None:
        df_hole = df_all[df_all["type"] == -1]
        x_hole = df_hole["posx"].mean()

    # =========================
    # 3. Detectar partículas candidatas
    # =========================
    df_fluido = df_all[df_all["type"] == 0]

    mask_x = (
        (df_fluido["posx"] >= x_hole - 2*h) &
        (df_fluido["posx"] <= x_hole + 2*h)
    )

    df_candidatas = df_fluido[mask_x]

    # =========================
    # 4. Seleccionar partícula
    # =========================
    if id_particula is None:
        # Elegir la que aparece primero en el tiempo
        id_particula = (
            df_candidatas
            .groupby("id")["step"]
            .min()
            .idxmin()
        )

    df_trayectoria = df_candidatas[df_candidatas["id"] == id_particula]

    if len(df_trayectoria) < min_puntos:
        raise ValueError("No hay suficientes puntos para el ajuste.")

    t = df_trayectoria["step"].values * dt
    y = df_trayectoria["posy"].values

    # 6. Ajuste por mínimos cuadrados
    coef = np.polyfit(t, y, 2)
    a, b, c = coef

    g_estimado = 2 * a
    v0 = b
    y0 = c

    return {
        "id_particula": id_particula,
        "v0": v0,
        "g_estimado": g_estimado,
        "y0": y0,
        "coeficientes": coef,
        "t": t,
        "y": y
    }
