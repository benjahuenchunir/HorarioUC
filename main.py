from backend import Logic
from frontend import ScheduleWindow
import parametros as p
import sys
from PyQt5.QtWidgets import QApplication


class HorarioMaker:
    def __init__(self):
        self.front = ScheduleWindow()
        self.back = Logic()
        self.conectar_senales()

    def conectar_senales(self):
        self.front.senal_buscar_sigla.connect(self.back.find_course_info)
        self.back.senal_add_course.connect(self.front.add_course)
        self.back.senal_update_schedule.connect(self.front.new_schedule)
        self.front.senal_borrar_curso.connect(self.back.delete_course)
        self.front.senal_cambiar_seccion.connect(self.back.filter_course_section)
        self.back.senal_borrar_curso.connect(self.front.delete_course)

    def iniciar(self):
        self.front.show()


if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = HorarioMaker()
    main.iniciar()

    sys.exit(app.exec())
