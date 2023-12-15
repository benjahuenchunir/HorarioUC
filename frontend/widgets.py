from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox
    
)
import sys
from backend.models import GroupedSection
import global_constants as c

class DoubleLineWidget(QWidget):
    def __init__(self, text, color):
        super().__init__()
        
        """sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)"""
        self.setStyleSheet("padding :4px")
        self.main_layout = QVBoxLayout()
        label1 = QLabel(text)
        label1.setStyleSheet(f"background-color: {color}; font-weight: bold")
        self.main_layout.addWidget(label1)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
    def addLabel(self, text, color):
        label = QLabel(text)
        label.setStyleSheet(f"background-color: {color}; font-weight: bold")
        self.main_layout.addWidget(label)


class CourseInfoListElement(QWidget):
    def __init__(self, id_, name, secciones, nrc, profesor):
        super().__init__()

        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.lbl_id = QLabel(str(id_), self)
        hbox.addWidget(self.lbl_id)
        self.lbl_name = QLabel(name, self)
        self.lbl_name.setWordWrap(True)
        hbox.addWidget(self.lbl_name)        
        self.lbl_seccion = QLabel("\n".join(map(str, secciones)), self)
        hbox.addWidget(self.lbl_seccion)
        self.lbl_nrc = QLabel("\n".join(map(str, nrc)), self)
        hbox.addWidget(self.lbl_nrc)
        self.lbl_teacher = QLabel("\n".join(profesor), self)
        hbox.addWidget(self.lbl_teacher)


class CourseListElement(QWidget):
    def __init__(self, id_curso, sigla, secciones_agrupadas: list[GroupedSection], senal_borrar_curso, senal_cambiar_seccion):
        super().__init__()
        self.id_curso = id_curso
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        secciones: list[tuple[int, str]] = []
        for seccion_grupo in secciones_agrupadas:
            for seccion, profesor in zip(seccion_grupo[c.SECCIONES], seccion_grupo[c.PROFESORES]):
                secciones.append((seccion, profesor))
        self.lbl_id = QLabel(sigla, self)
        hbox.addWidget(self.lbl_id)
        self.lbl_secciones = QLabel(str(len(secciones)), self)
        hbox.addWidget(self.lbl_secciones)
        self.qcb_section_selection = QComboBox(self)
        hbox.addWidget(self.qcb_section_selection)
        self.btn_delete = QPushButton("Borrar", self)
        hbox.addWidget(self.btn_delete)
        self.qcb_section_selection.addItem("Todas")
        for seccion, profesor in sorted(secciones, key=lambda x: x[0]):
            self.qcb_section_selection.addItem(f"{seccion} - {profesor}")

        self.senal_cambiar_seccion = senal_cambiar_seccion
        self.senal_borrar_curso = senal_borrar_curso
        self.qcb_section_selection.currentIndexChanged.connect(self.cambiar_seccion)
        self.btn_delete.clicked.connect(self.borrar)

    def cambiar_seccion(self, indice):
        self.senal_cambiar_seccion.emit(self.id_curso, indice)

    def borrar(self):
        self.senal_borrar_curso.emit(self.id_curso)

class CourseFilters(QWidget):
    def __init__(self, senal_campus, senal_creditos) -> None:
        super().__init__()
        self.senal_campus = senal_campus
        self.senal_creditos = senal_creditos

        layout_filters = QHBoxLayout()
        self.setLayout(layout_filters)
        self.qcb_campus_filter = QComboBox(self)
        self.qcb_campus_filter.addItems(map(lambda x: x.replace("+", " "), c.CAMPUS))
        self.qcb_credits_filter = QComboBox(self)
        self.qcb_credits_filter.addItems(map(str, c.CREDITOS))
        layout_filters.addWidget(self.qcb_campus_filter)
        layout_filters.addWidget(self.qcb_credits_filter)

        self.qcb_campus_filter.currentTextChanged.connect(lambda x: self.senal_campus.emit(x))
        self.qcb_credits_filter.currentTextChanged.connect(lambda x: self.senal_creditos.emit(x))


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)

    sys.exit(app.exec())
