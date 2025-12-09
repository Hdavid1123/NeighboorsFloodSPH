import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def plot_ics(archivo_txt, particle_size=6):
    # --- Cargar datos ---
    df = pd.read_csv(archivo_txt, sep=" ")

    # --- Separar por tipo ---
    df_fluid = df[df["type"] == 0]
    df_boundary = df[df["type"] == 1]
    df_hole = df[df["type"] == -1]

    # --- Graficar ---
    plt.figure(figsize=(6, 8))
    plt.scatter(df_boundary["posx"], df_boundary["posy"],
                s=particle_size, c="black", label="Frontera (type=1)")
    plt.scatter(df_fluid["posx"], df_fluid["posy"],
                s=particle_size, c="blue", label="Fluido (type=0)")
    plt.scatter(df_hole["posx"], df_hole["posy"],
                s=particle_size, c="red", label="Agujero (type=-1)")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("Distribución de partículas iniciales")
    plt.legend()
    plt.axis("equal")
    plt.grid(True)

    # --- Notación científica en los ejes ---
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # Mostrar figura
    plt.show()