import numpy as np
import matplotlib.pyplot as plt

def density_mesh_from_file(
    filepath,
    mass,
    Nx=100,
    Ny=100,
    cmap="viridis",
    plot_boundaries=True
):
    """
    Calcula y grafica un campo de densidad en una malla regular a partir
    de un archivo de partículas.

    Parámetros
    ----------
    filepath : str
        Ruta al archivo .txt
    mass : float
        Masa de cada partícula (misma para todas)
    Nx, Ny : int
        Número de celdas en x e y
    cmap : str
        Colormap de matplotlib
    """

    # 1. Leer datos
    data = np.loadtxt(filepath, skiprows=1)

    posx = data[:, 1]
    posy = data[:, 2]
    ptype = data[:, 12]

    # 2. Filtrar partículas
    fluid = (ptype == 0)
    boundary = (ptype != 0)

    x_f = posx[fluid]
    y_f = posy[fluid]

    x_b = posx[boundary]
    y_b = posy[boundary]

    # 3. Definir dominio y malla
    xmin, xmax = x_f.min(), x_f.max()
    ymin, ymax = y_f.min(), y_f.max()

    dx = (xmax - xmin) / Nx
    dy = (ymax - ymin) / Ny
    cell_area = dx * dy

    mass_grid = np.zeros((Ny, Nx))

    # 4. Asignación a celdas
    ix = ((x_f - xmin) / dx).astype(int)
    iy = ((y_f - ymin) / dy).astype(int)

    ix = np.clip(ix, 0, Nx - 1)
    iy = np.clip(iy, 0, Ny - 1)

    for i, j in zip(ix, iy):
        mass_grid[j, i] += mass

    # 5. Densidad
    rho_grid = mass_grid / cell_area

    # 6. Visualización
    plt.figure(figsize=(6, 5))

    plt.imshow(
        rho_grid,
        extent=[xmin, xmax, ymin, ymax],
        origin="lower",
        cmap=cmap
    )

    plt.colorbar(label="Density")

    # Fronteras
    if plot_boundaries:
        plt.scatter(x_b, y_b, s=1, c="black")

    plt.xlabel("x")
    plt.ylabel("y")
    #plt.ylim(-0.06, 0.06)
    plt.title("Density field")
    plt.tight_layout()
    plt.show()

    return rho_grid
