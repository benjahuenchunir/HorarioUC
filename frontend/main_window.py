import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QApplication,
    QAbstractItemView,
    QCompleter,
    QMainWindow,
    QMenuBar,
    QAction,
    QDockWidget
)
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QDir
from PyQt5.QtGui import QColor, QIcon
from frontend.widgets import (
    CourseListElement,
    CourseInfoListElement,
    DoubleLineWidget,
    CourseInfoListHeader,
    TopesFilter
)
from backend.models import GroupedSection
import frontend.constants as c
import global_constants as gc
from backend.models import Course

class ScheduleWindow(QMainWindow):
    senal_buscar_sigla = pyqtSignal(str)
    senal_borrar_curso = pyqtSignal(int)
    senal_cambiar_seccion = pyqtSignal(int, int)
    senal_buscar_ofgs = pyqtSignal()
    senal_cambiar_campus = pyqtSignal(str)
    senal_cambiar_creditos = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        # TODO toggle dark mode
        self.setStyleSheet(c.DARK_MODE)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        menu_icon = QAction(QIcon(c.PATH_MENU_ICON), "Menu", self)
        menu_bar.addAction(menu_icon)
        
        self.dock_widget = QDockWidget("Menu", self)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.hide()
        menu_icon.triggered.connect(self.toggle_side_menu)
        
        dock_widget_content = QWidget(self.dock_widget)
        dock_widget_layout = QVBoxLayout(dock_widget_content)
        
        checkbox_group = TopesFilter(dock_widget_content)
        dock_widget_layout.addWidget(checkbox_group)
        
        file_list_title = QLabel("Guardados", dock_widget_content)
        dock_widget_layout.addWidget(file_list_title)
        file_list = QListWidget(dock_widget_content)
        directory = QDir(c.PATH_SAVED_COMBINATIONS)
        files = directory.entryList(QDir.Files)
        file_list.addItems(files)
        dock_widget_layout.addWidget(file_list)

        self.dock_widget.setWidget(dock_widget_content)

        layout_add = QHBoxLayout()
        self.txt_sigla = QComboBox(self)
        self.txt_sigla.setEditable(True)
        self.txt_sigla.setInsertPolicy(QComboBox.NoInsert)
        self.txt_sigla.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.btn_add = QPushButton("Agregar", self)
        layout_add.addWidget(self.txt_sigla)
        layout_add.addWidget(self.btn_add)
        layout.addLayout(layout_add)

        self.list_courses = QListWidget(self)
        self.list_courses.setSelectionMode(QAbstractItemView.NoSelection) # This is to avoid the blue selection
        self.lbl_combinations = QLabel("0", self)
        self.lbl_combinations.setStyleSheet("background-color: #2b2b2b;")
        layout.addWidget(self.list_courses)
        layout.addWidget(self.lbl_combinations)

        layout_btn = QHBoxLayout()
        self.btn_previous = QPushButton("Anterior", self)
        self.btn_previous.setEnabled(False)
        self.lbl_current_index = QLabel("0", self)
        self.lbl_current_index.setAlignment(Qt.AlignCenter)
        self.lbl_current_index.setStyleSheet("background-color: #2b2b2b;")
        self.btn_next = QPushButton("Siguiente", self)
        self.btn_next.setEnabled(False)
        layout_btn.addWidget(self.btn_previous)
        layout_btn.addWidget(self.lbl_current_index)
        layout_btn.addWidget(self.btn_next)
        layout.addLayout(layout_btn)
        layout_courses = QHBoxLayout()
        self.tb_schedule = QTableWidget(self)
        self.tb_schedule.setColumnCount(5)
        self.tb_schedule.setRowCount(9)
        self.tb_schedule.setRowHeight(4, 1)
        self.tb_schedule.setVerticalHeaderLabels(c.H_LABELS_HORARIO)
        self.tb_schedule.setHorizontalHeaderLabels(c.DIAS.keys())
        self.tb_schedule.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.set_lunch_line(4)
        self.list_current_courses = QListWidget(self)
        self.list_current_courses.setSelectionMode(QAbstractItemView.NoSelection) # This is to avoid the blue selection   
        layout_courses.addWidget(self.tb_schedule)
        layout_courses.addWidget(self.list_current_courses)
        layout.addLayout(layout_courses)
        btn_ofgs = QPushButton("Buscar OFGs", self)
        layout.addWidget(btn_ofgs)

        self.btn_add.clicked.connect(self.buscar_sigla)
        btn_ofgs.clicked.connect(self.enviar_buscar_ofgs)
    
    def toggle_side_menu(self):
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()
    
    def add_suggestions(self, courses: list[Course]):
        self.txt_sigla.clear()
        self.txt_sigla.addItems([course[gc.SIGLA] for course in courses])
        self.txt_sigla.clearEditText()

    def set_lunch_line(self, rowIndex):
        color = QColor("#5a5a5a")
        for j in range(self.tb_schedule.columnCount()):
            self.tb_schedule.setItem(rowIndex, j, QTableWidgetItem())
            self.tb_schedule.item(rowIndex, j).setBackground(color)

    def add_course_schedule(self, course):
        for sigla_type in [c.SIGLA_CATEDRA, c.SIGLA_AYUDANTIA, c.SIGLA_LAB, c.SIGLA_TALLER]:
            self.add_item(
                course[gc.SIGLA],
                course[gc.SECCIONES],
                course[gc.HORARIO][sigla_type].items(),
                c.COLORES[sigla_type],
            )

    def add_item(self, course_id, sections, items, color):
        sections = [str(section) for section in sections]
        for dia, modulos in items:
            for modulo in modulos:
                if modulo <= 4:
                    modulo -= 1
                cell_widget = self.tb_schedule.cellWidget(modulo, c.DIAS[dia])
                label = f"{course_id}-{','.join(sections)}"
                if cell_widget:
                    cell_widget.addLabel(label, color)
                else:
                    item = DoubleLineWidget(label, color)
                    self.tb_schedule.setCellWidget(modulo, c.DIAS[dia], item)

    def update_schedule(self, combinacion: list[GroupedSection]):
        self.list_current_courses.clear()
        self.tb_schedule.clearContents()
        self.set_lunch_line(4)
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(100, 35))
        header_item.setFlags(Qt.NoItemFlags)
        self.list_current_courses.addItem(header_item)
        self.list_current_courses.setItemWidget(
            header_item,
            CourseInfoListHeader(),
        )
        for course in combinacion:
            self.add_course_schedule(course)
            item = QListWidgetItem()
            item.setFlags(Qt.NoItemFlags)
            widget = CourseInfoListElement(course)
            item.setSizeHint(widget.sizeHint())
            self.list_current_courses.addItem(item)
            self.list_current_courses.setItemWidget(
                item,
                widget,
            )

    def new_schedule(self, combination: list[GroupedSection], cantidad_combinaciones, combinacion_actual):
        self.update_combinations_label(cantidad_combinaciones)
        self.update_current_index_label(combinacion_actual)
        self.update_schedule(combination)
        self.btn_previous.setEnabled(False)
        self.btn_next.setEnabled(False)

    def update_current_index_label(self, combinacion_actual):
        self.lbl_current_index.setText(f"Combinacion {combinacion_actual}")
    
    def update_combinations_label(self, cantidad_combinaciones):
        self.lbl_combinations.setText(f"{cantidad_combinaciones} combinaciones")

    def buscar_sigla(self):
        self.senal_buscar_sigla.emit(self.txt_sigla.currentText())

    def add_course(self, course: Course):
        self.txt_sigla.clearEditText()
        item = QListWidgetItem()
        item.setFlags(Qt.NoItemFlags)
        widget = CourseListElement(
                course,
                course[gc.SECCIONES],
                self.senal_borrar_curso,
                self.senal_cambiar_seccion,
            )
        item.setSizeHint(widget.sizeHint())
        self.list_courses.addItem(item)
        self.list_courses.setItemWidget(
            item,
            widget,
        )

    def delete_course(self, course_id):
        for i in range(self.list_courses.count()):
            item = self.list_courses.item(i)
            widget = self.list_courses.itemWidget(item)
            if widget.id_curso == course_id:
                self.list_courses.takeItem(self.list_courses.row(item))
                del item
                break

    def enviar_buscar_ofgs(self):
        self.senal_buscar_ofgs.emit()
    
    def update_course_section(self, course_id, section):
        for i in range(self.list_courses.count()):
            item = self.list_courses.item(i)
            widget = self.list_courses.itemWidget(item)
            if widget.id_curso == course_id:
                widget.update_section(section)
                break


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = ScheduleWindow()
    main.show()

    sys.exit(app.exec())
