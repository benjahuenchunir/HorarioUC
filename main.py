from backend import Logic
from frontend import ScheduleWindow, OFGWindow
import parametros as p
import sys
from PyQt5.QtWidgets import QApplication


class HorarioMaker:
    def __init__(self):
        self.front = ScheduleWindow()
        self.ofgs = OFGWindow()
        self.back = Logic()
        self.conectar_senales()

    def conectar_senales(self):
        self.front.senal_buscar_sigla.connect(self.back.find_course_info)
        self.back.senal_add_course.connect(self.front.add_course)
        self.back.senal_update_schedule.connect(self.front.new_schedule)
        self.front.senal_borrar_curso.connect(self.back.delete_course)
        self.front.senal_cambiar_seccion.connect(self.back.filter_course_section)
        self.back.senal_borrar_curso.connect(self.front.delete_course)

        self.front.senal_buscar_ofgs.connect(self.change_to_ofgs)
        self.ofgs.senal_cambiar_area.connect(self.back.change_ofg_area)
        self.back.senal_update_ofgs.connect(self.ofgs.update_ofgs)
        self.ofgs.senal_volver.connect(self.change_to_main)

    def iniciar(self):
        self.front.show()

    def change_to_ofgs(self, selected_combination):
        self.front.hide()
        self.back.current_combination.clear()
        for course in selected_combination:
            self.back.current_combination.append([course])
        self.ofgs.iniciar()

    def change_to_main(self):
        self.ofgs.close()
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
