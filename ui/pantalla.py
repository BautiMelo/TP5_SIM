# Pantalla principal (PyQt6): junta los parámetros de la simulación,
# corre el motor (simulacion.py) y muestra el vector de estado y los
# resultados finales. Reemplaza/complementa el modo por consola de
# simulacion.py.
import os
import sys

# Este archivo vive en ui/, pero importa módulos que están un nivel
# arriba (params.py, simulacion.py) y módulos que están en su propia
# carpeta (error_dialog.py). Si se corre como script (`python
# ui/pantalla.py`) Python sólo agrega ui/ a sys.path, y si se corre como
# módulo (`python -m ui.pantalla`) sólo agrega la raíz del proyecto. Para
# que ambos imports funcionen sin importar cómo se lo ejecute, agregamos
# manualmente las dos carpetas a sys.path.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_THIS_DIR)
for _dir in (_THIS_DIR, _ROOT_DIR):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtGui import QDoubleValidator, QIntValidator  # noqa: E402
from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from error_dialog import ErrorDialog  # noqa: E402
from params import Params  # noqa: E402
from simulacion import SimulacionInscripcion  # noqa: E402


class MainWindow(QMainWindow):
    """Ventana única de la app: a la izquierda los campos de parámetros
    (todos los valores "en rojo" del enunciado) y un botón Iniciar; a la
    derecha la tabla con el vector de estado y los resultados finales."""

    def __init__(self, default_params: Params):
        super().__init__()
        self.params: Params = default_params
        # Se completa recién al presionar "Iniciar"; mientras tanto el
        # botón de exportar Euler queda deshabilitado (ver más abajo).
        self.ultima_simulacion: SimulacionInscripcion | None = None

        self.setWindowTitle("TP5 Simulación")
        # self.showMaximized()
        self.setMinimumSize(1800, 1000)

        # contenedor principal de todos los elementos ui
        container = QWidget()
        layout = QHBoxLayout()
        container.setLayout(layout)

        # agregar botones a la izquierda
        layout.addLayout(self.crear_layout_parametros(), 3)

        # layout de resultados
        layout.addLayout(self.crear_layout_resultados(), 9)

        self.setCentralWidget(container)

    # crea los botones para ingresar los parametros
    def crear_layout_parametros(self) -> QLayout:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(40)

        titulo = QLabel("Parámetros de la simulación")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold")
        layout.addWidget(titulo)

        # parametros de la simulacion
        layout_simulacion = self.layout_parametros_simulacion()

        # parametros de los alumnos
        layout_inscripcion = self.layout_parametros_inscripcion()

        # parametros de mantenimiento
        layout_mantenimiento = self.layout_mantenimiento()

        # parametros de euler
        layout_euler = self.layout_euler()

        # boton iniciar
        layout_boton = QVBoxLayout()
        layout_boton.setSpacing(10)
        iniciar_label = QLabel("Iniciar simulación")
        iniciar_boton = QPushButton("Iniciar")
        iniciar_boton.clicked.connect(self.iniciar_simulacion)
        layout_boton.addWidget(iniciar_label)
        layout_boton.addWidget(iniciar_boton)

        self.boton_exportar_euler = QPushButton(
            "Exportar integración de Euler (CSV)")
        self.boton_exportar_euler.clicked.connect(self.exportar_euler)
        self.boton_exportar_euler.setEnabled(False)
        layout_boton.addWidget(self.boton_exportar_euler)

        layout.addLayout(layout_simulacion)
        layout.addLayout(layout_inscripcion)
        layout.addLayout(layout_mantenimiento)
        layout.addLayout(layout_euler)
        layout.addLayout(layout_boton)
        return layout

    # crea los botones para ingresar los parametros de tiempo maximo,
    # cantidad de iteraciones y filas a mostrar
    def layout_parametros_simulacion(self) -> QLayout:
        layout_simulacion = QVBoxLayout()
        layout_simulacion.setSpacing(10)
        # tiempo maximo
        # titulo
        tiempo_label = QLabel("Tiempo máximo de simulación en minutos (X):")
        # input
        self.tiempo_input = QLineEdit()
        self.tiempo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_input.setText(str(self.params.tiempo_maximo_simulacion))
        # cantidad de iteraciones
        # titulo
        iteraciones_label = QLabel(
            "Cantidad máxima de iteraciones (N, hasta 100000):")
        # input
        self.iteraciones_input = QLineEdit()
        self.iteraciones_input.setValidator(QIntValidator(1, 100000))
        self.iteraciones_input.setText(str(self.params.iteraciones_maximas))
        # mostrar desde hora
        # titulo
        mostrar_desde_label = QLabel(
            "Mostrar resultados desde el minuto (j):")
        # input
        self.mostrar_desde_input = QLineEdit()
        self.mostrar_desde_input.setValidator(
            QDoubleValidator(0.0, 10000.0, 2))
        self.mostrar_desde_input.setText(
            str(self.params.minutos_desde_que_muestra))
        # cantidad filas
        # titulo
        filas_label = QLabel("Cantidad de filas a mostrar (i):")
        # input
        self.filas_input = QLineEdit()
        self.filas_input.setValidator(QIntValidator(0, 100000))
        self.filas_input.setText(str(self.params.filas_a_mostrar))
        # agregar al layout
        layout_simulacion.addWidget(tiempo_label)
        layout_simulacion.addWidget(self.tiempo_input)
        layout_simulacion.addWidget(iteraciones_label)
        layout_simulacion.addWidget(self.iteraciones_input)
        layout_simulacion.addWidget(mostrar_desde_label)
        layout_simulacion.addWidget(self.mostrar_desde_input)
        layout_simulacion.addWidget(filas_label)
        layout_simulacion.addWidget(self.filas_input)

        return layout_simulacion

    # crea los botones para ingresar los parametros de los alumnos
    def layout_parametros_inscripcion(self) -> QLayout:
        layout_inscripcion = QVBoxLayout()
        layout_inscripcion.setSpacing(10)

        # tiempo de llegada
        # titulo
        llegada_label = QLabel("Media de llegada de alumnos en minutos:")
        # input
        self.llegada_alumnos_input = QLineEdit()
        self.llegada_alumnos_input.setValidator(
            QDoubleValidator(0.01, 10000.0, 2))
        self.llegada_alumnos_input.setText(
            str(self.params.media_llegada_alumnos))
        # tiempo minimo de inscripcion
        # titulo
        tiempo_minimo_label = QLabel(
            "Tiempo mínimo de inscripción en minutos:")
        # input
        self.tiempo_minimo_input = QLineEdit()
        self.tiempo_minimo_input.setValidator(
            QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_minimo_input.setText(
            str(self.params.tiempo_minimo_inscripcion))
        # tiempo maximo de inscripcion
        # titulo
        tiempo_maximo_label = QLabel(
            "Tiempo máximo de inscripción en minutos:")
        # input
        self.tiempo_maximo_input = QLineEdit()
        self.tiempo_maximo_input.setValidator(
            QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_maximo_input.setText(
            str(self.params.tiempo_maximo_inscripcion))
        # cantidad maxima de alumnos en cola
        # titulo
        max_cola_label = QLabel("Cantidad máxima de alumnos en cola:")
        # input
        self.max_cola_input = QLineEdit()
        self.max_cola_input.setValidator(QIntValidator(0, 1000))
        self.max_cola_input.setText(str(self.params.max_cola))
        # tiempo de regreso de un alumno que se va
        # titulo
        tiempo_regreso_label = QLabel(
            "Tiempo de regreso de un alumno en minutos:")
        # input
        self.tiempo_regreso_input = QLineEdit()
        self.tiempo_regreso_input.setValidator(
            QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_regreso_input.setText(
            str(self.params.tiempo_regreso_alumno))
        # agregar al layout
        layout_inscripcion.addWidget(llegada_label)
        layout_inscripcion.addWidget(self.llegada_alumnos_input)
        layout_inscripcion.addWidget(tiempo_minimo_label)
        layout_inscripcion.addWidget(self.tiempo_minimo_input)
        layout_inscripcion.addWidget(tiempo_maximo_label)
        layout_inscripcion.addWidget(self.tiempo_maximo_input)
        layout_inscripcion.addWidget(max_cola_label)
        layout_inscripcion.addWidget(self.max_cola_input)
        layout_inscripcion.addWidget(tiempo_regreso_label)
        layout_inscripcion.addWidget(self.tiempo_regreso_input)

        return layout_inscripcion

    # crea los botones para ingresar los parametros de mantenimiento
    def layout_mantenimiento(self) -> QLayout:
        layout_mantenimiento = QVBoxLayout()
        layout_mantenimiento.setSpacing(10)

        # tiempo de llegada
        # titulo
        llegada_label = QLabel(
            "Media de llegada de mantenimiento en minutos:")
        # input
        self.llegada_mantenimiento_input = QLineEdit()
        self.llegada_mantenimiento_input.setValidator(
            QDoubleValidator(0.01, 10000.0, 2))
        self.llegada_mantenimiento_input.setText(
            str(self.params.media_llegada_mantenimiento))
        # variacion de llegada
        # titulo
        variacion_label = QLabel(
            "Variación de llegada de mantenimiento en minutos:")
        # input
        self.variacion_input = QLineEdit()
        self.variacion_input.setValidator(QDoubleValidator(0.0, 10000.0, 2))
        self.variacion_input.setText(
            str(self.params.variacion_llegada_mantenimiento))
        # agregar al layout
        layout_mantenimiento.addWidget(llegada_label)
        layout_mantenimiento.addWidget(self.llegada_mantenimiento_input)
        layout_mantenimiento.addWidget(variacion_label)
        layout_mantenimiento.addWidget(self.variacion_input)

        return layout_mantenimiento

    def layout_euler(self) -> QLayout:
        layout_euler = QVBoxLayout()
        layout_euler.setSpacing(10)

        # paso de euler
        # titulo
        paso_label = QLabel("Paso de Euler en minutos (h):")
        # input
        self.paso_input = QLineEdit()
        self.paso_input.setValidator(QDoubleValidator(0.01, 1, 2))
        self.paso_input.setText(str(self.params.paso_euler))
        # agregar al layout
        layout_euler.addWidget(paso_label)
        layout_euler.addWidget(self.paso_input)

        return layout_euler

    # layout donde se muestran la tabla del vector de estado y los
    # resultados finales pedidos por el enunciado
    def crear_layout_resultados(self) -> QLayout:
        layout = QVBoxLayout()

        self.resultados_label = QLabel(
            "Configure los parámetros y presione \"Iniciar\".")
        layout.addWidget(self.resultados_label)

        self.tabla_resultado = QTableWidget()
        layout.addWidget(self.tabla_resultado)

        return layout

    def iniciar_simulacion(self):
        """Handler del botón "Iniciar": valida los campos, corre el
        motor de punta a punta y muestra los resultados."""
        if not self.leer_parametros():
            return

        self.ultima_simulacion = SimulacionInscripcion.desde_params(
            self.params)
        vector_estado = self.ultima_simulacion.ejecutar_simulacion()
        self.mostrar_vector_estado(vector_estado)
        self.mostrar_resultados(self.ultima_simulacion.calcular_resultados())
        # Sólo tiene sentido exportar si hubo al menos un mantenimiento
        self.boton_exportar_euler.setEnabled(
            bool(self.ultima_simulacion.euler_log))

    # lee los campos de input y carga los parametros. Devuelve True si
    # todos los valores son válidos, False si mostró algún error.
    def leer_parametros(self) -> bool:
        # Tabla (input, tipo, validación, mensaje de error, atributo de
        # Params a actualizar) para no repetir el mismo try/except 12
        # veces: se valida y vuelca cada campo en un solo loop.
        campos = (
            (self.tiempo_input, float, lambda v: v > 0,
             "El tiempo máximo de simulación debe ser un número positivo.",
             "tiempo_maximo_simulacion"),
            (self.iteraciones_input, int, lambda v: v > 0,
             "La cantidad máxima de iteraciones debe ser un número "
             "positivo.",
             "iteraciones_maximas"),
            (self.mostrar_desde_input, float, lambda v: v >= 0,
             "El minuto desde el que muestran las filas debe ser un "
             "número no negativo.",
             "minutos_desde_que_muestra"),
            (self.filas_input, int, lambda v: v >= 0,
             "La cantidad de filas a mostrar debe ser un número no "
             "negativo.",
             "filas_a_mostrar"),
            (self.llegada_alumnos_input, float, lambda v: v > 0,
             "La media de llegada de alumnos debe ser un número positivo.",
             "media_llegada_alumnos"),
            (self.tiempo_minimo_input, float, lambda v: v > 0,
             "El tiempo mínimo de inscripción debe ser un número positivo.",
             "tiempo_minimo_inscripcion"),
            (self.tiempo_maximo_input, float, lambda v: v > 0,
             "El tiempo máximo de inscripción debe ser un número positivo.",
             "tiempo_maximo_inscripcion"),
            (self.max_cola_input, int, lambda v: v >= 0,
             "La cantidad máxima de alumnos en cola debe ser un número "
             "no negativo.",
             "max_cola"),
            (self.tiempo_regreso_input, float, lambda v: v > 0,
             "El tiempo de regreso de un alumno debe ser un número "
             "positivo.",
             "tiempo_regreso_alumno"),
            (self.llegada_mantenimiento_input, float, lambda v: v > 0,
             "La media de llegada de mantenimiento debe ser un número "
             "positivo.",
             "media_llegada_mantenimiento"),
            (self.variacion_input, float, lambda v: v >= 0,
             "La variación de llegada de mantenimiento debe ser un "
             "número no negativo.",
             "variacion_llegada_mantenimiento"),
            (self.paso_input, float, lambda v: v > 0,
             "El paso de Euler debe ser un número positivo.",
             "paso_euler"),
        )

        for campo, tipo, es_valido, mensaje, atributo in campos:
            try:
                valor = tipo(campo.text())
                if not es_valido(valor):
                    raise ValueError(mensaje)
            except ValueError:
                # Tanto si tipo() falla (texto no numérico) como si
                # es_valido() rechaza el valor, mostramos el mismo
                # diálogo y cortamos sin tocar self.params.
                ErrorDialog(mensaje).exec()
                return False
            setattr(self.params, atributo, valor)

        return True

    def mostrar_vector_estado(self, vector_estado):
        """Vuelca el vector de estado devuelto por la simulación a la
        tabla: una columna por cada clave del diccionario de fila
        (número de fila, evento, próximos eventos, rnd's, etc.).

        Los alumnos (objetos temporales) se agregan en cada fila con
        columnas Alumno{n}_*, y n varía según cuántos haya en ese
        instante puntual: no todas las filas tienen la misma cantidad de
        claves. Por eso las columnas de la tabla se calculan como la
        UNIÓN de las claves de todas las filas (en el orden en que van
        apareciendo), en vez de tomar nada más que las de la primera
        fila — así la tabla sólo tiene tantas columnas de alumnos como
        el máximo realmente alcanzado, y no columnas vacías de más."""
        tabla = self.tabla_resultado
        if not vector_estado:
            tabla.setRowCount(0)
            tabla.setColumnCount(0)
            return

        columnas = []
        vistas = set()
        for fila in vector_estado:
            for columna in fila:
                if columna not in vistas:
                    vistas.add(columna)
                    columnas.append(columna)

        tabla.setColumnCount(len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setRowCount(len(vector_estado))

        # Evita redibujar la tabla por cada celda: con ventanas grandes
        # (hasta 100000 filas, según el enunciado) eso congela la UI.
        tabla.setUpdatesEnabled(False)
        for fila_idx, fila in enumerate(vector_estado):
            for col_idx, columna in enumerate(columnas):
                # get(): esta fila puede no tener esta columna (por
                # ejemplo, tiene menos alumnos que el máximo de la
                # ventana), en ese caso se muestra vacío.
                valor = QTableWidgetItem(str(fila.get(columna, '')))
                tabla.setItem(fila_idx, col_idx, valor)
        tabla.setUpdatesEnabled(True)

    def mostrar_resultados(self, resultados: dict):
        """Muestra las 3 respuestas finales del enunciado (% que se van,
        ocio promedio del técnico, visitas promedio por día)."""
        texto = " | ".join(
            f"{clave}: {valor}" for clave, valor in resultados.items())
        self.resultados_label.setText(texto)

    # exporta el detalle de cada integración de Euler con referencia a la
    # visita y PC a la que corresponde (pedido por el enunciado)
    def exportar_euler(self):
        # El botón está deshabilitado hasta que haya una simulación
        # corrida, pero el guard queda por las dudas (y para que el
        # checker de tipos sepa que de acá en más no es None).
        if self.ultima_simulacion is None:
            return
        self.ultima_simulacion.exportar_euler_csv()
        QMessageBox.information(
            self, "Exportación completa",
            f"Se exportaron {len(self.ultima_simulacion.euler_log)} "
            f"integraciones de Euler a euler_log.csv")


# Punto de entrada de la app de escritorio.
if __name__ == "__main__":
    app = QApplication([])
    params = Params()
    window = MainWindow(params)
    window.show()
    app.exec()
