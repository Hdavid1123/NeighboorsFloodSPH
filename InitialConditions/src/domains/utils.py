import numpy as np

def segmentar_lado(P1, P2, spacing: float = 1.0):
    """
    Devuelve un arreglo de puntos entre P1 y P2,
    con espaciado determinado.
    """
    d = np.linalg.norm(P2 - P1)
    n_puntos = max(2, int(np.ceil(d/spacing) + 1))
    return np.linspace(P1, P2, n_puntos)


def construir_trapecio(d1, d2, d3, a1, a2, a3, spacing):
    # Escalar longitudes
    angulos = np.deg2rad([a1, a2, a3])

    A = np.array([0.0, 0.0])
    B = A + d1 * np.array([np.cos(angulos[0]), np.sin(angulos[0])])
    C = B + d2 * np.array([np.cos(angulos[1]), np.sin(angulos[1])])
    D = C + d3 * np.array([np.cos(angulos[2]), np.sin(angulos[2])])

    # Centrar verticalmente
    offset = - (min(A[1], B[1], C[1], D[1]) + max(A[1], B[1], C[1], D[1])) / 2
    for p in [A, B, C, D]:
        p[1] += offset

    # CORRECCIÓN: usar k*sc_base para segmentar lados
    lados = {
        'AB': segmentar_lado(A, B, spacing),
        'BC': segmentar_lado(B, C, spacing),
        'CD': segmentar_lado(C, D, spacing),
        'DA': segmentar_lado(D, A, spacing),
    }

    vertices = {'A': A, 'B': B, 'C': C, 'D': D}
    return lados, vertices


def agregar_agujero(P1, P2, longitud, offset, spacing):
    dir_vec = P2 - P1
    dir_unit = dir_vec / np.linalg.norm(dir_vec)
    inicio = P1 + offset * dir_unit

    puntos = segmentar_lado(P1, P2, spacing)
    
    borderPoints = []
    holePoints = []

    for p in puntos:
        proy = np.dot(p - inicio, dir_unit)
        if 0 <= proy <= longitud:
            holePoints.append(p)
        else:
            borderPoints.append(p)

    # Devolvemos ambos conjuntos
    return np.array(borderPoints), np.array(holePoints)