import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os
from scipy.signal import find_peaks, savgol_filter


def analyze_density_simulation(sim_folder: Path,
                               window_length=151,
                               polyorder=3,
                               prominence=5,
                               min_peak_distance=50,
                               variation_threshold=1.0):
    """
    Ejecuta todo el análisis de ondas de densidad sobre carpetas de simulación SPH.
    
    Parámetros
    ----------
    sim_folder : Path
        Carpeta que contiene el folder 'Output' con los archivos state_*.txt.
    window_length : int
        Longitud de ventana para el suavizado Savitzky-Golay.
    polyorder : int
        Orden del polinomio del suavizado.
    prominence : float
        Prominencia mínima para considerar un pico real.
    min_peak_distance : int
        Separación mínima entre picos filtrados (en índices).
    variation_threshold : float
        Porcentaje (en %) por debajo del cual se considera que la amplitud es estable.
    
    Returns
    -------
    dict
        Diccionario con:
        't' : índices temporales
        'rho_avg' : promedio de densidad por estado
        'y_smooth' : señal suavizada
        'peaks_filtered' : índices de picos reales
        'duplas' : pares de picos consecutivos
        'dupla_mean' : promedio de densidad en cada dupla
        'amplitudes' : amplitudes entre cada dos picos
        'variaciones_pct' : variaciones relativas en %
        'index_threshold' : primer índice donde variación < threshold
        'dupla_threshold' : dupla correspondiente
        'valor_promedio_threshold' : valor promedio en ese punto
    """

    # --- 1. Buscar archivos ---
    output_folder = sim_folder / "Output"
    archivos = sorted(glob.glob(os.path.join(output_folder, "state_*.txt")))
    
    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos state_*.txt en {output_folder}")

    promedios_rho = []
    indices = []

    # --- 2. Leer cada archivo y extraer promedio ---
    for archivo in archivos:
        df = pd.read_csv(archivo, sep=r"\s+", header=0)
        promedios_rho.append(df["rho"].mean())
        idx = int(os.path.basename(archivo).split("_")[1].split(".")[0])
        indices.append(idx)

    y = np.array(promedios_rho)
    t = np.array(indices)

    # --- 3. Suavizado ---
    y_smooth = savgol_filter(y, window_length=window_length, polyorder=polyorder)

    # --- 4. Detección de picos (máximos y mínimos) ---
    pmax, _ = find_peaks(y_smooth, prominence=prominence)
    pmin, _ = find_peaks(-y_smooth, prominence=prominence)

    picos = np.sort(np.concatenate([pmax, pmin]))

    # --- 5. Filtrar picos demasiado cercanos ---
    picos_filtrados = [picos[0]]
    for i in range(1, len(picos)):
        if picos[i] - picos_filtrados[-1] > min_peak_distance:
            picos_filtrados.append(picos[i])
    picos_filtrados = np.array(picos_filtrados)

    # --- 6. Generar duplas ---
    duplas = [
        [picos_filtrados[i], picos_filtrados[i + 1]]
        for i in range(len(picos_filtrados) - 1)
    ]

    # --- 7. Promedio en cada dupla ---
    promedio_duplas = [
        float(np.mean([y_smooth[a], y_smooth[b]]))
        for (a, b) in duplas
    ]

    # --- 8. Amplitudes ---
    amplitudes = [
        float(np.abs(y_smooth[a] - y_smooth[b]))
        for (a, b) in duplas
    ]

    # --- 9. Variación porcentual ---
    variacion_amp_pct = [
        100 * amplitudes[i] / promedio_duplas[i]
        for i in range(len(duplas))
    ]

    # --- 10. Buscar primer índice donde la variación < threshold ---
    index_threshold = None
    dupla_threshold = None
    valor_promedio_threshold = None

    for i, var in enumerate(variacion_amp_pct):
        if var < variation_threshold:
            index_threshold = i
            dupla_threshold = duplas[i]
            valor_promedio_threshold = promedio_duplas[i]
            break

    # --- 11. Empaquetar resultados ---
    return {
        "t": t,
        "rho_avg": y,
        "y_smooth": y_smooth,
        "peaks_filtered": picos_filtrados,
        "duplas": duplas,
        "dupla_mean": promedio_duplas,
        "amplitudes": amplitudes,
        "variaciones_pct": variacion_amp_pct,
        "index_threshold": index_threshold,
        "dupla_threshold": dupla_threshold,
        "valor_promedio_threshold": valor_promedio_threshold
    }
