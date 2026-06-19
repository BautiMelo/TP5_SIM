import csv
import math
import random

from euler import EulerSimulator


class Computadora:
    def __init__(self, id_pc):
        self.id_pc = id_pc
        self.estado = 'Libre'  # 'Libre', 'Inscribiendo', 'Mantenimiento'
        self.tiempo_fin_inscripcion = -1


class ObjetoAlumno:
    def __init__(self, id_alumno, estado, hora_llegada, pc_id=None):
        self.id_alumno = id_alumno
        self.estado = estado  # 'Esperando turno', 'Siendo inscripto'
        self.hora_llegada = hora_llegada
        self.pc_id = pc_id  # PC que lo está atendiendo (None si espera)


class SimulacionInscripcion:
    def __init__(self,
                 tiempo_x, iteraciones_max,
                 mostrar_desde_i, mostrar_desde_hora_j,
                 inscripcion_a=5, inscripcion_b=8,
                 llegada_media=2,
                 mantenimiento_media=60, mantenimiento_var=3,
                 max_cola=6, tiempo_regreso=30,
                 h_euler=0.1):

        # Parámetros (en rojo o parametrizables)
        self.tiempo_x = tiempo_x
        self.iteraciones_max = iteraciones_max
        self.mostrar_desde_i = mostrar_desde_i
        self.mostrar_desde_hora_j = mostrar_desde_hora_j

        self.inscripcion_a = inscripcion_a
        self.inscripcion_b = inscripcion_b
        self.llegada_media = llegada_media
        self.mantenimiento_media = mantenimiento_media
        self.mantenimiento_var = mantenimiento_var
        self.max_cola = max_cola
        self.tiempo_regreso = tiempo_regreso

        # Euler
        self.euler = EulerSimulator(h_euler)

        self.reset_state()

    @classmethod
    def desde_params(cls, params):
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

    def reset_state(self):
        # Reloj e Iteracion
        self.reloj = 0
        self.iteracion = 0

        # Próximos eventos principales (-1 significa "sin evento programado")
        self.proxima_llegada_alumno = self.generar_llegada_alumno()
        self.proxima_llegada_mantenimiento = \
            self.generar_llegada_mantenimiento()
        self.proximo_fin_mantenimiento = -1

        # Lista para alumnos que regresan
        self.proximos_regresos = []

        # Servidores (PCs)
        self.pcs = [Computadora(i) for i in range(1, 6)]

        # Variables de Mantenimiento
        self.estado_mantenimiento = 'Salio'  # Salio, Esperando, Trabajando
        self.pc_a_mantener = 0  # Indice 0 a 4 correspondientes a PC 1 a 5
        self.llegada_historica_mantenimiento = 0  # Para tiempo ocioso

        # Colas
        self.cola = 0
        self.alumnos_en_sistema = []  # Guarda objetos alumnos
        self.id_alumno_count = 0

        # Estadísticas / Contadores
        self.cont_alumnos_llegados = 0
        self.cont_alumnos_se_van = 0
        self.tiempo_ocioso_mantenimiento = 0
        self.cont_visitas_mantenimiento = 0

        # Últimos números aleatorios / valores generados. Se resetean al
        # inicio de cada iteración y solo quedan con valor en la fila donde
        # efectivamente se generó la variable aleatoria correspondiente.
        self.rnd_llegada_alumno = ''
        self.rnd_llegada_mantenimiento = ''
        self.rnd_atencion = ''
        self.rnd_archivos_mantenimiento = ''
        self.archivos_a0 = ''
        self.tiempo_mantenimiento_calc = ''
        self.pc_asignada = ''

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

    def generar_llegada_alumno(self):
        rnd = random.random()
        self.rnd_llegada_alumno = round(rnd, 4)
        tiempo_entre_llegadas = -self.llegada_media * math.log(1 - rnd)
        return self.reloj + tiempo_entre_llegadas

    def generar_tiempo_inscripcion(self):
        rnd = random.random()
        self.rnd_atencion = round(rnd, 4)
        tiempo = self.inscripcion_a + rnd * \
            (self.inscripcion_b - self.inscripcion_a)
        return tiempo

    def generar_llegada_mantenimiento(self):
        rnd = random.random()
        self.rnd_llegada_mantenimiento = round(rnd, 4)
        a = self.mantenimiento_media - self.mantenimiento_var
        b = self.mantenimiento_media + self.mantenimiento_var
        tiempo = a + rnd * (b - a)
        return self.reloj + tiempo

    def generar_archivos_mantenimiento(self):
        rnd = random.random()
        self.rnd_archivos_mantenimiento = round(rnd, 4)
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
            self.pc_asignada = ''

            # Buscar el evento inminente
            tiempos_eventos = {
                'Llegada Alumno': self.proxima_llegada_alumno,
                'Llegada Mantenimiento': self.proxima_llegada_mantenimiento
                if self.proxima_llegada_mantenimiento != -1
                else float('inf'),
                'Fin Mantenimiento': self.proximo_fin_mantenimiento
                if self.proximo_fin_mantenimiento != -1 else float('inf')}

            # Fin inscripción de cada PC
            for i, pc in enumerate(self.pcs):
                if pc.tiempo_fin_inscripcion != -1:
                    tiempos_eventos[
                        f'Fin Inscripcion PC {i+1}'
                    ] = pc.tiempo_fin_inscripcion

            # Regresos más inminentes
            if self.proximos_regresos:
                tiempos_eventos['Regreso Alumno'] = min(self.proximos_regresos)
            else:
                tiempos_eventos['Regreso Alumno'] = float('inf')

            # Obtener el mínimo
            evento_proximo = min(tiempos_eventos, key=tiempos_eventos.get)
            reloj_siguiente = tiempos_eventos[evento_proximo]

            # Actualizar reloj
            self.reloj = reloj_siguiente
            self.iteracion += 1

            # Derivar al gestor correspondiente
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

            # Ventana de i filas a mostrar a partir de la hora j
            if (self.reloj >= self.mostrar_desde_hora_j and
                    self.filas_mostradas_en_ventana < self.mostrar_desde_i):
                self.agregar_fila(evento_proximo)
                self.filas_mostradas_en_ventana += 1

        # Última fila por requerimiento (siempre, este o no en la ventana)
        self.agregar_fila("Corte por Fin de Simulación")
        return self.vector_estado

    # --- Lógica de Eventos ---

    def procesar_llegada_generica(self):
        self.cont_alumnos_llegados += 1
        self.id_alumno_count += 1

        # Verificar si se va (más de max_cola esperando)
        if self.cola > self.max_cola:
            self.cont_alumnos_se_van += 1
            tiempo_regresa = self.reloj + self.tiempo_regreso
            self.proximos_regresos.append(tiempo_regresa)
        else:
            # Pasa al sistema
            # Buscar PC Libre que NO esté en mantenimiento y que el del
            # mantenimiento NO la esté esperando
            pc_libre = None
            for p in self.pcs:
                # Si está libre y si mantenimiento la está esperando no la
                # tomamos (tiene prioridad mantenimiento)
                if p.estado == 'Libre' and not (
                    self.estado_mantenimiento == 'Esperando' and p.id_pc -
                        1 == self.pc_a_mantener):
                    pc_libre = p
                    break

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
        self.procesar_llegada_generica()
        self.proxima_llegada_alumno = self.generar_llegada_alumno()

    def evento_regreso_alumno(self):
        # Quitamos el mínimo
        min_regreso = min(self.proximos_regresos)
        self.proximos_regresos.remove(min_regreso)
        self.procesar_llegada_generica()

    def evento_llegada_mantenimiento(self):
        self.cont_visitas_mantenimiento += 1
        self.iniciar_espera_mantenimiento()

    def iniciar_espera_mantenimiento(self):
        # El técnico queda a la espera de la PC objetivo del ciclo actual.
        # Se llama tanto al llegar de afuera (nueva visita) como al pasar de
        # una PC a la siguiente dentro de la misma visita.
        self.estado_mantenimiento = 'Esperando'
        self.llegada_historica_mantenimiento = self.reloj
        # Hasta que no termine la visita completa, no generamos la próxima
        self.proxima_llegada_mantenimiento = -1

        pc_objetivo = self.pcs[self.pc_a_mantener]

        if pc_objetivo.estado == 'Libre':
            # Arranca inmediatamente
            self.comenzar_mantenimiento(pc_objetivo)

    def comenzar_mantenimiento(self, pc_objetivo):
        self.estado_mantenimiento = 'Trabajando'
        ocio = self.reloj - self.llegada_historica_mantenimiento
        self.tiempo_ocioso_mantenimiento += ocio

        pc_objetivo.estado = 'Mantenimiento'
        a0 = self.generar_archivos_mantenimiento()
        self.archivos_a0 = a0

        # <-- Integración EULER -->
        # El método de Euler retorna una tupla (tiempo, tabla_detalle)
        tiempo_mant, tabla_euler = self.euler.integrar(a0)
        self.tiempo_mantenimiento_calc = round(tiempo_mant, 2)
        self.proximo_fin_mantenimiento = self.reloj + tiempo_mant

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
        pc_objetivo = self.pcs[self.pc_a_mantener]
        pc_objetivo.estado = 'Libre'
        self.proximo_fin_mantenimiento = -1

        # ¿Hay gente esperando en cola? Tomar el primero
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
        pc = self.pcs[pc_index]
        pc.estado = 'Libre'
        pc.tiempo_fin_inscripcion = -1

        # Liberar al alumno que estaba siendo atendido en ESTA PC puntual
        # (no el primero que aparezca: puede haber varias PCs atendiendo
        # alumnos distintos al mismo tiempo)
        for alum in self.alumnos_en_sistema:
            if alum.estado == 'Siendo inscripto' and alum.pc_id == pc.id_pc:
                self.alumnos_en_sistema.remove(alum)
                break

        # ¿El mantenimiento estaba esperando por esta PC?
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
        pct_se_van = (
            self.cont_alumnos_se_van / self.cont_alumnos_llegados
            if self.cont_alumnos_llegados else 0
        )
        ocio_promedio_por_visita = (
            round(self.tiempo_ocioso_mantenimiento /
                  self.cont_visitas_mantenimiento, 2)
            if self.cont_visitas_mantenimiento else 'Sin visitas'
        )
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
        la visita y PC a la que corresponde, para trazabilidad."""
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
        # Aca extraés todo el estado y lo formatéas en un diccionario
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
            'rnd_atencion': self.rnd_atencion,
            'pc_asignada': self.pc_asignada,
            'px_fin_man': round(
                    self.proximo_fin_mantenimiento,
                    2) if self.proximo_fin_mantenimiento != -
            1 else '',
            'rnd_archivos_man': self.rnd_archivos_mantenimiento,
            'archivos_a0': self.archivos_a0,
            'tiempo_mantenimiento_calc': self.tiempo_mantenimiento_calc,
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

        # Cuando es el fin se puede filtrar campos temp objects (alumnos)
        # como dice el enunciado.

        self.vector_estado.append(fila)


def pedir_parametro(mensaje, default, tipo=float):
    entrada = input(f'{mensaje} [{default}]: ').strip()
    if not entrada:
        return default
    return tipo(entrada)


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
