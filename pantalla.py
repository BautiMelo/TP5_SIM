from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QLayout, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from params import Params
from error_dialog import ErrorDialog


class MainWindow(QMainWindow):
    def __init__(self, default_params: Params):
        super().__init__()
        self.params: Params = default_params

        self.setWindowTitle("TP5 Simulación")
        self.showMaximized()

        # contenedor principal de todos los elementos ui
        container = QWidget()
        layout = QHBoxLayout()
        container.setLayout(layout)

        # agregar botones a la izquierda
        layout.addLayout(self.crear_layout_parametros(), 3)

        # layout de resultados
        layout.addLayout(QVBoxLayout(), 9)

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

        layout.addLayout(layout_simulacion)
        layout.addLayout(layout_inscripcion)
        layout.addLayout(layout_mantenimiento)
        layout.addLayout(layout_euler)
        layout.addLayout(layout_boton)
        return layout

    # crea los botones para ingresar los parametros de tiempo maximo y filas a mostrar
    def layout_parametros_simulacion(self) -> QLayout:
        layout_simulacion = QVBoxLayout()
        layout_simulacion.setSpacing(10)
        # tiempo maximo
        # titulo
        tiempo_label = QLabel("Tiempo máximo de simulación en minutos:")
        # input
        self.tiempo_input = QLineEdit()
        self.tiempo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_input.setText(str(self.params.tiempo_maximo_simulacion))
        # mostrar desde hora
        # titulo
        mostrar_desde_label = QLabel("Mostrar resultados desde el minuto:")
        # input
        self.mostrar_desde_input = QLineEdit()
        self.mostrar_desde_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.mostrar_desde_input.setText(str(self.params.minutos_desde_que_muestra))
        # cantidad filas
        # titulo
        filas_label = QLabel("Mostrar resultados desde el minuto:")
        # input
        self.filas_input = QLineEdit()
        self.filas_input.setValidator(QIntValidator(0, 10000))
        self.filas_input.setText(str(self.params.filas_a_mostrar))
        # agregar al layout
        layout_simulacion.addWidget(tiempo_label)
        layout_simulacion.addWidget(self.tiempo_input)
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
        self.llegada_input = QLineEdit()
        self.llegada_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.llegada_input.setText(str(self.params.media_llegada_alumnos))
        # tiempo minimo de inscripcion
        # titulo
        tiempo_minimo_label = QLabel("Tiempo mínimo de inscripción en minutos:")
        # input
        self.tiempo_minimo_input = QLineEdit()
        self.tiempo_minimo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_minimo_input.setText(str(self.params.tiempo_minimo_inscripcion))
        # tiempo maximo de inscripcion
        # titulo
        tiempo_maximo_label = QLabel("Tiempo máximo de inscripción en minutos:")
        # input
        self.tiempo_maximo_input = QLineEdit()
        self.tiempo_maximo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.tiempo_maximo_input.setText(str(self.params.tiempo_maximo_inscripcion))
        # agregar al layout
        layout_inscripcion.addWidget(llegada_label)
        layout_inscripcion.addWidget(self.llegada_input)
        layout_inscripcion.addWidget(tiempo_minimo_label)
        layout_inscripcion.addWidget(self.tiempo_minimo_input)
        layout_inscripcion.addWidget(tiempo_maximo_label)
        layout_inscripcion.addWidget(self.tiempo_maximo_input)

        return layout_inscripcion

    # crea los botones para ingresar los parametros de mantenimiento
    def layout_mantenimiento(self) -> QLayout:
        layout_mantenimiento = QVBoxLayout()
        layout_mantenimiento.setSpacing(10)

        # tiempo de llegada
        # titulo
        llegada_label = QLabel("Media de llegada de mantenimiento en minutos:")
        # input
        self.llegada_input = QLineEdit()
        self.llegada_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.llegada_input.setText(str(self.params.media_llegada_mantenimiento))
        # variacion de llegada
        # titulo
        variacion_label = QLabel("Variación de llegada de mantenimiento en minutos:")
        # input
        self.variacion_input = QLineEdit()
        self.variacion_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        self.variacion_input.setText(str(self.params.variacion_llegada_mantenimiento))
        # agregar al layout
        layout_mantenimiento.addWidget(llegada_label)
        layout_mantenimiento.addWidget(self.llegada_input)
        layout_mantenimiento.addWidget(variacion_label)
        layout_mantenimiento.addWidget(self.variacion_input)

        return layout_mantenimiento

    def layout_euler(self):
        layout_euler = QVBoxLayout()
        layout_euler.setSpacing(10)

        # paso de euler
        # titulo
        paso_label = QLabel("Paso de Euler en minutos:")
        # input
        self.paso_input = QLineEdit()
        self.paso_input.setValidator(QDoubleValidator(0.01, 1, 2))
        self.paso_input.setText(str(self.params.paso_euler))
        # agregar al layout
        layout_euler.addWidget(paso_label)
        layout_euler.addWidget(self.paso_input)

        return layout_euler

    def iniciar_simulacion(self):
        self.leer_parametros()

    # lee los campos de input y carga los parametros
    def leer_parametros(self):
        try:
            p = float(self.tiempo_input.text())
            if p <= 0:
                raise ValueError("El tiempo máximo de simulación debe ser un número positivo.")
            self.params.tiempo_maximo_simulacion = p
        except ValueError:
            error = ErrorDialog("El tiempo máximo de simulación debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.mostrar_desde_input.text())
            if p < 0:
                raise ValueError("El minuto desde el que muestran las filas debe ser un número no negativo.")
            self.params.minutos_desde_que_muestra = p
        except ValueError:
            error = ErrorDialog("El minuto desde el que muestran las filas debe ser un número no negativo.")
            error.exec()
            return

        try:
            p = int(self.filas_input.text())
            if p < 0:
                raise ValueError("La cantidad de filas a mostrar debe ser un número no negativo.")
            self.params.filas_a_mostrar = p
        except ValueError:
            error = ErrorDialog("La cantidad de filas a mostrar debe ser un número no negativo.")
            error.exec()
            return

        try:
            p = float(self.llegada_input.text())
            if p <= 0:
                raise ValueError("La media de llegada de alumnos debe ser un número positivo.")
            self.params.media_llegada_alumnos = p
        except ValueError:
            error = ErrorDialog("La media de llegada de alumnos debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.tiempo_minimo_input.text())
            if p <= 0:
                raise ValueError("El tiempo mínimo de inscripción debe ser un número positivo.")
            self.params.tiempo_minimo_inscripcion = p
        except ValueError:
            error = ErrorDialog("El tiempo mínimo de inscripción debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.tiempo_maximo_input.text())
            if p <= 0:
                raise ValueError("El tiempo máximo de inscripción debe ser un número positivo.")
            self.params.tiempo_maximo_inscripcion = p
        except ValueError:
            error = ErrorDialog("El tiempo máximo de inscripción debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.llegada_input.text())
            if p <= 0:
                raise ValueError("La media de llegada de mantenimiento debe ser un número positivo.")
            self.params.media_llegada_mantenimiento = p
        except ValueError:
            error = ErrorDialog("La media de llegada de mantenimiento debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.variacion_input.text())
            if p <= 0:
                raise ValueError("La variación de llegada de mantenimiento debe ser un número positivo.")
            self.params.variacion_llegada_mantenimiento = p
        except ValueError:
            error = ErrorDialog("La variación de llegada de mantenimiento debe ser un número positivo.")
            error.exec()
            return

        try:
            p = float(self.paso_input.text())
            if p <= 0:
                raise ValueError("El paso de Euler debe ser un número positivo.")
            self.params.paso_euler = p
        except ValueError:
            error = ErrorDialog("El paso de Euler debe ser un número positivo.")
            error.exec()
            return


if __name__ == "__main__":
    app = QApplication([])
    params = Params()
    window = MainWindow(params)
    window.show()
    app.exec()