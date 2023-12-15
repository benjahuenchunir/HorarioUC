from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QColor
import frontend.constants as p
import global_constants as gc
from frontend.widgets import DoubleLineWidget, CourseInfoListElement

class OFGWindow(QWidget):
    senal_cambiar_area = pyqtSignal(str)
    senal_volver = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.course_list = []
        self.__current_course_index = 0
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.setStyleSheet(p.DARK_MODE)

        self.btn_back = QPushButton("Volver", self)
        layout.addWidget(self.btn_back)
        self.qcb_ofg_areas = QComboBox(self)
        self.qcb_ofg_areas.addItem("-")
        for area in gc.OFG:
            self.qcb_ofg_areas.addItem(area)
        self.lbl_combinations = QLabel(self)
        layout.addWidget(self.qcb_ofg_areas)
        layout.addWidget(self.lbl_combinations)

        layout_btn = QHBoxLayout()
        self.btn_previous = QPushButton("Anterior", self)
        self.btn_previous.setEnabled(False)
        self.lbl_current_ofg = QLabel(self)
        self.btn_next = QPushButton("Siguiente", self)
        self.btn_next.setEnabled(False)
        layout_btn.addWidget(self.btn_previous)
        layout_btn.addWidget(self.lbl_current_ofg)
        layout_btn.addWidget(self.btn_next)
        layout.addLayout(layout_btn)
        layout_courses = QHBoxLayout()
        self.tb_schedule = QTableWidget(self)
        self.tb_schedule.setColumnCount(5)
        self.tb_schedule.setRowCount(9)
        self.tb_schedule.setRowHeight(4, 1)
        self.tb_schedule.setVerticalHeaderLabels(p.H_LABELS_HORARIO)
        self.tb_schedule.setHorizontalHeaderLabels(p.DIAS.keys())
        self.set_lunch_line()
        self.list_current_courses = QListWidget(self)
        layout_courses.addWidget(self.tb_schedule)
        layout_courses.addWidget(self.list_current_courses)
        layout.addLayout(layout_courses)

        self.update_combinations_label()
        self.btn_next.clicked.connect(self.increase_current_index)
        self.btn_previous.clicked.connect(self.decrease_current_index)
        self.qcb_ofg_areas.currentTextChanged.connect(self.enviar_cambiar_area)
        self.btn_back.clicked.connect(lambda x: self.senal_volver.emit())

    @property
    def current_course_index(self):
        return self.__current_course_index

    @current_course_index.setter
    def current_course_index(self, value):
        self.__current_course_index = max(0, min(value, len(self.course_list) - 1))

    def iniciar(self):
        self.lbl_combinations.clear()
        self.lbl_current_ofg.clear()
        self.list_current_courses.clear()
        self.tb_schedule.clearContents()
        self.qcb_ofg_areas.setCurrentIndex(0)
        self.show()

    def set_lunch_line(self):
        for j in range(self.tb_schedule.columnCount()):
            self.tb_schedule.setItem(4, j, QTableWidgetItem())
            self.tb_schedule.item(4, j).setBackground(QColor(224, 224, 224))

    def add_course_schedule(self, course):
        self.add_item(course.id, course.sections, course.catedra.items(), p.COLORES[p.CATEDRA])
        self.add_item(course.id, course.sections, course.ayudantia.items(), p.COLORES[p.AYUDANTIA])
        self.add_item(course.id, course.sections, course.lab.items(), p.COLORES[p.LAB])
        self.add_item(course.id, course.sections, course.taller.items(), p.COLORES[p.TALLER])

    def add_item(self, course_id, sections, items, color):
        for dia, modulos in items:
            for modulo in modulos:
                if modulo <= 4:
                    modulo -= 1
                if self.tb_schedule.cellWidget(modulo, p.DIAS[dia]):
                    self.tb_schedule.cellWidget(modulo, p.DIAS[dia]).addLabel(f"{course_id}-{','.join(sections)}", color)
                else:
                    item = DoubleLineWidget(f"{course_id}-{','.join(sections)}", color)
                    self.tb_schedule.setCellWidget(modulo, p.DIAS[dia], item)

    def increase_current_index(self):
        self.current_course_index += 1
        if self.current_course_index == len(self.course_list) - 1:
            self.btn_next.setEnabled(False)
        self.btn_previous.setEnabled(True)
        self.update_schedule()

    def decrease_current_index(self):
        self.current_course_index -= 1
        if self.current_course_index == 0:
            self.btn_previous.setEnabled(False)
        self.btn_next.setEnabled(True)
        self.update_schedule()

    def update_schedule(self):
        self.list_current_courses.clear()
        self.tb_schedule.clearContents()
        self.set_lunch_line()
        id_, combinacion = self.course_list[self.current_course_index]
        self.lbl_current_ofg.setText(id_)
        for course in combinacion:
            self.add_course_schedule(course)
            item = QListWidgetItem()
            item.setSizeHint(QSize(100, 80))
            self.list_current_courses.addItem(item)
            self.list_current_courses.setItemWidget(item, CourseInfoListElement(course.id, course.name, course.sections, course.nrcs, course.teachers))

    def update_ofgs(self, ofgs: list):
        self.course_list = ofgs
        self.current_course_index = 0
        self.update_combinations_label()
        self.update_schedule()
        self.btn_previous.setEnabled(False)
        self.btn_next.setEnabled(True)
        if self.current_course_index == len(self.course_list) - 1:
            self.btn_next.setEnabled(False)

    def update_combinations_label(self):
        self.lbl_combinations.setText(f"{len(self.course_list)} combinaciones")

    def enviar_cambiar_area(self, area):
        if area != "-":
            self.senal_cambiar_area.emit(area)