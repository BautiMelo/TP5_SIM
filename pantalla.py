from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
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

from params import Params
from simulacion import SimulacionInscripcion


class MainWindow(QMainWindow):
    def __init__(self, default_params: Params):
        super().__init__()
        self.params: Params = default_params
        self.inputs: dict[str, QLineEdit] = {}

        self.setWindowTitle("TP5 Simulación")
        self.showMaximized()

        # contenedor principal de todos los elementos ui
        container = QWidget()
        layout = QHBoxLayout()
        container.setLayout(layout)

        # agregar botones a la izquierda
        layout.addLayout(self.crear_layout_parametros(), 3)

        # layout de resultados
        layout.addLayout(self.crear_layout_resultados(), 9)

        self.setCentralWidget(container)

    # crea un QLineEdit numérico, lo registra en self.inputs y lo agrega
    # al layout junto con su etiqueta
    def agregar_campo(
            self, layout: QLayout, nombre: str, etiqueta: str,
            valor_inicial, minimo=0.01, maximo=100000.0):
        layout.addWidget(QLabel(etiqueta))
        campo = QLineEdit()
        campo.setValidator(QDoubleValidator(minimo, maximo, 4))
        campo.setText(str(valor_inicial))
        layout.addWidget(campo)
        self.inputs[nombre] = campo

    # crea los botones para ingresar los parametros
    def crear_layout_parametros(self) -> QLayout:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(40)

        titulo = QLabel("Parámetros de la simulación")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold")
        layout.addWidget(titulo)

        layout.addLayout(self.layout_parametros_simulacion())
        layout.addLayout(self.layout_parametros_inscripcion())
        layout.addLayout(self.layout_mantenimiento())
        layout.addLayout(self.layout_euler())

        boton_simular = QPushButton("Simular")
        boton_simular.clicked.connect(self.ejecutar_simulacion)
        layout.addWidget(boton_simular)

        return layout

    # parametros de tiempo maximo, cantidad de iteraciones y ventana
    # de filas a mostrar
    def layout_parametros_simulacion(self) -> QLayout:
        layout_simulacion = QVBoxLayout()
        layout_simulacion.setSpacing(10)

        self.agregar_campo(
            layout_simulacion, "tiempo_maximo_simulacion",
            "Tiempo máximo de simulación en minutos (X):",
            self.params.tiempo_maximo_simulacion)
        self.agregar_campo(
            layout_simulacion, "iteraciones_maximas",
            "Cantidad máxima de iteraciones (N):",
            self.params.iteraciones_maximas, minimo=1, maximo=100000)
        self.agregar_campo(
            layout_simulacion, "minutos_desde_que_muestra",
            "Mostrar resultados desde el minuto (j):",
            self.params.minutos_desde_que_muestra, minimo=0)
        self.agregar_campo(
            layout_simulacion, "filas_a_mostrar",
            "Cantidad de filas a mostrar (i):",
            self.params.filas_a_mostrar, minimo=0, maximo=100000)

        return layout_simulacion

    # crea los campos para ingresar los parametros de los alumnos
    def layout_parametros_inscripcion(self) -> QLayout:
        layout_inscripcion = QVBoxLayout()
        layout_inscripcion.setSpacing(10)

        self.agregar_campo(
            layout_inscripcion, "media_llegada_alumnos",
            "Media de llegada de alumnos en minutos:",
            self.params.media_llegada_alumnos)
        self.agregar_campo(
            layout_inscripcion, "tiempo_minimo_inscripcion",
            "Tiempo mínimo de inscripción en minutos:",
            self.params.tiempo_minimo_inscripcion)
        self.agregar_campo(
            layout_inscripcion, "tiempo_maximo_inscripcion",
            "Tiempo máximo de inscripción en minutos:",
            self.params.tiempo_maximo_inscripcion)
        self.agregar_campo(
            layout_inscripcion, "max_cola",
            "Cantidad máxima de alumnos en cola:",
            self.params.max_cola, minimo=0, maximo=1000)
        self.agregar_campo(
            layout_inscripcion, "tiempo_regreso_alumno",
            "Tiempo de regreso de un alumno en minutos:",
            self.params.tiempo_regreso_alumno)

        return layout_inscripcion

    # crea los campos para ingresar los parametros de mantenimiento
    def layout_mantenimiento(self) -> QLayout:
        layout_mantenimiento = QVBoxLayout()
        layout_mantenimiento.setSpacing(10)

        self.agregar_campo(
            layout_mantenimiento, "media_llegada_mantenimiento",
            "Media de llegada de mantenimiento en minutos:",
            self.params.media_llegada_mantenimiento)
        self.agregar_campo(
            layout_mantenimiento, "variacion_llegada_mantenimiento",
            "Variación de llegada de mantenimiento en minutos:",
            self.params.variacion_llegada_mantenimiento, minimo=0)

        return layout_mantenimiento

    def layout_euler(self) -> QLayout:
        layout_euler = QVBoxLayout()
        layout_euler.setSpacing(10)

        self.agregar_campo(
            layout_euler, "paso_euler",
            "Paso de Euler en minutos (h):",
            self.params.paso_euler, minimo=0.01, maximo=1.0)

        return layout_euler

    # layout donde se muestran la tabla del vector de estado y los
    # resultados finales pedidos por el enunciado
    def crear_layout_resultados(self) -> QLayout:
        layout = QVBoxLayout()

        self.resultados_label = QLabel(
            "Configure los parámetros y presione \"Simular\".")
        layout.addWidget(self.resultados_label)

        self.boton_exportar_euler = QPushButton(
            "Exportar integración de Euler (CSV)")
        self.boton_exportar_euler.clicked.connect(self.exportar_euler)
        self.boton_exportar_euler.setEnabled(False)
        layout.addWidget(self.boton_exportar_euler)

        self.tabla_resultado = QTableWidget()
        layout.addWidget(self.tabla_resultado)

        return layout

    # nombres de self.inputs que representan parámetros enteros (el resto
    # son float); los nombres coinciden 1 a 1 con los atributos de Params
    CAMPOS_ENTEROS = {"iteraciones_maximas", "filas_a_mostrar", "max_cola"}

    # lee los valores ingresados y los vuelca sobre self.params
    def actualizar_params_desde_inputs(self):
        for nombre, campo in self.inputs.items():
            tipo = int if nombre in self.CAMPOS_ENTEROS else float
            setattr(self.params, nombre, tipo(float(campo.text())))

    # corre la simulación con los parámetros actuales y muestra el
    # vector de estado y los resultados finales
    def ejecutar_simulacion(self):
        try:
            self.actualizar_params_desde_inputs()
        except ValueError:
            QMessageBox.warning(
                self, "Parámetros inválidos",
                "Revisá que todos los campos tengan un número válido.")
            return

        self.ultima_simulacion = SimulacionInscripcion.desde_params(
            self.params)
        vector_estado = self.ultima_simulacion.ejecutar_simulacion()
        self.mostrar_vector_estado(vector_estado)
        self.mostrar_resultados(self.ultima_simulacion.calcular_resultados())
        self.boton_exportar_euler.setEnabled(
            bool(self.ultima_simulacion.euler_log))

    def mostrar_vector_estado(self, vector_estado):
        tabla = self.tabla_resultado
        if not vector_estado:
            tabla.setRowCount(0)
            tabla.setColumnCount(0)
            return

        columnas = list(vector_estado[0].keys())
        tabla.setColumnCount(len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setRowCount(len(vector_estado))

        # Evita redibujar la tabla por cada celda: con ventanas grandes
        # (hasta 100000 filas, según el enunciado) eso congela la UI.
        tabla.setUpdatesEnabled(False)
        for fila_idx, fila in enumerate(vector_estado):
            for col_idx, columna in enumerate(columnas):
                valor = QTableWidgetItem(str(fila[columna]))
                tabla.setItem(fila_idx, col_idx, valor)
        tabla.setUpdatesEnabled(True)

    def mostrar_resultados(self, resultados: dict):
        texto = " | ".join(
            f"{clave}: {valor}" for clave, valor in resultados.items())
        self.resultados_label.setText(texto)

    # exporta el detalle de cada integración de Euler con referencia a la
    # visita y PC a la que corresponde (pedido por el enunciado)
    def exportar_euler(self):
        self.ultima_simulacion.exportar_euler_csv()
        QMessageBox.information(
            self, "Exportación completa",
            f"Se exportaron {len(self.ultima_simulacion.euler_log)} "
            f"integraciones de Euler a euler_log.csv")


if __name__ == "__main__":
    app = QApplication([])
    params = Params()
    window = MainWindow(params)
    window.show()
    app.exec()
