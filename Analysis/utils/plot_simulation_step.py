import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def plot_step_resaltado(
    archivo_txt,
    df_resaltado=None,
    ids_resaltados=None,
    color_resaltado="orange",
    label_resaltado="Partículas resaltadas",
    particle_size=6,
    title=None,
    xlim=None,
    ylim=None
):
    """
    Grafica partículas SPH y permite resaltar un subconjunto
    cambiando su color (sin dibujarlas dos veces).
    """

    # Leer datos
    df = pd.read_csv(archivo_txt, sep=r"\s+")

    # Máscara global de resaltado (sobre df completo)
    mask_resaltado = pd.Series(False, index=df.index)

    if df_resaltado is not None:
        mask_resaltado.loc[df_resaltado.index] = True
    elif ids_resaltados is not None:
        mask_resaltado = df["id"].isin(ids_resaltados)

    fig, ax = plt.subplots(figsize=(6, 8))

    # ---------- FRONTERA (type = 1) ----------
    df_b = df[df["type"] == 1]
    mask_b = mask_resaltado.loc[df_b.index]

    df_b_norm = df_b[~mask_b]
    df_b_res  = df_b[mask_b]

    ax.scatter(df_b_norm["posx"], df_b_norm["posy"],
               s=particle_size, c="black", label="Frontera (type=1)")

    if not df_b_res.empty:
        ax.scatter(df_b_res["posx"], df_b_res["posy"],
                   s=particle_size, c=color_resaltado,
                   label=label_resaltado)

    # ---------- FLUIDO (type = 0) ----------
    df_f = df[df["type"] == 0]
    mask_f = mask_resaltado.loc[df_f.index]

    df_f_norm = df_f[~mask_f]
    df_f_res  = df_f[mask_f]

    ax.scatter(df_f_norm["posx"], df_f_norm["posy"],
               s=particle_size, c="blue", label="Fluido (type=0)")

    if not df_f_res.empty:
        ax.scatter(df_f_res["posx"], df_f_res["posy"],
                   s=particle_size, c=color_resaltado)

    # ---------- AGUJERO (type = -1) ----------
    df_h = df[df["type"] == -1]
    mask_h = mask_resaltado.loc[df_h.index]

    df_h_norm = df_h[~mask_h]
    df_h_res  = df_h[mask_h]

    ax.scatter(df_h_norm["posx"], df_h_norm["posy"],
               s=particle_size, c="red", label="Agujero (type=-1)")

    if not df_h_res.empty:
        ax.scatter(df_h_res["posx"], df_h_res["posy"],
                   s=particle_size, c=color_resaltado)

    # ---------- FORMATO ----------
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    ax.set_title(title if title is not None else "Distribución de partículas")

    ax.legend()
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
