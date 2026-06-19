from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class ErrorDialog(QDialog):
    """Ventanita simple para mostrar un mensaje de validación al usuario
    (ej: "el tiempo máximo debe ser positivo"). La usa pantalla.py en
    leer_parametros() cuando algún campo no pasa la validación."""

    def __init__(self, mensaje):
        super().__init__()
        self.setWindowTitle("Error")
        self.setMinimumSize(300, 150)

        layout = QVBoxLayout()
        label_mensaje = QLabel(mensaje)
        layout.addWidget(label_mensaje)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)

        self.setLayout(layout)
