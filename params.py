class Params:
    # simulacion
    tiempo_maximo_simulacion: float = 1440
    iteraciones_maximas: int = 100000
    minutos_desde_que_muestra: float = 0
    filas_a_mostrar: int = 30

    # alumnos
    media_llegada_alumnos: float = 2
    tiempo_minimo_inscripcion: float = 5
    tiempo_maximo_inscripcion: float = 8
    max_cola: int = 6
    tiempo_regreso_alumno: float = 30

    # mantenimiento
    media_llegada_mantenimiento: float = 60
    variacion_llegada_mantenimiento: float = 3

    # euler
    paso_euler: float = 0.1
