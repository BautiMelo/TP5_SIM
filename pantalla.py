from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QLayout, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtGui import QDoubleValidator
from params import Params


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

        layout.addLayout(layout_simulacion)
        layout.addLayout(layout_inscripcion)
        layout.addLayout(layout_mantenimiento)
        layout.addLayout(layout_euler)
        return layout

    # crea los botones para ingresar los parametros de tiempo maximo y filas a mostrar
    def layout_parametros_simulacion(self) -> QLayout:
        layout_simulacion = QVBoxLayout()
        layout_simulacion.setSpacing(10)
        # tiempo maximo
        # titulo
        tiempo_label = QLabel("Tiempo máximo de simulación en minutos:")
        # input
        tiempo_input = QLineEdit()
        tiempo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        tiempo_input.setText(str(self.params.tiempo_maximo_simulacion))
        # mostrar desde hora
        # titulo
        mostrar_desde_label = QLabel("Mostrar resultados desde el minuto:")
        # input
        mostrar_desde_input = QLineEdit()
        mostrar_desde_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        mostrar_desde_input.setText(str(self.params.minutos_desde_que_muestra))
        # cantidad filas
        # titulo
        filas_label = QLabel("Mostrar resultados desde el minuto:")
        # input
        filas_input = QLineEdit()
        filas_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        filas_input.setText(str(self.params.filas_a_mostrar))
        # agregar al layout
        layout_simulacion.addWidget(tiempo_label)
        layout_simulacion.addWidget(tiempo_input)
        layout_simulacion.addWidget(mostrar_desde_label)
        layout_simulacion.addWidget(mostrar_desde_input)
        layout_simulacion.addWidget(filas_label)
        layout_simulacion.addWidget(filas_input)

        return layout_simulacion

    # crea los botones para ingresar los parametros de los alumnos
    def layout_parametros_inscripcion(self) -> QLayout:
        layout_inscripcion = QVBoxLayout()
        layout_inscripcion.setSpacing(10)

        # tiempo de llegada
        # titulo
        llegada_label = QLabel("Media de llegada de alumnos en minutos:")
        # input
        llegada_input = QLineEdit()
        llegada_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        llegada_input.setText(str(self.params.media_llegada_alumnos))
        # tiempo minimo de inscripcion
        # titulo
        tiempo_minimo_label = QLabel("Tiempo mínimo de inscripción en minutos:")
        # input
        tiempo_minimo_input = QLineEdit()
        tiempo_minimo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        tiempo_minimo_input.setText(str(self.params.tiempo_minimo_inscripcion))
        # tiempo maximo de inscripcion
        # titulo
        tiempo_maximo_label = QLabel("Tiempo máximo de inscripción en minutos:")
        # input
        tiempo_maximo_input = QLineEdit()
        tiempo_maximo_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        tiempo_maximo_input.setText(str(self.params.tiempo_maximo_inscripcion))
        # agregar al layout
        layout_inscripcion.addWidget(llegada_label)
        layout_inscripcion.addWidget(llegada_input)
        layout_inscripcion.addWidget(tiempo_minimo_label)
        layout_inscripcion.addWidget(tiempo_minimo_input)
        layout_inscripcion.addWidget(tiempo_maximo_label)
        layout_inscripcion.addWidget(tiempo_maximo_input)

        return layout_inscripcion

    # crea los botones para ingresar los parametros de mantenimiento
    def layout_mantenimiento(self) -> QLayout:
        layout_mantenimiento = QVBoxLayout()
        layout_mantenimiento.setSpacing(10)

        # tiempo de llegada
        # titulo
        llegada_label = QLabel("Media de llegada de mantenimiento en minutos:")
        # input
        llegada_input = QLineEdit()
        llegada_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        llegada_input.setText(str(self.params.media_llegada_mantenimiento))
        # variacion de llegada
        # titulo
        variacion_label = QLabel("Variación de llegada de mantenimiento en minutos:")
        # input
        variacion_input = QLineEdit()
        variacion_input.setValidator(QDoubleValidator(0.01, 10000.0, 2))
        variacion_input.setText(str(self.params.variacion_llegada_mantenimiento))
        # agregar al layout
        layout_mantenimiento.addWidget(llegada_label)
        layout_mantenimiento.addWidget(llegada_input)
        layout_mantenimiento.addWidget(variacion_label)
        layout_mantenimiento.addWidget(variacion_input)

        return layout_mantenimiento

    def layout_euler(self):
        layout_euler = QVBoxLayout()
        layout_euler.setSpacing(10)

        # paso de euler
        # titulo
        paso_label = QLabel("Paso de Euler en minutos:")
        # input
        paso_input = QLineEdit()
        paso_input.setValidator(QDoubleValidator(0.01, 1, 2))
        paso_input.setText(str(self.params.paso_euler))
        # agregar al layout
        layout_euler.addWidget(paso_label)
        layout_euler.addWidget(paso_input)

        return layout_euler


if __name__ == "__main__":
    app = QApplication([])
    params = Params()
    window = MainWindow(params)
    window.show()
    app.exec()