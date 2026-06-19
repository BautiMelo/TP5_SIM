from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class ErrorDialog(QDialog):
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