import numpy as np

def characteristic_vel(H_max_fluid, g, L_max):
    """
    Args:
        H_max_fluid (_type_): Altura máxima del fluido para aplicar la ley de Torricelli
        g (_type_): aceleración gravitacional
        L_max (_type_): Tamaño máximo representativo del sistema de simulación.
    """
    torricelli_v = np.sqrt(2*g*H_max_fluid)
    
    potentialE_v = np.sqrt(g*L_max)
    
    if torricelli_v == potentialE_v:
        return torricelli_v
    else:
        return (torricelli_v + potentialE_v)/2

def sound_velocity_Ma(H_max_fluid, g, L_max, Mach=0.1):
    """
    Realiza el cálculo de la velocidad de sonido tal que el número Mach,
    dentro del régimen de débilmente compresible.
    
    Hace uso de characteristic_vel.
    """
    U = characteristic_vel(H_max_fluid, g, L_max)
    
    if Mach > 0.1:
        print("El número Mach no es adecuado para el sistema")
    else:
        c = U / Mach
    
    return c

def Froude_number(ch_velocity, g, L_max):
    """
    Se calcula el número de Froude para determinar si los parámetros
    son compatibles con el intervalo 

    Args:
        ch_velocity (_type_): _description_
        g (_type_): _description_
        L_max (_type_): _description_
    """