class EulerSimulator:
    """Integra dA/dt = -68 - A^2/A0 por el metodo de Euler hasta A <= 0."""

    def __init__(self, h):
        self.h = h

    def integrar(self, a0):
        t = 0
        a = a0
        tabla = [[t, a]]

        while a > 0:
            a = a + (-68 - (a ** 2) / a0) * self.h
            t = t + self.h
            tabla.append([t, a])

        return t, tabla


if __name__ == "__main__":
    euler = EulerSimulator(0.1)
    tiempo, tabla = euler.integrar(2000)
    print(tiempo)
    for fila in tabla:
        print(fila)
