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
        self.backend.senal_new_schedule.connect(self.frontend.new_schedule)
        self.backend.senal_update_schedule.connect(self.frontend.update_schedule)
        self.frontend.btn_next.clicked.connect(self.backend.increase_index)
        self.backend.senal_change_next_btn_state.connect(lambda x: self.frontend.btn_next.setEnabled(x))
        self.frontend.btn_previous.clicked.connect(self.backend.decrease_index)
        self.backend.senal_change_prev_btn_state.connect(lambda x: self.frontend.btn_previous.setEnabled(x))
        self.backend.senal_update_index.connect(self.frontend.update_current_index_label)
        

if __name__ == "__main__":
    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    
    horario = HorarioUC()
    horario.frontend.show()
    horario.backend.retrieve_course("IIC1005")
    horario.backend.retrieve_course("MAT1630")
    
    sys.exit(app.exec())