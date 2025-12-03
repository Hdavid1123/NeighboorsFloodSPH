import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as colors

def plot_ics_color(
        archivo_txt,
        prop="pressure",
        vmin=None,
        vmax=None,
        under_color="#4B0082",   # morado
        over_color="#800000",    # vinotinto
        cmap_name="turbo"        # tipo espectro visible
    ):

    if vmin is None or vmax is None:
        raise ValueError("Debes definir vmin y vmax manualmente.")

    # --- Cargar datos ---
    df = pd.read_csv(archivo_txt, sep=" ")

    df_fluid    = df[df["type"] == 0]
    df_boundary = df[df["type"] == 1]
    df_hole     = df[df["type"] == -1]

    prop_values = df_fluid[prop]

    # --- Colormap ---
    cmap_mod = plt.get_cmap(cmap_name).copy()
    cmap_mod.set_under(under_color)
    cmap_mod.set_over(over_color)

    norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=False)

    # --- Crear figura con CONSTRAINED LAYOUT (sin warnings) ---
    fig = plt.figure(figsize=(6, 4), constrained_layout=True)
    ax = fig.add_subplot(111)

    # Partículas frontera
    ax.scatter(df_boundary["posx"], df_boundary["posy"],
               s=6, color="black", label="Frontera (1)")

    # Agujeros
    ax.scatter(df_hole["posx"], df_hole["posy"],
               s=6, color="gray", label="Agujero (-1)")

    # Fluido coloreado
    sc = ax.scatter(df_fluid["posx"], df_fluid["posy"], s=6,
                    c=prop_values, cmap=cmap_mod, norm=norm,
                    label=f"Fluido ({prop})")

    # --- COLORBAR en la derecha (sin add_axes) ---
    cbar = fig.colorbar(sc, ax=ax, orientation="vertical", extend="both")
    cbar.set_label(prop)

    # --- Ajustes de aspecto y estilo ---
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Distribución de partículas iniciales")
    ax.legend(markerscale=3)
    ax.grid(True)

    # Mantener proporciones compactas sin estirar la figura
    ax.set_aspect('equal', adjustable='datalim')

    # Notación científica
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.show()
