class Params:
    # simulacion
    tiempo_maximo_simulacion: float = 100
    minutos_desde_que_muestra: float = 0
    filas_a_mostrar: int = 10

    # alumnos
    media_llegada_alumnos: float = 2
    tiempo_minimo_inscripcion: float = 5
    tiempo_maximo_inscripcion: float = 8

    # mantenimiento
    media_llegada_mantenimiento: float = 60
    variacion_llegada_mantenimiento: float = 3

    # euler
    paso_euler: float = 0.1