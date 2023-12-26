import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QApplication,
    QAbstractItemView,
    QToolBar,
    QAction,
    QDockWidget,
    QMainWindow,
    QFormLayout,
)
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QColor, QIcon
import frontend.constants as p
import global_constants as gc
from frontend.widgets import (
    DoubleLineWidget,
    CourseInfoListElement,
    CourseInfoListHeader,
    FilterComboBox,
    OFGInfoWidget,
)
from backend.models import GroupedSection, Filter


class OFGWindow(QMainWindow):
    senal_cambiar_area = pyqtSignal(str)
    senal_cambiar_filtro = pyqtSignal()
    senal_filtrar = pyqtSignal(Filter, str)

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.setStyleSheet(p.DARK_MODE)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        self.back_action = QAction(QIcon(p.PATH_BACK_ICON), "Volver", self)
        self.toolbar.addAction(self.back_action)
        self.side_menu_action = QAction(QIcon(p.PATH_FILTER_ICON), "Filtrar", self)
        self.toolbar.addAction(self.side_menu_action)
        self.side_menu_action.triggered.connect(self.open_side_menu)

        self.dock_widget = QDockWidget("Filtros", self)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.hide()

        dock_widget_content = QWidget(self.dock_widget)
        dock_widget_layout = QFormLayout(dock_widget_content)

        self.campus_filter = FilterComboBox(
            gc.OPCIONES_CAMPUS, self.senal_cambiar_filtro, self
        )
        self.format_filter = FilterComboBox(
            gc.OPCIONES_FORMATO, self.senal_cambiar_filtro, self
        )
        self.credits_filter = FilterComboBox(
            gc.OPCIONES_CREDITOS, self.senal_cambiar_filtro, self
        )
        self.english_filter = FilterComboBox(
            gc.OPCIONES_EN_INGLES, self.senal_cambiar_filtro, self
        )
        self.withdrawal_filter = FilterComboBox(
            gc.OPCIONES_PERMITE_RETIRO, self.senal_cambiar_filtro, self
        )

        dock_widget_layout.addRow("Campus", self.campus_filter)
        dock_widget_layout.addRow("Formato", self.format_filter)
        dock_widget_layout.addRow("Creditos", self.credits_filter)
        dock_widget_layout.addRow("En ingles", self.english_filter)
        dock_widget_layout.addRow("Permite retiro", self.withdrawal_filter)

        self.dock_widget.setWidget(dock_widget_content)

        self.qcb_ofg_areas = QComboBox(self)
        self.qcb_ofg_areas.addItem("-")
        for area in gc.OFG:
            self.qcb_ofg_areas.addItem(area)
        self.lbl_combinations = QLabel("0", self)
        self.lbl_combinations.setStyleSheet("background-color: #2b2b2b;")
        layout.addWidget(self.qcb_ofg_areas)
        layout.addWidget(self.lbl_combinations)

        layout_btn = QHBoxLayout()
        self.btn_previous = QPushButton("Anterior", self)
        self.btn_previous.setEnabled(False)
        self.lbl_current_ofg = QLabel("0", self)
        self.lbl_current_ofg.setAlignment(Qt.AlignCenter)
        self.lbl_current_ofg.setStyleSheet("background-color: #2b2b2b;")
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
        self.tb_schedule.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.set_lunch_line()
        right_layout = QVBoxLayout()
        self.ofg_info_widget = OFGInfoWidget(self)
        right_layout.addWidget(self.ofg_info_widget)
        self.list_current_courses = QListWidget(self)
        self.list_current_courses.setSelectionMode(QAbstractItemView.NoSelection)
        right_layout.addWidget(self.list_current_courses)
        layout_courses.addWidget(self.tb_schedule)
        layout_courses.addLayout(right_layout)
        layout.addLayout(layout_courses)
        self.btn_choose_ofg = QPushButton("Elegir OFG", self)
        self.btn_choose_ofg.setEnabled(False)
        layout.addWidget(self.btn_choose_ofg)

        self.qcb_ofg_areas.currentTextChanged.connect(self.enviar_cambiar_area)

    def open_side_menu(self):
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()

    def change_filters(self):
        self.senal_filtrar.emit(
            Filter(
                campus=self.campus_filter.currentText(),
                formato=self.format_filter.currentText(),
                creditos=self.credits_filter.currentText(),
                en_ingles=self.english_filter.currentText(),
                permite_retiro=self.withdrawal_filter.currentText(),
            ),
            self.qcb_ofg_areas.currentText(),
        )

    def iniciar(self):
        self.lbl_combinations.clear()
        self.lbl_current_ofg.clear()
        self.list_current_courses.clear()
        self.ofg_info_widget.clear()
        self.tb_schedule.clearContents()
        self.qcb_ofg_areas.setCurrentIndex(0)
        self.btn_next.setEnabled(False)
        self.btn_previous.setEnabled(False)
        self.showMaximized()

    def set_lunch_line(self):
        color = QColor("#5a5a5a")
        for j in range(self.tb_schedule.columnCount()):
            self.tb_schedule.setItem(4, j, QTableWidgetItem())
            self.tb_schedule.item(4, j).setBackground(color)

    def add_course_schedule(self, course):
        for sigla_type in [
            gc.SIGLA_CATEDRA,
            gc.SIGLA_AYUDANTIA,
            gc.SIGLA_LAB,
            gc.SIGLA_TALLER,
        ]:
            self.add_item(
                course[gc.SIGLA],
                course[gc.SECCIONES],
                course[gc.HORARIO][sigla_type].items(),
                p.COLORES[sigla_type],
            )

    def add_item(self, course_id, sections, items, color):
        sections = [str(section) for section in sections]
        for dia, modulos in items:
            for modulo in modulos:
                if modulo <= 4:
                    modulo -= 1
                cell_widget = self.tb_schedule.cellWidget(modulo, p.DIAS[dia])
                label = f"{course_id}-{','.join(sections)}"
                if cell_widget:
                    cell_widget.addLabel(label, color)
                else:
                    item = DoubleLineWidget(label, color)
                    self.tb_schedule.setCellWidget(modulo, p.DIAS[dia], item)

    def update_schedule(self, combinacion: list[GroupedSection]):
        self.list_current_courses.clear()
        self.tb_schedule.clearContents()
        self.set_lunch_line()
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
        self.btn_choose_ofg.setEnabled(False)
        if len(combination) > 1:
            self.btn_choose_ofg.setEnabled(True)

    def update_current_index_label(self, combinacion_actual):
        self.lbl_current_ofg.setText(f"Combinacion {combinacion_actual}")

    def update_combinations_label(self, cantidad_combinaciones):
        self.lbl_combinations.setText(f"{cantidad_combinaciones} combinaciones")

    def enviar_cambiar_area(self, area):
        self.senal_cambiar_area.emit(area)


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = OFGWindow()
    main.show()

    sys.exit(app.exec())
