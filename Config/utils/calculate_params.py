import math

def calculate_params(
    U_max, Ma,
    rho0,
    h, dx, dy,
    vx, vy,
    alpha, beta,
    f_accel
):
    # Velocidad del sonido
    c = U_max / Ma
    
    # Constante B
    gamma = 7
    B = rho0 * c**2 / gamma

    # Phi_ij
    phi_ij = h * (vx * dx + vy * dy) / (dx**2 + dy**2)

    # Delta t por CFL
    dt_CV = h / (c + 0.6 * (alpha * c + beta * abs(phi_ij)))

    # Delta t por fuerzas
    dt_f = math.sqrt(h / f_accel)

    # Delta t final
    lambda1 = 0.4
    lambda2 = 0.25
    
    dt = min(lambda1 * dt_CV, lambda2 * dt_f)

    return {
        "c": c,
        "B": B,
        "phi_ij": phi_ij,
        "dt_CV": dt_CV,
        "dt_f": dt_f,
        "dt": dt
    }
