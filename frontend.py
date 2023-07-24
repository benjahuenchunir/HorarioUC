from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QListWidget,
    QLineEdit,
    QListWidgetItem,
    QComboBox
)
from PyQt5.QtCore import pyqtSignal, QSize
import parametros as p
import sys


class DoubleLineWidget(QWidget):
    def __init__(self, text, color):
        super().__init__()
        
        """sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)"""

        self.main_layout = QVBoxLayout()
        label1 = QLabel(text)
        label1.setStyleSheet(f"background-color: {color}")
        self.main_layout.addWidget(label1)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
    def addLabel(self, text, color):
        label = QLabel(text)
        label.setStyleSheet(f"background-color: {color}")
        self.main_layout.addWidget(label)


class CourseInfoListElement(QWidget):
    def __init__(self, id_, seccion, nrc, profesor):
        super().__init__()

        hbox = QHBoxLayout()
        self.setLayout(hbox)

        self.lbl_id = QLabel(id_, self)
        hbox.addWidget(self.lbl_id)
        self.lbl_seccion = QLabel("\n".join(seccion), self)
        hbox.addWidget(self.lbl_seccion)
        self.lbl_nrc = QLabel("\n".join(nrc), self)
        hbox.addWidget(self.lbl_nrc)
        self.lbl_teacher = QLabel("\n".join(profesor), self)
        hbox.addWidget(self.lbl_teacher)


class CourseListElement(QWidget):
    def __init__(self, id_, secciones, senal_borrar_curso, senal_cambiar_seccion):
        super().__init__()

        hbox = QHBoxLayout()
        self.setLayout(hbox)

        self.lbl_id = QLabel(id_, self)
        hbox.addWidget(self.lbl_id)
        self.lbl_secciones = QLabel(str(len(secciones)), self)
        hbox.addWidget(self.lbl_secciones)
        self.qcb_section_selection = QComboBox(self)
        hbox.addWidget(self.qcb_section_selection)
        self.btn_delete = QPushButton("Borrar", self)
        hbox.addWidget(self.btn_delete)

        self.qcb_section_selection.addItem("Todas")
        for seccion in sorted(secciones, key=lambda x: int(x.section)):
            self.qcb_section_selection.addItem(f"{seccion.section} - {seccion.teacher}")

        self.senal_cambiar_seccion = senal_cambiar_seccion
        self.senal_borrar_curso = senal_borrar_curso
        self.qcb_section_selection.currentIndexChanged.connect(self.cambiar_seccion)
        self.btn_delete.clicked.connect(self.borrar)

    def cambiar_seccion(self, indice):
        self.senal_cambiar_seccion.emit(self.lbl_id.text(), indice)

    def borrar(self):
        self.senal_borrar_curso.emit(self.lbl_id.text())


class ScheduleWindow(QWidget):
    senal_buscar_sigla = pyqtSignal(str)
    senal_borrar_curso = pyqtSignal(str)
    senal_cambiar_seccion = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.course_list = []
        self.current_course_index = 0
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout_add = QHBoxLayout()
        self.txt_sigla = QLineEdit(self)
        self.btn_add = QPushButton("Agregar", self)
        layout_add.addWidget(self.txt_sigla)
        layout_add.addWidget(self.btn_add)
        layout.addLayout(layout_add)

        self.list_courses = QListWidget(self)
        self.lbl_combinations = QLabel(self)
        layout.addWidget(self.list_courses)
        layout.addWidget(self.lbl_combinations)

        layout_btn = QHBoxLayout()
        self.btn_previous = QPushButton("Anterior", self)
        self.btn_previous.setEnabled(False)
        self.lbl_current_index = QLabel(self)
        self.btn_next = QPushButton("Siguiente", self)
        self.btn_next.setEnabled(False)
        layout_btn.addWidget(self.btn_previous)
        layout_btn.addWidget(self.lbl_current_index)
        layout_btn.addWidget(self.btn_next)
        layout.addLayout(layout_btn)
        layout_courses = QHBoxLayout()
        self.tb_schedule = QTableWidget(self)
        self.tb_schedule.setColumnCount(5)
        self.tb_schedule.setHorizontalHeaderLabels(p.DIAS.keys())
        self.tb_schedule.setRowCount(8)
        self.list_current_courses = QListWidget(self)
        layout_courses.addWidget(self.tb_schedule)
        layout_courses.addWidget(self.list_current_courses)
        layout.addLayout(layout_courses)

        self.update_current_index_label()
        self.update_combinations_label()
        self.btn_add.clicked.connect(self.buscar_sigla)
        self.btn_next.clicked.connect(self.increase_current_index)
        self.btn_previous.clicked.connect(self.decrease_current_index)

    def addItem(self, course):
        for dia, modulos in course.catedra.items():
            for modulo in modulos:
                if self.tb_schedule.cellWidget(modulo, p.DIAS[dia]):
                    self.tb_schedule.cellWidget(modulo, p.DIAS[dia]).addLabel(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.CATEDRA])
                else:
                    item = DoubleLineWidget(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.CATEDRA])
                    self.tb_schedule.setCellWidget(modulo, p.DIAS[dia], item)

        for dia, modulos in course.lab.items():
            for modulo in modulos:
                if self.tb_schedule.cellWidget(modulo, p.DIAS[dia]):
                    self.tb_schedule.cellWidget(modulo, p.DIAS[dia]).addLabel(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.LAB])
                else:
                    item = DoubleLineWidget(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.LAB])
                    self.tb_schedule.setCellWidget(modulo, p.DIAS[dia], item)
        for dia, modulos in course.ayudantia.items():
            for modulo in modulos:
                if self.tb_schedule.cellWidget(modulo, p.DIAS[dia]):
                    self.tb_schedule.cellWidget(modulo, p.DIAS[dia]).addLabel(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.AYUDANTIA])
                else:
                    item = DoubleLineWidget(f"{course.id}-{','.join(course.sections)}", p.COLORES[p.AYUDANTIA])
                    self.tb_schedule.setCellWidget(modulo, p.DIAS[dia], item)

    def increase_current_index(self):
        self.current_course_index = self.current_course_index + 1
        if self.current_course_index == len(self.course_list) - 1:
            self.btn_next.setEnabled(False)
        self.btn_previous.setEnabled(True)
        self.update_schedule()
        self.update_current_index_label()

    def decrease_current_index(self):
        self.current_course_index = self.current_course_index - 1
        if self.current_course_index == 0:
            self.btn_previous.setEnabled(False)
        self.btn_next.setEnabled(True)
        self.update_schedule()
        self.update_current_index_label()

    def update_schedule(self):
        self.list_current_courses.clear()
        self.tb_schedule.clear()
        self.tb_schedule.setHorizontalHeaderLabels(p.DIAS.keys())
        for course in self.course_list[self.current_course_index]:
            self.addItem(course)
            item = QListWidgetItem()
            item.setSizeHint(QSize(100, 80))
            self.list_current_courses.addItem(item)
            self.list_current_courses.setItemWidget(item, CourseInfoListElement(course.id, course.sections, course.nrcs, course.teachers))

    def new_schedule(self, combinations): # TODO falta eliminar curso de la lista principal al apretar borrar
        self.course_list = combinations
        self.current_course_index = 0
        self.update_current_index_label()
        self.update_combinations_label()
        self.update_schedule()
        self.btn_next.setEnabled(True)
        if self.current_course_index == len(self.course_list) - 1:
            self.btn_next.setEnabled(False)

    def update_current_index_label(self):
        self.lbl_current_index.setText(f"Combinacion {self.current_course_index + 1}")

    def update_combinations_label(self):
        self.lbl_combinations.setText(f"{len(self.course_list)} combinaciones")

    def buscar_sigla(self):
        sigla = self.txt_sigla.text()
        if sigla != "":
            self.senal_buscar_sigla.emit(sigla)

    def add_course(self, course):
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 80))
        self.list_courses.addItem(item)
        self.list_courses.setItemWidget(item, CourseListElement(course.id, course.sections, self.senal_borrar_curso, self.senal_cambiar_seccion))

    def delete_course(self, course_id):
        for i in range(self.list_courses.count()):
            item = self.list_courses.item(i)
            widget = self.list_courses.itemWidget(item)
            if widget.lbl_id.text() == course_id:
                self.list_courses.takeItem(self.list_courses.row(item))
                del item
                break


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = CourseInfoListElement("test", "test", "test", "test")
    main.show()

    sys.exit(app.exec())
