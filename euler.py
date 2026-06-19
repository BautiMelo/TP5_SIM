class EulerSimulator:
    """Integra numéricamente dA/dt = -68 - A²/A0 por el método de Euler.

    A representa la cantidad de archivos que le quedan por procesar a la
    PC en mantenimiento; A0 es la cantidad inicial (1000, 1500 o 2000,
    sorteada en simulacion.py). La ecuación no tiene solución cerrada
    simple, por eso se integra paso a paso con paso h (parametrizable,
    pedido por el enunciado). Se considera que el mantenimiento terminó
    cuando A llega a 0 o menos.
    """

    def __init__(self, h):
        self.h = h  # paso de integración (minutos)

    def integrar(self, a0):
        """Devuelve (tiempo_total, tabla) donde tiempo_total es el
        instante en que A se hizo <= 0 (duración del mantenimiento) y
        tabla es la lista de pares [t, A] de cada paso, para poder
        mostrar/exportar el detalle de la integración."""
        t = 0
        a = a0
        tabla = [[t, a]]

        while a > 0:
            # Paso de Euler: A_(i+1) = A_i + h * f(t_i, A_i)
            a = a + (-68 - (a ** 2) / a0) * self.h
            t = t + self.h
            tabla.append([t, a])

        return t, tabla


# Permite probar la integración de forma aislada: corre con A0 = 2000 y
# h = 0.1 (los valores que usa el enunciado de ejemplo) e imprime cada
# paso por consola.
if __name__ == "__main__":
    euler = EulerSimulator(0.1)
    tiempo, tabla = euler.integrar(2000)
    print(tiempo)
    for fila in tabla:
        print(fila)
