def altura_promedio_capa_superior(
    df,
    delta_y,
    x_min=None,
    x_max=None,
    tipo=0
):
    # Filtrar por tipo de partícula
    df_filtrado = df[df["type"] == tipo]

    # Filtrar por intervalo en X si se indica
    if x_min is not None:
        df_filtrado = df_filtrado[df_filtrado["posx"] >= x_min]
    if x_max is not None:
        df_filtrado = df_filtrado[df_filtrado["posx"] <= x_max]

    if df_filtrado.empty:
        return None, 0

    # Altura máxima
    y_max = df_filtrado["posy"].max()
    y_min = y_max - delta_y

    # Partículas dentro de la capa superior
    capa = df_filtrado[
        (df_filtrado["posy"] >= y_min) &
        (df_filtrado["posy"] <= y_max)
    ]

    if capa.empty:
        return None, 0

    altura_media = capa["posy"].mean()
    return altura_media, len(capa)
