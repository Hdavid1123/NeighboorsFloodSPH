from Config.utils.plot_ics import plot_ics

def show_ics_and_confirm(txt_file, particle_size=6):
    while True:
        plot_ics(str(txt_file), particle_size=particle_size)

        print("\nOpciones:")
        print("  Y → Aceptar geometría")
        print("  N → Cancelar y borrar archivos")
        print("  S → Cambiar tamaño de partícula")

        op = input("Selecciona opción (Y/N/S): ").strip().upper()

        if op == "Y":
            return True

        elif op == "N":
            return False

        elif op == "S":
            try:
                particle_size = float(
                    input("Nuevo tamaño de partícula (ej: 2, 5, 10): ")
                )
            except ValueError:
                print("Valor inválido. Usando tamaño anterior.")

        else:
            print("Opción no válida.")
