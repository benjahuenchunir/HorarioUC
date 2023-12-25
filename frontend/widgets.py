import textwrap
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGroupBox,
    QCheckBox,
    QFormLayout
)
from PyQt5.QtCore import Qt
import sys
from backend.models import GroupedSection, Course
import global_constants as c
import frontend.constants as p
from PyQt5.QtGui import QFont


class BackgroundQLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: #2b2b2b")


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

# class GroupedSection(TypedDict):
#     id_curso: int
#     sigla: str
#     secciones: list[int]
#     nrcs: list[int]
#     profesores: list[str]
#     campuses: list[str]
#     en_ingles: list[bool]
#     formatos: list[str]
#     horario: dict[str, dict]

class CustomTooltip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip)
        self.setLayout(QVBoxLayout())
        self.label = QLabel(self)
        self.layout().addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class CourseInfoListHeader(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        font = QFont()
        font.setBold(True)
        self.lbl_id = QLabel("SIGLA", self)
        self.lbl_id.setFont(font)
        self.lbl_id.setFixedWidth(100)
        hbox.addWidget(self.lbl_id)
        self.lbl_name = QLabel("NOMBRE", self)
        self.lbl_name.setFont(font)
        self.lbl_name.setFixedWidth(100)
        hbox.addWidget(self.lbl_name)
        self.lbl_seccion = QLabel("SECCION", self)
        self.lbl_seccion.setFont(font)
        self.lbl_seccion.setFixedWidth(100)
        hbox.addWidget(self.lbl_seccion)
        self.lbl_nrc = QLabel("NRC", self)
        self.lbl_nrc.setFont(font)
        self.lbl_nrc.setFixedWidth(100)
        hbox.addWidget(self.lbl_nrc)
        self.lbl_teacher = QLabel("PROFESOR", self)
        self.lbl_teacher.setFont(font)
        self.lbl_teacher.setFixedWidth(100)
        hbox.addWidget(self.lbl_teacher)

class CourseInfoListElement(QWidget):
    def __init__(self, grouped_section: GroupedSection):
        super().__init__()
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.lbl_id = QLabel(str(grouped_section[c.SIGLA]), self)
        self.lbl_id.setFixedWidth(100)
        hbox.addWidget(self.lbl_id)
        self.lbl_name = QLabel(grouped_section[c.NOMBRE], self)
        self.lbl_name.setFixedWidth(100)
        self.lbl_name.setWordWrap(True)
        hbox.addWidget(self.lbl_name)        
        self.lbl_seccion = QLabel("\n".join(map(str, grouped_section[c.SECCIONES])), self)
        self.lbl_seccion.setFixedWidth(100)
        hbox.addWidget(self.lbl_seccion)
        self.lbl_nrc = QLabel("\n".join(map(str, grouped_section[c.NRCS])), self)
        self.lbl_nrc.setFixedWidth(100)
        hbox.addWidget(self.lbl_nrc)
        self.lbl_teacher = QLabel("\n".join(grouped_section[c.PROFESORES]), self)
        self.lbl_teacher.setFixedWidth(100)
        hbox.addWidget(self.lbl_teacher)

        extra_data = """
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
        </style>
        <table>
            <tr>
                <th>Seccion</th>
                <th>Campus</th>
                <th>En Ingles</th>
                <th>Formato</th>
            </tr>
        """
        for seccion, campus, en_ingles, formato in zip(grouped_section[c.SECCIONES], grouped_section[c.CAMPUSES], grouped_section[c.EN_INGLES], grouped_section[c.FORMATOS]):
            extra_data += f"<tr><td>{seccion}</td><td>{campus}</td><td>{p.BOOL_TO_STR[en_ingles]}</td><td>{formato}</td></tr>"
        extra_data += "</table>"

        self.tooltip = CustomTooltip(self)
        self.tooltip.setText(extra_data)

    def enterEvent(self, event):
        self.tooltip.move(event.globalPos())
        self.tooltip.show()

    def leaveEvent(self, event):
        self.tooltip.hide()

class CourseListElement(QWidget):
    def __init__(self, curso: Course, secciones_agrupadas: list[GroupedSection], senal_borrar_curso, senal_cambiar_seccion):
        super().__init__()
        self.id_curso = curso[c.ID]
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        secciones: list[tuple[int, str]] = []
        for seccion_grupo in secciones_agrupadas:
            for seccion, profesor in zip(seccion_grupo[c.SECCIONES], seccion_grupo[c.PROFESORES]):
                secciones.append((seccion, profesor))
        self.lbl_id = QLabel(curso[c.SIGLA], self)
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
        
        wrapped_description = '<br>'.join(textwrap.wrap(curso[c.DESCRIPCION], width=80))
        extra_data = f"<b>Permite Retiro:</b> {p.BOOL_TO_STR[curso[c.PERMITE_RETIRO]]}<br><b>Aprob Especial:</b> {p.BOOL_TO_STR[curso[c.APROB_ESPECIAL]]}<br><b>Area:</b> {curso[c.AREA]}<br><b>Creditos:</b> {curso[c.CREDITOS]}<br><b>Descripcion:</b> {wrapped_description}"
        self.tooltip = CustomTooltip(self)
        self.tooltip.setText(extra_data)

    def cambiar_seccion(self, indice):
        self.senal_cambiar_seccion.emit(self.id_curso, indice)

    def borrar(self):
        self.senal_borrar_curso.emit(self.id_curso)
    
    def enterEvent(self, event):
        self.tooltip.move(event.globalPos())
        self.tooltip.show()

    def leaveEvent(self, event):
        self.tooltip.hide()
    
    def update_section(self, seccion):
        self.qcb_section_selection.setCurrentIndex(seccion)
    
class FilterComboBox(QComboBox):
    def __init__(self, options: list[str], senal: QtCore.pyqtBoundSignal, parent=None):
        super().__init__(parent)
        self.addItems(options)
        self.currentTextChanged.connect(lambda x: senal.emit())

class TopesFilter(QGroupBox):
    def __init__(self, parent = None) -> None:
        super().__init__("Topes", parent)
        checkbox_layout = QVBoxLayout(self)
        checkbox1 = QCheckBox("Catedra + Catedra", self)
        checkbox2 = QCheckBox("Catedra + Ayudantia", self)
        checkbox3 = QCheckBox("Catedra + Lab", self)
        checkbox4 = QCheckBox("Ayudantia + Ayudantia", self)
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addWidget(checkbox3)
        checkbox_layout.addWidget(checkbox4)


class OFGInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QFormLayout(self)

        self.sigla_label = BackgroundQLabel('<h1>-</h1>')
        self.name_label = BackgroundQLabel('<h1>-</h1>')
        self.creditos_label = BackgroundQLabel()
        self.permite_retiro_label = BackgroundQLabel()
        self.aprob_especial_label = BackgroundQLabel()
        self.descripcion_label = BackgroundQLabel()
        self.descripcion_label.setWordWrap(True)

        self.layout.addRow(self.sigla_label)
        self.layout.addRow(self.name_label)
        self.layout.addRow("Creditos:", self.creditos_label)
        self.layout.addRow("Permite Retiro:", self.permite_retiro_label)
        self.layout.addRow("Aprob Especial:", self.aprob_especial_label)
        self.layout.addRow("Descripcion:", self.descripcion_label)

    def set_course_info(self, course_info):
        self.sigla_label.setText(f"<h1>{course_info[c.SIGLA]}</h1>")
        self.name_label.setText(f"<h1>{course_info[c.NOMBRE]}</h1>")
        self.permite_retiro_label.setText(p.BOOL_TO_STR[course_info[c.PERMITE_RETIRO]])
        self.aprob_especial_label.setText(p.BOOL_TO_STR[course_info[c.APROB_ESPECIAL]])
        self.creditos_label.setText(str(course_info[c.CREDITOS]))
        self.descripcion_label.setText(course_info[c.DESCRIPCION])
    
    def clear(self):
        self.sigla_label.setText('<h1>-</h1>')
        self.name_label.setText('<h1>-</h1>')
        self.creditos_label.setText("")
        self.permite_retiro_label.setText("")
        self.aprob_especial_label.setText("")
        self.descripcion_label.setText("")


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)

    sys.exit(app.exec())
