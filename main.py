from backend.logic import Logic
from frontend.main_window import ScheduleWindow
from frontend.ofg_window import OFGWindow
import sys
from PyQt5.QtWidgets import QApplication

class HorarioUC:
    def __init__(self) -> None:
        super().__init__()
        self.backend = Logic()
        self.schedule_window = ScheduleWindow()
        self.ofg_window = OFGWindow()
        self.conectar_senales_schedule()
        self.conectar_senales_ofg()
        self.backend.load_year_and_period()
        self.backend.retrieve_all_courses()
        self.schedule_window.showMaximized()
    
    def conectar_senales_schedule(self):
        self.backend.senal_enviar_cursos.connect(self.schedule_window.add_suggestions)
        self.schedule_window.senal_buscar_sigla.connect(self.backend.retrieve_course)
        self.backend.senal_add_course.connect(self.schedule_window.add_course)
        self.schedule_window.senal_cambiar_seccion.connect(self.backend.filter_course_section)
        self.schedule_window.senal_borrar_curso.connect(self.backend.delete_course)
        self.schedule_window.senal_borrar_curso.connect(self.schedule_window.delete_course)
        self.backend.senal_new_schedule.connect(self.schedule_window.new_schedule)
        self.backend.senal_update_schedule.connect(self.schedule_window.update_schedule)
        self.schedule_window.btn_next.clicked.connect(self.backend.increase_index)
        self.backend.senal_change_next_btn_state.connect(lambda x: self.schedule_window.btn_next.setEnabled(x))
        self.schedule_window.btn_previous.clicked.connect(self.backend.decrease_index)
        self.backend.senal_change_prev_btn_state.connect(lambda x: self.schedule_window.btn_previous.setEnabled(x))
        self.backend.senal_update_index.connect(self.schedule_window.update_current_index_label)
        self.schedule_window.senal_buscar_ofgs.connect(self.change_to_ofgs)
        self.backend.senal_cambiar_seccion.connect(self.schedule_window.update_course_section)
        self.schedule_window.senal_guardar_combinacion.connect(self.backend.save_combination)
        self.backend.senal_actualizar_combinaciones_guardadas.connect(self.schedule_window.update_saved_combinations)
        self.schedule_window.senal_cargar_combinacion.connect(self.backend.load_combination)
        self.backend.senal_limpiar_lista_cursos.connect(self.schedule_window.list_courses.clear)
        self.schedule_window.senal_eliminar_combinacion.connect(self.backend.delete_combination)
        self.schedule_window.senal_cambiar_topes.connect(self.backend.update_topes_filter)
        self.schedule_window.dropdown_year.currentTextChanged.connect(self.backend.update_year_filter)
        self.schedule_window.dropdown_period.currentTextChanged.connect(self.backend.update_period_filter)
        self.backend.senal_send_semester.connect(self.schedule_window.update_semester_filter)
        self.backend.senal_mostrar_alerta.connect(self.schedule_window.show_alert)
        self.schedule_window.senal_download_info.connect(self.backend.download_course_info)
        
    def conectar_senales_ofg(self):
        self.ofg_window.senal_cambiar_area.connect(self.backend.retrieve_ofg_area)
        self.ofg_window.back_action.triggered.connect(self.change_to_schedule)
        self.ofg_window.btn_next.clicked.connect(self.backend.increase_ofg_index)
        self.backend.senal_change_next_btn_state_ofg.connect(lambda x: self.ofg_window.btn_next.setEnabled(x))
        self.ofg_window.btn_previous.clicked.connect(self.backend.decrease_ofg_index)
        self.backend.senal_change_prev_btn_state_ofg.connect(lambda x: self.ofg_window.btn_previous.setEnabled(x))
        self.backend.senal_update_index_ofg.connect(self.ofg_window.update_current_index_label)
        self.backend.senal_new_schedule_ofg.connect(self.ofg_window.new_schedule)
        self.backend.senal_update_schedule_ofg.connect(self.ofg_window.update_schedule)
        self.ofg_window.btn_choose_ofg.clicked.connect(self.backend.choose_ofg)
        self.ofg_window.btn_choose_ofg.clicked.connect(self.change_to_schedule)
        self.ofg_window.senal_cambiar_filtro.connect(self.ofg_window.change_filters)
        self.ofg_window.senal_filtrar.connect(self.backend.update_ofg_filter)
        self.backend.senal_update_ofg_info.connect(self.ofg_window.ofg_info_widget.set_course_info)
        self.ofg_window.senal_download_course_info.connect(self.backend.download_course_info)

    def change_to_ofgs(self):
        self.schedule_window.hide()
        self.ofg_window.iniciar()
        if self.backend.combinaciones:
            self.ofg_window.new_schedule(self.backend.combinaciones[self.backend.current_course_index], 0, 0)
    
    def change_to_schedule(self):
        self.ofg_window.hide()
        self.schedule_window.showMaximized()
        

if __name__ == "__main__":
    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    
    horario = HorarioUC()
    
    sys.exit(app.exec())