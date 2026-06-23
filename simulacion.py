# Motor de simulación de eventos discretos para el TP5 (inscripción a
# exámenes). Funciona con la técnica de "próximo evento": en cada
# iteración se calculan los tiempos de todos los eventos pendientes, se
# salta el reloj al más cercano y se ejecuta su lógica. Cada vez que se
# guarda una fila del vector de estado queda un snapshot completo del
# sistema en ese instante (eventos, próximos eventos, objetos, contadores
# y los rnd usados), tal como pide el enunciado.
import csv
import math
import random
from math import trunc

from euler import EulerSimulator


class Computadora:
    """Representa una de las 5 PCs de inscripción (los "servidores")."""

    def __init__(self, id_pc):
        self.id_pc = id_pc  # 1 a 5
        self.estado = 'Libre'  # 'Libre', 'Inscribiendo', 'Mantenimiento'
        # -1 = no tiene ninguna inscripción en curso en este momento
        self.tiempo_fin_inscripcion: float = -1


class ObjetoAlumno:
    """Un alumno dentro del sistema (en cola o siendo atendido)."""

    def __init__(self, id_alumno, estado, hora_llegada, pc_id=None):
        self.id_alumno = id_alumno
        self.estado = estado  # 'Esperando turno', 'Siendo inscripto'
        self.hora_llegada = hora_llegada
        # PC que lo está atendiendo (None si todavía espera en la cola).
        # Es necesario para saber, cuando termina una inscripción en una
        # PC puntual, a qué alumno hay que liberar (puede haber varias
        # PCs atendiendo alumnos distintos al mismo tiempo).
        self.pc_id = pc_id


class SimulacionInscripcion:
    """Motor principal: corre la simulación y arma el vector de estado.

    Todos los parámetros del __init__ son los valores "en rojo" del
    enunciado (parametrizables desde la pantalla o la línea de comandos).
    """

    def __init__(self,
                 tiempo_x, iteraciones_max,
                 mostrar_desde_i, mostrar_desde_hora_j,
                 inscripcion_a=5, inscripcion_b=8,
                 llegada_media=2,
                 mantenimiento_media=60, mantenimiento_var=3,
                 max_cola=6, tiempo_regreso=30,
                 h_euler=0.1):

        # Parámetros (en rojo o parametrizables)
        self.tiempo_x = tiempo_x  # X: tiempo total a simular (minutos)
        self.iteraciones_max = iteraciones_max  # N: tope de iteraciones
        self.mostrar_desde_i = mostrar_desde_i  # i: cantidad de filas a ver
        self.mostrar_desde_hora_j = mostrar_desde_hora_j  # j: desde cuándo

        self.inscripcion_a = inscripcion_a  # min. inscripción (uniforme)
        self.inscripcion_b = inscripcion_b  # max. inscripción (uniforme)
        self.llegada_media = llegada_media  # media exp. negativa, alumnos
        self.mantenimiento_media = mantenimiento_media  # media (60' = 1h)
        self.mantenimiento_var = mantenimiento_var  # +/- 3' uniforme
        self.max_cola = max_cola  # alumnos esperando antes de irse (6)
        self.tiempo_regreso = tiempo_regreso  # minutos hasta que regresa

        # Euler: integra dA/dt = -68 - A²/A0 para la demora de mantenimiento
        self.euler = EulerSimulator(h_euler)

        self.reset_state()

    @classmethod
    def desde_params(cls, params):
        """Construye la simulación a partir de un objeto Params de la UI,
        mapeando cada campo al parámetro correspondiente del motor."""
        return cls(
            tiempo_x=params.tiempo_maximo_simulacion,
            iteraciones_max=params.iteraciones_maximas,
            mostrar_desde_i=params.filas_a_mostrar,
            mostrar_desde_hora_j=params.minutos_desde_que_muestra,
            inscripcion_a=params.tiempo_minimo_inscripcion,
            inscripcion_b=params.tiempo_maximo_inscripcion,
            llegada_media=params.media_llegada_alumnos,
            mantenimiento_media=params.media_llegada_mantenimiento,
            mantenimiento_var=params.variacion_llegada_mantenimiento,
            max_cola=params.max_cola,
            tiempo_regreso=params.tiempo_regreso_alumno,
            h_euler=params.paso_euler,
        )

    def generar_random(self):
        """Genera un numero aleatorio entre 0 y 1 truncado a 2 decimales"""
        rnd = random.random()
        return trunc(rnd * 100) / 100

    def reset_state(self):
        """Inicializa (o reinicia) todas las variables de estado de una
        corrida nueva: reloj, próximos eventos, PCs, colas, contadores y
        el vector de estado vacío. Se llama una sola vez, al final del
        __init__."""
        # Reloj e Iteracion
        self.reloj = 0
        self.iteracion = 0

        # Últimos números aleatorios / valores generados. Se inicializan
        # ACÁ, antes de generar nada, para que los primeros rnd (los que
        # se calculan dos líneas más abajo, para la fila de
        # "Inicialización") no se pisen con un '' después.
        self.rnd_llegada_alumno = ''
        self.rnd_llegada_mantenimiento = ''
        self.rnd_atencion = ''
        self.rnd_archivos_mantenimiento = ''
        self.archivos_a0 = ''
        self.tiempo_mantenimiento_calc = ''
        self.rnd_pc_asignada = ''
        self.pc_asignada = ''

        # Próximos eventos principales (-1 significa "sin evento programado")
        # Se generan ya acá los primeros valores de las variables
        # aleatorias de llegada, tal como se ve en la fila de
        # "Inicialización" del vector de estado.
        self.proxima_llegada_alumno = self.generar_llegada_alumno()
        self.proxima_llegada_mantenimiento = \
            self.generar_llegada_mantenimiento()
        self.proximo_fin_mantenimiento: float = -1

        # Lista para alumnos que se fueron y van a volver más tarde
        self.proximos_regresos = []

        # Servidores (PCs), siempre 5 (PC 1 a PC 5)
        self.pcs = [Computadora(i) for i in range(1, 6)]

        # Estado del técnico de mantenimiento:
        #   'Salio'      -> no está en la sala (entre visitas)
        #   'Esperando'  -> llegó/avanzó a la próxima PC pero está ocupada
        #                   con un alumno, espera a que se libere
        #   'Trabajando' -> está haciendo mantenimiento en pc_a_mantener
        self.estado_mantenimiento = 'Salio'
        # Índice 0 a 4 de la PC que le toca en el ciclo (0=PC1 ... 4=PC5).
        # Recorre siempre en orden y nunca se puede alterar (enunciado).
        self.pc_a_mantener = 0
        # Momento en que empezó a esperar la PC actual, para poder medir
        # el tiempo ocioso (acumulado en tiempo_ocioso_mantenimiento).
        self.llegada_historica_mantenimiento = 0

        # Colas
        self.cola = 0
        self.alumnos_en_sistema = []  # Guarda objetos alumnos
        self.id_alumno_count = 0

        # Estadísticas / Contadores
        self.cont_alumnos_llegados = 0
        self.cont_alumnos_se_van = 0
        self.tiempo_ocioso_mantenimiento = 0
        self.cont_visitas_mantenimiento = 0

        # Registro de integraciones de Euler (una entrada por cada PC a la
        # que se le hace mantenimiento), con referencia a la visita y la PC
        # para poder identificar a qué instancia de la simulación pertenece.
        self.euler_log = []

        # Ventana de filas a mostrar: arranca al llegar a mostrar_desde_hora_j
        # y dura mostrar_desde_i filas.
        self.filas_mostradas_en_ventana = 0

        # Vector de Estado (guardar fila)
        self.numero_fila = 0
        self.vector_estado = []

    # --- Generadores de Variables Aleatorias ---
    #
    # Cada método de esta sección genera UNA variable aleatoria con el
    # método de la transformada inversa, guarda el rnd usado en un
    # self.rnd_* (para que agregar_fila lo muestre en la fila del evento
    # que lo generó) y devuelve el valor ya calculado. El rnd se trunca a
    # 2 decimales ANTES de usarlo en la fórmula (no sólo para mostrarlo),
    # igual que se hace a mano en la resolución por Excel.

    def generar_llegada_alumno(self):
        """Próxima llegada de un alumno: exponencial negativa, media 2'."""
        rnd = self.generar_random()
        self.rnd_llegada_alumno = rnd
        tiempo_entre_llegadas = -self.llegada_media * math.log(1 - rnd)
        return self.reloj + tiempo_entre_llegadas

    def generar_tiempo_inscripcion(self):
        """Duración de una inscripción: uniforme entre a y b minutos."""
        rnd = self.generar_random()
        self.rnd_atencion = rnd
        tiempo = self.inscripcion_a + rnd * \
            (self.inscripcion_b - self.inscripcion_a)
        return tiempo

    def generar_llegada_mantenimiento(self):
        """Próxima visita del técnico: uniforme media ± variación
        (1 hora ± 3' por defecto), contada desde que se llama (es decir,
        desde que terminó el mantenimiento de la última PC del ciclo)."""
        rnd = self.generar_random()
        self.rnd_llegada_mantenimiento = rnd
        a = self.mantenimiento_media - self.mantenimiento_var
        b = self.mantenimiento_media + self.mantenimiento_var
        tiempo = a + rnd * (b - a)
        return self.reloj + tiempo

    def generar_archivos_mantenimiento(self):
        """Cantidad de archivos (A0) de la PC a mantener: 1000, 1500 o
        2000 con probabilidad 1/3 cada uno. Este valor es el que alimenta
        la integración por Euler de dA/dt = -68 - A²/A0."""
        rnd = self.generar_random()
        self.rnd_archivos_mantenimiento = rnd
        # Pueden ser 1000, 1500, o 2000 (probabilidad uniforme de 1/3)
        if rnd < 1 / 3:
            a0 = 1000
        elif rnd < 2 / 3:
            a0 = 1500
        else:
            a0 = 2000
        return a0

    # --- Motor de Eventos ---

    def ejecutar_simulacion(self):
        """Corre la simulación completa con la técnica de "próximo
        evento": en cada vuelta del while se calculan los tiempos de
        TODOS los eventos que podrían pasar a continuación, se elige el
        más cercano, se salta el reloj a ese instante y se ejecuta su
        lógica. Se corta por tiempo_x o iteraciones_max, lo que ocurra
        primero (como pide el enunciado), y siempre se guarda la última
        fila aunque haya quedado fuera de la ventana i/j."""

        self.agregar_fila("- Inicialización -")

        while (self.reloj < self.tiempo_x and
               self.iteracion < self.iteraciones_max):

            # Reinicio de los valores "de esta fila": una variable aleatoria
            # solo debe mostrarse en la fila del evento que la generó.
            self.rnd_llegada_alumno = ''
            self.rnd_llegada_mantenimiento = ''
            self.rnd_atencion = ''
            self.rnd_archivos_mantenimiento = ''
            self.archivos_a0 = ''
            self.tiempo_mantenimiento_calc = ''
            self.rnd_pc_asignada = ''
            self.pc_asignada = ''

            # Buscar el evento inminente: armamos un diccionario
            # {nombre_evento: tiempo_en_que_ocurriría} con todos los
            # candidatos y nos quedamos con el de menor tiempo. Los
            # eventos que no están programados (-1) se mandan a +infinito
            # para que nunca puedan "ganar".
            tiempos_eventos = {
                'Llegada Alumno': self.proxima_llegada_alumno,
                'Llegada Mantenimiento': self.proxima_llegada_mantenimiento
                if self.proxima_llegada_mantenimiento != -1
                else float('inf'),
                'Fin Mantenimiento': self.proximo_fin_mantenimiento
                if self.proximo_fin_mantenimiento != -1 else float('inf')}

            # Fin inscripción de cada PC: puede haber hasta 5 al mismo
            # tiempo (una por cada PC que esté "Inscribiendo").
            for i, pc in enumerate(self.pcs):
                if pc.tiempo_fin_inscripcion != -1:
                    tiempos_eventos[
                        f'Fin Inscripcion PC {i+1}'
                    ] = pc.tiempo_fin_inscripcion

            # Regresos más inminentes (alumnos que se fueron por cola
            # llena y ya cumplieron su tiempo de espera)
            if self.proximos_regresos:
                tiempos_eventos['Regreso Alumno'] = min(self.proximos_regresos)
            else:
                tiempos_eventos['Regreso Alumno'] = float('inf')

            # Obtener el mínimo: ese es el "próximo evento" del reloj
            evento_proximo = min(
                tiempos_eventos, key=lambda k: tiempos_eventos[k])
            reloj_siguiente = tiempos_eventos[evento_proximo]

            # Actualizar reloj (salto directo al próximo evento)
            self.reloj = reloj_siguiente
            self.iteracion += 1

            # Derivar al gestor correspondiente, según qué evento ganó
            if evento_proximo == 'Llegada Alumno':
                self.evento_llegada_alumno()
            elif evento_proximo == 'Regreso Alumno':
                self.evento_regreso_alumno()
            elif evento_proximo == 'Llegada Mantenimiento':
                self.evento_llegada_mantenimiento()
            elif evento_proximo == 'Fin Mantenimiento':
                self.evento_fin_mantenimiento()
            elif evento_proximo.startswith('Fin Inscripcion'):
                idx_pc = int(evento_proximo.split()[-1]) - 1
                self.evento_fin_inscripcion(idx_pc)

            # Ventana de i filas a mostrar a partir de la hora j: una vez
            # que el reloj llega a mostrar_desde_hora_j empezamos a
            # contar, y dejamos de agregar filas al llegar a
            # mostrar_desde_i (es una sola ventana, no se reabre).
            if (self.reloj >= self.mostrar_desde_hora_j and
                    self.filas_mostradas_en_ventana < self.mostrar_desde_i):
                self.agregar_fila(evento_proximo)
                self.filas_mostradas_en_ventana += 1

        # Última fila por requerimiento (siempre, este o no en la ventana)
        self.agregar_fila("Corte por Fin de Simulación")
        return self.vector_estado

    # --- Lógica de Eventos ---

    def procesar_llegada_generica(self):
        """Lógica común a una llegada nueva y a un regreso: cuenta el
        alumno, decide si se va (cola llena) o entra al sistema, y si
        entra busca una PC libre o lo manda a la cola."""
        self.cont_alumnos_llegados += 1
        self.id_alumno_count += 1

        # Verificar si se va: "si hay más de 6 esperando" se interpreta
        # como la cola YA estaba en 7+ antes de que llegue este alumno
        # (si está en 6, este entra como 7mo y todavía no se considera
        # "más de 6"; el que se va es el siguiente que encuentre la cola
        # en 7).
        if self.cola > self.max_cola:
            self.cont_alumnos_se_van += 1
            tiempo_regresa = self.reloj + self.tiempo_regreso
            self.proximos_regresos.append(tiempo_regresa)
        else:
            # Pasa al sistema: buscamos una PC libre, salvo la PC que el
            # técnico de mantenimiento está esperando para usar (tiene
            # prioridad sobre los alumnos, pero no interrumpe una
            # inscripción que ya está en curso).
            pcs_libres = [
                p for p in self.pcs
                if p.estado == 'Libre' and not (
                    self.estado_mantenimiento == 'Esperando'
                    and p.id_pc - 1 == self.pc_a_mantener)
            ]
            pc_libre = None
            if pcs_libres:
                rnd = self.generar_random()
                self.rnd_pc_asignada = rnd
                pc_libre = pcs_libres[int(rnd * len(pcs_libres))]

            if pc_libre:
                pc_libre.estado = 'Inscribiendo'
                tiempo_atencion = self.generar_tiempo_inscripcion()
                pc_libre.tiempo_fin_inscripcion = self.reloj + tiempo_atencion
                self.pc_asignada = pc_libre.id_pc

                # Crear alumno
                nuevo_alumno = ObjetoAlumno(
                    self.id_alumno_count, 'Siendo inscripto', self.reloj,
                    pc_id=pc_libre.id_pc)
                self.alumnos_en_sistema.append(nuevo_alumno)
            else:
                self.cola += 1
                nuevo_alumno = ObjetoAlumno(
                    self.id_alumno_count, 'Esperando turno', self.reloj)
                self.alumnos_en_sistema.append(nuevo_alumno)

    def evento_llegada_alumno(self):
        """Llega un alumno nuevo desde afuera (no un regreso)."""
        self.procesar_llegada_generica()
        # Programamos cuándo va a llegar el SIGUIENTE alumno
        self.proxima_llegada_alumno = self.generar_llegada_alumno()

    def evento_regreso_alumno(self):
        """Un alumno que se había ido por cola llena vuelve a intentar."""
        min_regreso = min(self.proximos_regresos)
        self.proximos_regresos.remove(min_regreso)
        self.procesar_llegada_generica()

    # -- Ciclo del técnico de mantenimiento --
    #
    # El técnico hace UNA visita cada vez que se cumple el timer de
    # "llegada de mantenimiento" (1 hora ± 3'). En esa visita recorre las
    # 5 PCs SIEMPRE en orden (1, 2, 3, 4, 5) sin poder saltearse ninguna.
    # Si la PC que le toca está libre, empieza enseguida; si está
    # "Inscribiendo", se pone a 'Esperando' (con prioridad sobre los
    # alumnos, pero sin interrumpir la inscripción en curso) hasta que se
    # libera. Recién cuando termina la PC 5 (la última del ciclo) se va y
    # programa la siguiente visita; en las PCs 1 a 4 sigue de inmediato
    # con la próxima, sin generar un nuevo timer de llegada.

    def evento_llegada_mantenimiento(self):
        """Arranca una visita nueva (dispara el timer de 1h ± 3')."""
        self.cont_visitas_mantenimiento += 1
        self.iniciar_espera_mantenimiento()

    def iniciar_espera_mantenimiento(self):
        """Pone al técnico a la espera de la PC que le toca en el ciclo
        (pc_a_mantener). Se usa tanto al llegar de afuera (nueva visita)
        como al pasar de una PC a la siguiente dentro de la misma
        visita."""
        self.estado_mantenimiento = 'Esperando'
        self.llegada_historica_mantenimiento = self.reloj
        # Hasta que no termine la visita completa (las 5 PCs), no se
        # programa la próxima llegada de mantenimiento.
        self.proxima_llegada_mantenimiento = -1

        pc_objetivo = self.pcs[self.pc_a_mantener]

        if pc_objetivo.estado == 'Libre':
            # La PC ya está libre: arranca el mantenimiento ahora mismo
            self.comenzar_mantenimiento(pc_objetivo)

    def comenzar_mantenimiento(self, pc_objetivo):
        """Empieza efectivamente el mantenimiento de una PC: calcula el
        tiempo ocioso que esperó el técnico, sortea la cantidad de
        archivos (A0) y usa Euler para calcular cuánto va a demorar."""
        self.estado_mantenimiento = 'Trabajando'
        ocio = self.reloj - self.llegada_historica_mantenimiento
        self.tiempo_ocioso_mantenimiento += ocio

        pc_objetivo.estado = 'Mantenimiento'
        a0 = self.generar_archivos_mantenimiento()
        self.archivos_a0 = a0

        # <-- Integración EULER -->
        # El método de Euler retorna una tupla (tiempo, tabla_detalle):
        # tiempo es el instante en que A llega a 0 (la PC queda lista) y
        # tabla_detalle es el paso a paso (t, A) de la integración.
        tiempo_mant, tabla_euler = self.euler.integrar(a0)
        self.tiempo_mantenimiento_calc = round(tiempo_mant, 2)
        self.proximo_fin_mantenimiento = self.reloj + tiempo_mant

        # Guardamos el detalle de esta integración con referencia a la
        # visita y la PC, para poder mostrarla/exportarla después (pedido
        # explícito del enunciado).
        self.euler_log.append({
            'id': len(self.euler_log) + 1,
            'visita': self.cont_visitas_mantenimiento,
            'pc': pc_objetivo.id_pc,
            'a0': a0,
            'rnd_archivos': self.rnd_archivos_mantenimiento,
            'tiempo_calculado': round(tiempo_mant, 2),
            'tabla': tabla_euler,
        })

    def evento_fin_mantenimiento(self):
        """Termina el mantenimiento de la PC actual del ciclo."""
        pc_objetivo = self.pcs[self.pc_a_mantener]
        pc_objetivo.estado = 'Libre'
        self.proximo_fin_mantenimiento = -1

        # ¿Hay gente esperando en cola? Tomar el primero (FIFO)
        if self.cola > 0:
            self.cola -= 1
            pc_objetivo.estado = 'Inscribiendo'
            t_atencion = self.generar_tiempo_inscripcion()
            pc_objetivo.tiempo_fin_inscripcion = self.reloj + t_atencion
            self.pc_asignada = pc_objetivo.id_pc
            # Cambiar estado del primer alumno esperando -> Siendo inscripto
            for alum in self.alumnos_en_sistema:
                if alum.estado == 'Esperando turno':
                    alum.estado = 'Siendo inscripto'
                    alum.pc_id = pc_objetivo.id_pc
                    break

        # ¿Era la última PC del ciclo (PC 5)? Recién ahí el técnico se va y
        # vuelve en 1 hora ± 3'. Si no, sigue de inmediato con la próxima PC
        # del mismo ciclo (no puede alterar el orden de mantenimiento).
        fue_ultima_pc = self.pc_a_mantener == 4
        self.pc_a_mantener = (self.pc_a_mantener + 1) % 5

        if fue_ultima_pc:
            self.estado_mantenimiento = 'Salio'
            self.proxima_llegada_mantenimiento = \
                self.generar_llegada_mantenimiento()
        else:
            self.iniciar_espera_mantenimiento()

    def evento_fin_inscripcion(self, pc_index):
        """Termina la inscripción de un alumno en la PC pc_index."""
        pc = self.pcs[pc_index]
        pc.estado = 'Libre'
        pc.tiempo_fin_inscripcion = -1

        # Liberar al alumno que estaba siendo atendido en ESTA PC puntual
        # (no el primero que aparezca: puede haber varias PCs atendiendo
        # alumnos distintos al mismo tiempo, por eso filtramos también
        # por pc_id y no sólo por estado)
        for alum in self.alumnos_en_sistema:
            if alum.estado == 'Siendo inscripto' and alum.pc_id == pc.id_pc:
                self.alumnos_en_sistema.remove(alum)
                break

        # ¿El mantenimiento estaba esperando justo por esta PC? Tiene
        # prioridad sobre la cola de alumnos.
        if (self.estado_mantenimiento == 'Esperando' and
                self.pc_a_mantener == pc_index):
            self.comenzar_mantenimiento(pc)
            return

        # ¿Hay alumnos en la cola?
        if self.cola > 0:
            self.cola -= 1
            pc.estado = 'Inscribiendo'
            t_atencion = self.generar_tiempo_inscripcion()
            pc.tiempo_fin_inscripcion = self.reloj + t_atencion
            self.pc_asignada = pc.id_pc
            # Cambiar estado
            for alum in self.alumnos_en_sistema:
                if alum.estado == 'Esperando turno':
                    alum.estado = 'Siendo inscripto'
                    alum.pc_id = pc.id_pc
                    break

    # --- Resultados finales pedidos por el enunciado ---

    def calcular_resultados(self):
        """Calcula las 3 métricas finales que pide el enunciado:
        % de alumnos que se van y vuelven más tarde, tiempo ocioso
        promedio del técnico por visita, y promedio de visitas por día.
        """
        pct_se_van = (
            self.cont_alumnos_se_van / self.cont_alumnos_llegados
            if self.cont_alumnos_llegados else 0
        )
        ocio_promedio_por_visita = (
            round(self.tiempo_ocioso_mantenimiento /
                  self.cont_visitas_mantenimiento, 2)
            if self.cont_visitas_mantenimiento else 'Sin visitas'
        )
        # Días COMPLETOS simulados (no fraccionarios): si todavía no pasó
        # un día entero, "visitas por día" sería una proyección inestable
        # (por ej. con 10 minutos simulados daría una tasa carísima), así
        # que directamente se informa "Menos de un día".
        dias_simulados = int(self.reloj // 1440)
        visitas_promedio_por_dia = (
            round(self.cont_visitas_mantenimiento / dias_simulados, 2)
            if dias_simulados > 0 else 'Menos de un día'
        )

        return {
            'porcentaje_alumnos_se_van': round(pct_se_van * 100, 2),
            'ocio_promedio_por_visita': ocio_promedio_por_visita,
            'visitas_promedio_por_dia': visitas_promedio_por_dia,
        }

    def exportar_euler_csv(self, path='euler_log.csv'):
        """Vuelca el detalle de cada integración de Euler con referencia a
        la visita y PC a la que corresponde, para trazabilidad (pedido
        del enunciado: mostrar la integración numérica en la app o
        bajarla a Excel/CSV con referencia a qué instancia corresponde).
        Una fila por cada paso (t, A) de Euler, repitiendo id/visita/pc
        para poder filtrar/agrupar después."""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['id_integracion', 'visita', 'pc', 'a0',
                 'rnd_archivos', 't', 'A'])
            for entrada in self.euler_log:
                for t, a in entrada['tabla']:
                    writer.writerow([
                        entrada['id'], entrada['visita'], entrada['pc'],
                        entrada['a0'], entrada['rnd_archivos'],
                        round(t, 4), round(a, 4),
                    ])

    def agregar_fila(self, evento):
        """Construye una fila del vector de estado con todo lo que pide
        el enunciado: número de fila, hora simulada, evento, próximos
        eventos a ejecutarse (px_*), objetos del sistema con sus
        atributos (estado_mantenimiento, PCx_est/PCx_fin, y los alumnos
        presentes en Alumno{n}_*), variables auxiliares (cola,
        contadores) y el rnd de cada variable aleatoria que se haya
        generado en esta iteración puntual."""
        self.numero_fila += 1
        fila = {
            'numero_fila': self.numero_fila,
            'iteracion': self.iteracion,
            'reloj': round(self.reloj, 2),
            'evento': evento,
            'rnd_llegada_alum': self.rnd_llegada_alumno,
            'px_llegada_alum': round(self.proxima_llegada_alumno, 2),
            'rnd_llegada_man': self.rnd_llegada_mantenimiento,
            'px_llegada_man': round(
                self.proxima_llegada_mantenimiento,
                2) if self.proxima_llegada_mantenimiento != -1 else '',
            'rnd_pc_asignada': self.rnd_pc_asignada,
            'pc_asignada': self.pc_asignada,
            'rnd_atencion': self.rnd_atencion,
            'rnd_archivos_man': self.rnd_archivos_mantenimiento,
            'archivos_a0': self.archivos_a0,
            'tiempo_mantenimiento_calc': self.tiempo_mantenimiento_calc,
            'px_fin_man': round(
                    self.proximo_fin_mantenimiento,
                    2) if self.proximo_fin_mantenimiento != -
            1 else '',
            'estado_mantenimiento': self.estado_mantenimiento,
            'pc_en_mantenimiento': self.pcs[self.pc_a_mantener].id_pc,
            'cola': self.cola,
            'alumnos_van_regresan': self.cont_alumnos_se_van,
            'tiempo_ocioso_tot_mant': self.tiempo_ocioso_mantenimiento,
            'visitas_mant': self.cont_visitas_mantenimiento}

        for i, pc in enumerate(self.pcs):
            fila[f'PC{i + 1}_est'] = pc.estado
            tiempo_fin = pc.tiempo_fin_inscripcion
            fila[f'PC{i+1}_fin'] = (
                round(tiempo_fin, 2) if tiempo_fin != -1 else ''
            )

        # Objetos temporales: los alumnos presentes en el sistema en
        # este instante (los que ya se fueron no se muestran, porque ya
        # no existen). La cantidad de columnas Alumno{n}_* es dinámica
        # según cuántos haya en cada fila puntual, en vez de reservar de
        # antemano columnas para un máximo hipotético que casi siempre
        # estarían vacías. En la última fila (corte por fin de
        # simulación) el enunciado dice que no es necesario mostrarlos.
        if evento != "Corte por Fin de Simulación":
            for i, alum in enumerate(self.alumnos_en_sistema, start=1):
                fila[f'Alumno{i}_id'] = alum.id_alumno
                fila[f'Alumno{i}_estado'] = alum.estado
                fila[f'Alumno{i}_llegada'] = round(alum.hora_llegada, 2)
                fila[f'Alumno{i}_pc'] = (
                    alum.pc_id if alum.pc_id is not None else ''
                )

        self.vector_estado.append(fila)


def pedir_parametro(mensaje, default, tipo=float):
    """Pide un parámetro por consola, devolviendo un default si se
    aprieta Enter sin escribir nada. Usado por el modo CLI (alternativo
    a la pantalla de PyQt6 en ui/pantalla.py)."""
    entrada = input(f'{mensaje} [{default}]: ').strip()
    if not entrada:
        return default
    return tipo(entrada)


# Punto de entrada por línea de comandos: pide los parámetros "en rojo"
# por consola, corre la simulación completa y muestra el vector de
# estado, los resultados finales y exporta la integración de Euler.
if __name__ == "__main__":
    tiempo_x = pedir_parametro(
        'Tiempo X de simulación (minutos)', 1440)
    iteraciones_max = pedir_parametro(
        'Cantidad máxima de iteraciones', 100000, int)
    mostrar_desde_i = pedir_parametro(
        'Cantidad de filas a mostrar (i)', 30, int)
    mostrar_desde_hora_j = pedir_parametro(
        'Hora desde la que se muestra (j)', 0)
    h_euler = pedir_parametro('Paso h de Euler', 0.1)

    sim = SimulacionInscripcion(
        tiempo_x=tiempo_x,
        iteraciones_max=iteraciones_max,
        mostrar_desde_i=mostrar_desde_i,
        mostrar_desde_hora_j=mostrar_desde_hora_j,
        # parametros requeridos por el enunciado
        inscripcion_a=5,
        inscripcion_b=8,
        llegada_media=2,
        max_cola=6,
        tiempo_regreso=30,
        h_euler=h_euler,
    )
    res = sim.ejecutar_simulacion()
    for fila in res:
        print(fila)

    print('\nResultados:')
    for clave, valor in sim.calcular_resultados().items():
        print(f'  {clave}: {valor}')

    sim.exportar_euler_csv()
    print(f'\nDetalle de integraciones de Euler en euler_log.csv '
          f'({len(sim.euler_log)} integraciones registradas)')
