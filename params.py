class Params:
    """Todos los valores "en rojo" (parametrizables) del enunciado, con
    sus defaults. Los lee/escribe la pantalla de PyQt6 (ui/pantalla.py)
    y SimulacionInscripcion.desde_params() los traduce a los argumentos
    del motor de simulación (simulacion.py)."""

    # simulacion
    tiempo_maximo_simulacion: float = 1440  # X: minutos a simular (1 día)
    iteraciones_maximas: int = 100000  # N: tope de iteraciones (máx 100000)
    minutos_desde_que_muestra: float = 0  # j: desde qué minuto se muestra
    filas_a_mostrar: int = 30  # i: cantidad de filas de la ventana

    # alumnos
    media_llegada_alumnos: float = 2  # exp. negativa, minutos
    tiempo_minimo_inscripcion: float = 5  # uniforme, minutos
    tiempo_maximo_inscripcion: float = 8  # uniforme, minutos
    max_cola: int = 6  # alumnos esperando antes de que el próximo se vaya
    tiempo_regreso_alumno: float = 30  # minutos hasta que vuelve (media hora)

    # mantenimiento
    media_llegada_mantenimiento: float = 60  # 1 hora
    variacion_llegada_mantenimiento: float = 3  # +/- 3 minutos

    # euler
    paso_euler: float = 0.1  # h: paso de integración, en minutos
