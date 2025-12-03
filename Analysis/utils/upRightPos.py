import numpy as np

def find_part_up_right(file_path, n_altas=1, n_derechas=1):
    """
    Devuelve dos diccionarios:
      - altas:     {id: y}  → partículas con mayor altura (posy)
      - derechas:  {id: x}  → partículas más a la derecha (posx)
    """

    data = np.loadtxt(str(file_path), skiprows=1)

    # Extraer columnas del archivo
    ids   = data[:,0]
    posx  = data[:,1]
    posy  = data[:,2]
    types = data[:,12]

    # Filtrar partículas con type == 0
    mask = types == 0
    ids_0  = ids[mask]
    posx_0 = posx[mask]
    posy_0 = posy[mask]

    # --- Partículas más altas (máximos de posy) ---
    idx_sorted_y = np.argsort(posy_0)[::-1]      # ordenar posy descendente
    top_idx = idx_sorted_y[:n_altas]

    altas = {
        int(ids_0[i]): float(posy_0[i])          # SOLO Y
        for i in top_idx
    }

    # --- Partículas más a la derecha (máximos de posx) ---
    idx_sorted_x = np.argsort(posx_0)[::-1]      # ordenar posx descendente
    right_idx = idx_sorted_x[:n_derechas]

    derechas = {
        int(ids_0[i]): float(posx_0[i])          # SOLO X
        for i in right_idx
    }

    return altas, derechas
