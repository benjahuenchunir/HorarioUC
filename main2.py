from backend.logic import Logic
from frontend.main_window import ScheduleWindow
import sys
from PyQt5.QtWidgets import QApplication

class HorarioUC:
    def __init__(self) -> None:
        super().__init__()
        self.backend = Logic()
        self.frontend = ScheduleWindow()
        self.conectar_senales()
    
    def conectar_senales(self):
        self.frontend.senal_buscar_sigla.connect(self.backend.retrieve_course)
        self.backend.senal_add_course.connect(self.frontend.add_course)
        self.frontend.senal_cambiar_seccion.connect(self.backend.filter_course_section)
        self.frontend.senal_borrar_curso.connect(self.backend.delete_course)
        self.frontend.senal_borrar_curso.connect(self.frontend.delete_course)
        

if __name__ == "__main__":
    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    
    horario = HorarioUC()
    horario.frontend.show()

    sys.exit(app.exec())