import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def plot_ics(archivo_txt, particle_size=6, xlim=None, ylim=None):
    df = pd.read_csv(archivo_txt, sep=" ")

    df_fluid = df[df["type"] == 0]
    df_boundary = df[df["type"] == 1]
    df_hole = df[df["type"] == -1]

    fig, ax = plt.subplots(figsize=(6, 8))

    ax.scatter(df_boundary["posx"], df_boundary["posy"],
               s=particle_size, c="black", label="Frontera (type=1)")
    ax.scatter(df_fluid["posx"], df_fluid["posy"],
               s=particle_size, c="blue", label="Fluido (type=0)")
    ax.scatter(df_hole["posx"], df_hole["posy"],
               s=particle_size, c="red", label="Agujero (type=-1)")

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Distribución de partículas iniciales")
    ax.legend()
    ax.grid(True)

    # Aspect ratio sin ignorar tus límites
    ax.set_aspect("equal", adjustable="datalim")

    # Aplicar límites
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    # Notación científica
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.show()
