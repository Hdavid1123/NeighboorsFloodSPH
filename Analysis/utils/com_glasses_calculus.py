def detectar_superficie_libre(
    archivo_txt,
    intervalo_x,
    y_fondo=-0.5e-3,
    delta_rel=0.01,
    dy_extra_rel=0.0,     # 👈 NUEVO
    n_min=10,
    dx_tol=1e-7,
    particle_size=10,
    mostrar_plot=True,
    title=None,
    xlim=None,
    ylim=None,
    debug=False
):
    """
    Detecta la superficie libre del fluido en un intervalo en x
    usando un criterio de densidad vertical adaptativa.

    Primero detecta la superficie (criterio geométrico),
    luego extiende el muestreo hacia abajo sin mover la superficie.
    """

    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter

    # --------------------------------------------------
    # 1. Leer datos
    # --------------------------------------------------
    df = pd.read_csv(archivo_txt, sep=r"\s+")

    df_fluid = df[df["type"] == 0]
    df_boundary = df[df["type"] == 1]

    xmin, xmax = intervalo_x

    # --------------------------------------------------
    # 2. Filtrar fluido en intervalo x
    # --------------------------------------------------
    df_fluido_x = df_fluid[
        (df_fluid["posx"] >= xmin - dx_tol) &
        (df_fluid["posx"] <= xmax + dx_tol)
    ]

    if len(df_fluido_x) == 0:
        raise ValueError(
            f"No hay partículas de fluido en x ∈ [{xmin},{xmax}]"
        )

    # --------------------------------------------------
    # 3. Ordenar por altura
    # --------------------------------------------------
    df_ord = df_fluido_x.sort_values(
        "posy", ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 4. Detección de superficie (NO se toca)
    # --------------------------------------------------
    y_ref_final = None
    dy_final = None

    for i in range(len(df_ord)):
        y_ref = df_ord.loc[i, "posy"]
        altura_ref = y_ref - y_fondo

        if altura_ref <= 0:
            continue

        dy = delta_rel * altura_ref

        df_banda = df_ord[
            (df_ord["posy"] <= y_ref) &
            (df_ord["posy"] >= y_ref - dy)
        ]

        n = len(df_banda)

        if debug:
            print(
                f"i={i:3d}, y_ref={y_ref:.3e}, "
                f"dy={dy:.3e}, n={n}"
            )

        if n >= n_min:
            y_ref_final = y_ref
            dy_final = dy
            break

    if y_ref_final is None:
        raise ValueError(
            "No se encontró una superficie libre con suficientes partículas"
        )

    # --------------------------------------------------
    # 5. EXTENSIÓN DEL MUESTREO (NUEVO)
    # --------------------------------------------------
    altura_ref_final = y_ref_final - y_fondo
    dy_extra = dy_extra_rel * altura_ref_final
    dy_total = dy_final + dy_extra

    df_superficie = df_ord[
        (df_ord["posy"] <= y_ref_final) &
        (df_ord["posy"] >= y_ref_final - dy_total)
    ]

    # --------------------------------------------------
    # 6. Magnitudes finales
    # --------------------------------------------------
    y_prom = df_superficie["posy"].mean()
    altura_fluido = y_prom - y_fondo

    # --------------------------------------------------
    # 7. Gráfica
    # --------------------------------------------------
    if mostrar_plot:
        fig, ax = plt.subplots(figsize=(6, 8))

        ax.scatter(
            df_boundary["posx"], df_boundary["posy"],
            s=particle_size, c="black", label="Frontera"
        )

        ax.scatter(
            df_fluid["posx"], df_fluid["posy"],
            s=particle_size, c="blue", label="Fluido"
        )

        ax.scatter(
            df_superficie["posx"],
            df_superficie["posy"],
            s=particle_size * 2,
            c="orange",
            label="Superficie libre (extendida)"
        )

        ax.axhline(y_fondo, color="purple", linestyle="--", label="Fondo")
        ax.axhline(y_ref_final, color="red", linestyle=":", label="Inicio superficie")

        # Labels y título (MISMO TAMAÑO que plot_ics)
        ax.set_xlabel("x [m]", fontsize=15)
        ax.set_ylabel("y [m]", fontsize=15)
        ax.set_title(title or "Detección de superficie libre", fontsize=16)

        # Ticks, leyenda y grilla (MISMO TAMAÑO)
        ax.tick_params(axis="both", which="major", labelsize=13)
        ax.legend(fontsize=12)
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

    # --------------------------------------------------
    # 8. Resultados
    # --------------------------------------------------
    return {
        "intervalo_x": intervalo_x,
        "y_ref": y_ref_final,
        "dy": dy_final,
        "dy_total": dy_total,
        "y_prom": y_prom,
        "altura_fluido": altura_fluido,
        "n_particulas": len(df_superficie),
        "ids_particulas": df_superficie["id"].tolist(),
        "df_superficie": df_superficie
    }
