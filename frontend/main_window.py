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
    QAction,
    QDockWidget,
    QToolBar,
    QInputDialog,
    QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QDir
from PyQt5.QtGui import QColor, QIcon
from frontend.widgets import (
    CourseListElement,
    CourseInfoListElement,
    DoubleLineWidget,
    CourseInfoListHeader,
    TopesFilterWidget,
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
    senal_guardar_combinacion = pyqtSignal(str)
    senal_cargar_combinacion = pyqtSignal(str)
    senal_eliminar_combinacion = pyqtSignal(str)
    senal_cambiar_topes = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        # TODO toggle dark mode
        self.setStyleSheet(c.DARK_MODE)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        menu_bar = QToolBar(self, movable=False)
        menu_bar.setIconSize(QSize(32, 32))
        self.addToolBar(menu_bar)
        menu_icon = QAction(QIcon(c.PATH_MENU_ICON), "Menu", self)
        menu_bar.addAction(menu_icon)

        self.dock_widget = QDockWidget("", self)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.hide()
        menu_icon.triggered.connect(self.toggle_side_menu)

        dock_widget_content = QWidget(self.dock_widget)
        dock_widget_layout = QVBoxLayout(dock_widget_content)

        checkbox_group = TopesFilterWidget(self.senal_cambiar_topes, dock_widget_content)
        dock_widget_layout.addWidget(checkbox_group)

        file_list_title_layout = QHBoxLayout()
        file_list_title = QLabel("Guardados", dock_widget_content)
        file_list_title.setStyleSheet("background-color: #2b2b2b; font-weight: bold;")
        file_list_title_layout.addWidget(file_list_title)
        add_button = QPushButton("+", dock_widget_content)
        add_button.setFixedSize(30, 30)
        add_button.clicked.connect(self.prompt_save_name)
        file_list_title_layout.addWidget(add_button)
        dock_widget_layout.addLayout(file_list_title_layout)
        self.file_list = QListWidget(dock_widget_content)
        dock_widget_layout.addWidget(self.file_list)

        self.dock_widget.setWidget(dock_widget_content)

        layout_semester = QHBoxLayout()
        layout.addLayout(layout_semester)
        self.dropdown_year = QComboBox(self)
        self.dropdown_year.addItems(gc.YEARS)
        layout_semester.addWidget(self.dropdown_year)
        self.dropdown_period = QComboBox(self)
        self.dropdown_period.addItems(gc.PERIODS)
        layout_semester.addWidget(self.dropdown_period)
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
        self.list_courses.setSelectionMode(
            QAbstractItemView.NoSelection
        )  # This is to avoid the blue selection
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
        self.tb_schedule.setColumnCount(6)
        self.tb_schedule.setRowCount(10)
        self.tb_schedule.setRowHeight(4, 1)
        self.tb_schedule.setVerticalHeaderLabels(c.H_LABELS_HORARIO)
        self.tb_schedule.setHorizontalHeaderLabels(c.DIAS.keys())
        self.tb_schedule.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.set_lunch_line(4)
        self.list_current_courses = QListWidget(self)
        self.list_current_courses.setSelectionMode(
            QAbstractItemView.NoSelection
        )  # This is to avoid the blue selection
        layout_courses.addWidget(self.tb_schedule)
        layout_courses.addWidget(self.list_current_courses)
        layout.addLayout(layout_courses)
        btn_ofgs = QPushButton("Buscar OFGs", self)
        layout.addWidget(btn_ofgs)

        self.btn_add.clicked.connect(self.buscar_sigla)
        btn_ofgs.clicked.connect(self.enviar_buscar_ofgs)

        self.update_saved_combinations()
    
    def update_semester_filter(self, year, period):
        self.dropdown_year.blockSignals(True)
        self.dropdown_year.setCurrentText(year)
        self.dropdown_year.blockSignals(False)

        self.dropdown_period.blockSignals(True)
        self.dropdown_period.setCurrentText(period)
        self.dropdown_period.blockSignals(False)

    def toggle_side_menu(self):
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()

    def prompt_save_name(self):
        name, ok = QInputDialog.getText(
            self, "Guardar combinacion", "Ingresa un nombre:"
        )
        if ok:
            self.senal_guardar_combinacion.emit(name)

    def update_saved_combinations(self):
        directory = QDir(gc.PATH_SAVED_COMBINATIONS)
        files = directory.entryList(QDir.Files)
        self.file_list.clear()
        for file in files:
            if not file.endswith(".json"):
                continue
            item = QListWidgetItem(self.file_list)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            delete_button = QPushButton(QIcon(c.PATH_DELETE_ICON), "")
            delete_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            delete_button.setMaximumWidth(30)
            delete_button.clicked.connect(
                lambda checked, file=file: self.senal_eliminar_combinacion.emit(file)
            )
            layout.addWidget(delete_button, 0)
            label = QLabel(file.split(".")[0])
            label.setStyleSheet("background-color: #2b2b2b;")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            load_button = QPushButton(QIcon(c.PATH_LOAD_ICON), "")
            load_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            load_button.setMaximumWidth(60)
            load_button.clicked.connect(
                lambda checked, file=file: self.senal_cargar_combinacion.emit(file)
            )
            layout.addWidget(label, 1)
            layout.addWidget(load_button, 0)
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, widget)

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
        for sigla_type in gc.TIPOS_CLASES:
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

    def new_schedule(
        self,
        combination: list[GroupedSection],
        cantidad_combinaciones,
        combinacion_actual,
    ):
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
    
    def show_alert(self, message):
        alert = QMessageBox(self)
        alert.setText(message)
        alert.exec()


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = ScheduleWindow()
    main.show()

    sys.exit(app.exec())
