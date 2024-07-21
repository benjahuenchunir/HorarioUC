import os
import sys
from typing import Iterable
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from backend.database.database import Database
from backend.database.tables import SectionDTO, CourseDTO
from backend.database.constants import TABLA_CURSOS, TABLA_SECCIONES
import global_constants as c
from backend.scraper.scraper import Scraper
from mappers import mapCourseToModel
from icecream import ic
from backend.models import Course, GroupedSection, Filter, OFG, TopesFilter
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal
from itertools import product
import json
from dataclasses import replace

class Logic(QWidget):
    senal_enviar_cursos = pyqtSignal(list)
    senal_add_course = pyqtSignal(dict)
    senal_update_schedule = pyqtSignal(tuple)
    senal_new_schedule = pyqtSignal(tuple, int, int)
    senal_change_next_btn_state = pyqtSignal(bool)
    senal_change_prev_btn_state = pyqtSignal(bool)
    senal_update_index = pyqtSignal(int)
    senal_cambiar_seccion = pyqtSignal(int, int)
    senal_actualizar_combinaciones_guardadas = pyqtSignal()
    senal_limpiar_lista_cursos = pyqtSignal()
    senal_mostrar_alerta = pyqtSignal(str)
    
    senal_new_schedule_ofg = pyqtSignal(tuple, int, int)
    senal_update_schedule_ofg = pyqtSignal(tuple)
    senal_update_ofg_info = pyqtSignal(dict)
    senal_change_next_btn_state_ofg = pyqtSignal(bool)
    senal_change_prev_btn_state_ofg = pyqtSignal(bool)
    senal_update_index_ofg = pyqtSignal(int)
    senal_send_semester = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.scraper = Scraper()
        self.cursos: dict[int, Course] = {}
        self.year = c.YEARS[-1]
        self.period = c.PERIODS[0]
        
        self.secciones: dict[int, int] = {} # dict for storing the selected sections of each course
        self.combinaciones: list = []
        self.__current_course_index = 0
        self.topes_filter = TopesFilter()
        self.tope_lab = False
        self.tope_ayudantia = False
        
        self.current_combination: list[Course] = []
        self.ofg_combinations: list = []
        self.filter: Filter = Filter()
        self.current_ofg_combination_index = 0
    
    def load_year_and_period(self):
        try:
            with open(c.PATH_YEAR_AND_PERIOD, 'r') as f:
                data = json.load(f)
            self.year = data['year']
            self.period = data['period']
        except FileNotFoundError:
            self.db.clear()
            self.store_year_and_period()
        self.senal_send_semester.emit(self.year, self.period)
    
    def update_year_filter(self, year):
        self.year = year
        self.store_year_and_period()
        self.clear_everything()
        for course in list(self.cursos.values()):
            self.delete_course(course[c.ID], False)
            self.retrieve_course(course[c.SIGLA], False)
        self.new_schedule()
    
    def clear_everything(self):
        self.senal_limpiar_lista_cursos.emit()
        self.db.clear()
    
    def update_period_filter(self, period):
        self.period = period
        self.store_year_and_period()
        self.clear_everything()
        for course in list(self.cursos.values()):
            self.delete_course(course[c.ID], False)
            self.retrieve_course(course[c.SIGLA], False)
        self.new_schedule()
    
    def store_year_and_period(self):
        with open(c.PATH_YEAR_AND_PERIOD, 'w') as f:
            json.dump({'year': self.year, 'period': self.period}, f)
        
    @property
    def current_course_index(self):
        return self.__current_course_index

    @current_course_index.setter
    def current_course_index(self, value):
        self.__current_course_index = max(0, min(value, len(self.combinaciones) - 1))
    
    def retrieve_all_courses(self):
        """
        Retrieves all the courses from the database.
        """
        cursos = self.db.recuperar_cursos()
        cursos_model = []
        for curso in cursos:
            secciones = self.db.recuperar_secciones(curso[c.ID])
            cursos_model.append(mapCourseToModel(curso, secciones))
        self.senal_enviar_cursos.emit(cursos_model)

    def retrieve_course(self, sigla_curso: str, recalcular_combinaciones=True):
        if not sigla_curso:
            return
        sigla_curso = sigla_curso.upper()
        if any(sigla_curso == course[c.SIGLA].upper() for course in self.cursos.values()):
            return
        print(f"Buscando curso en la base de datos: {sigla_curso} ...")
        resultado = self.db.recuperar_curso(sigla_curso)
        if resultado is None:
            result = self.scrape_course(sigla_curso)
            if result is None:
                print("No se encontró el curso en la página web")
                self.senal_mostrar_alerta.emit(f"No se encontró el curso {sigla_curso.upper()} en la página web")
                return
            resultado, secciones = result
            if resultado is None:
                return
        else:
            print("El curso existe en la base de datos")
            secciones = self.retrieve_sections(resultado[c.ID])
        self.add_course_to_list(resultado, secciones, recalcular_combinaciones)

    def retrieve_sections(self, course_id):
        return self.db.recuperar_secciones(course_id)

    def scrape_course(self, sigla_curso):
        print(f"No existe el curso en la base de datos, se procederá a buscarlo en la página web")
        course = self.scraper.find_course_info(sigla_curso, self.year, self.period)
        if course is None:
            return
        self.db.insert_course(course)
        self.retrieve_all_courses()
        return course

    def add_course_to_list(self, resultado, secciones, recalcular_combinaciones):
        curso = mapCourseToModel(resultado, secciones)
        self.cursos[curso[c.ID]] = curso
        self.senal_add_course.emit(curso)
        if recalcular_combinaciones:
            self.new_schedule()        
    
    def retrieve_ofg_area(self, area):
        if area == "-":
            return
        self.save_current_combination()
        self.ofg_combinations.clear()
        ofgs = self.db.recuperar_ofgs(area)
        ofg_courses = self.get_filtered_courses(ofgs, area)
        self.add_combinations(ofg_courses)
        self.emit_ofg_schedule()

    def get_filtered_courses(self, ofgs, area):
        if not ofgs:
            ofgs = self.scrape_ofg_area(area)
            if not ofgs:
                return [] # TODO display error
        return [self.filter_ofg(curso, secciones) for curso, secciones in ofgs.values() if self.filter_ofg(curso, secciones)]

    def add_combinations(self, ofg_courses):
        for ofg in ofg_courses:
            combinaciones = self.generate_course_combinations(self.current_combination + [ofg])
            self.ofg_combinations.extend(combinaciones)
        self.current_ofg_combination_index = 0

    def emit_ofg_schedule(self):
        if self.ofg_combinations:
            self.senal_new_schedule_ofg.emit(self.ofg_combinations[self.current_ofg_combination_index], len(self.ofg_combinations), self.current_ofg_combination_index + 1)
            self.update_ofg_info()
        else:
            self.senal_new_schedule_ofg.emit((), 0, 0)
        if len(self.ofg_combinations) > 1:
            self.senal_change_next_btn_state_ofg.emit(True)
    
    def filter_ofg(self, ofg: CourseDTO, secciones: list[SectionDTO]) -> Course | None:
        if ofg[c.ID] in self.cursos: # Omitir cursos ya agregados
            return None
        if self.filter.creditos != c.CUALQUIERA and int(self.filter.creditos) != ofg[c.CREDITOS]:
            return None
        if self.filter.permite_retiro != c.CUALQUIERA and c.STRING_TO_BOOL[self.filter.permite_retiro] != ofg[c.PERMITE_RETIRO]:
            return None
        secciones = self.filter_sections(secciones)
        if not secciones:
            return None
        return mapCourseToModel(ofg, secciones)

    def filter_sections(self, secciones: list[SectionDTO]) -> list[SectionDTO]:
        return [seccion for seccion in secciones if
                (self.filter.campus == c.CUALQUIERA or self.filter.campus == seccion[c.CAMPUS]) and
                (self.filter.formato == c.CUALQUIERA or self.filter.formato == seccion[c.FORMATO]) and
                (self.filter.en_ingles == c.CUALQUIERA or c.STRING_TO_BOOL[self.filter.en_ingles] == seccion[c.EN_INGLES])]
    
    def save_current_combination(self):
        self.current_combination.clear()
        if not self.combinaciones:
            return
        for groupedSection in self.combinaciones[self.current_course_index]:
            curso = self.cursos[groupedSection[c.ID_CURSO]].copy()
            curso[c.SECCIONES] = [groupedSection]
            self.current_combination.append(curso)
    
    def scrape_ofg_area(self, area):
        url = f"https://buscacursos.uc.cl/?cxml_semestre={self.year}-{self.period}&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg={c.OFG[area]}&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
        courses = self.scraper.parse_url(url)
        if not courses:
            ... # TODO display error
        for course_tuple in courses.values():
            self.db.insert_course(course_tuple)
        self.retrieve_all_courses()
        return courses

    def generate_course_combinations(self, cursos: Iterable[Course]):
        """
        Generates all the possible combinations of courses that can be taken together.
        """
        filtered_courses: list[list[GroupedSection]] = []
        for course in cursos:
            grouped_sections = course[c.SECCIONES]
            filtered_section = self.secciones.get(course[c.ID], None)
            if filtered_section == c.TODAS or not filtered_section:
                filtered_courses.append(grouped_sections)
            else:
                filtered_courses.append([section for section in grouped_sections if filtered_section in section[c.SECCIONES]])
        
        # Generate all possible combinations of courses
        all_combinations = product(*filtered_courses)
        # Filter out the valid combinations
        valid_combinations = filter(self.are_courses_valid, all_combinations)
        return list(valid_combinations)
    
    def are_courses_valid(self, combination: list[GroupedSection]) -> bool:
        for attr in TopesFilter.__annotations__:
            class_type1, class_type2 = attr.split('_')
            if not getattr(self.topes_filter, attr) and not self.check_course_conflicts(combination, c.SHORT_FORM_TO_SIGLA[class_type1], c.SHORT_FORM_TO_SIGLA[class_type2]):
                return False
        return True

    def check_course_conflicts(self, combination: list[GroupedSection], class_type1: str, class_type2: str) -> bool:
        for i, course in enumerate(combination):
            for key, modules in course[c.HORARIO][class_type1].items():
                for j, other_course in enumerate(combination):
                    if (
                        i != j
                        and key in other_course[c.HORARIO][class_type2]
                        and any(val in other_course[c.HORARIO][class_type2][key] for val in modules)
                    ):
                        return False
        return True
    
    def new_schedule(self):
        self.combinaciones = self.generate_course_combinations(self.cursos.values())
        self.current_course_index = 0
        if self.combinaciones:
            self.senal_new_schedule.emit(self.combinaciones[self.current_course_index], len(self.combinaciones), self.current_course_index + 1)
        else:
            self.senal_new_schedule.emit((), 0, 0)
        if len(self.combinaciones) > 1:
            self.senal_change_next_btn_state.emit(True)
    
    def filter_course_section(self, course_id, seccion):
        self.secciones[course_id] = seccion
        if len(self.cursos[course_id][c.SECCIONES]) != 1:
            self.new_schedule()
    
    def delete_course(self, course_id, calcular_combinaciones=True):
        del self.cursos[course_id]
        if course_id in self.secciones:
            del self.secciones[course_id]
        if calcular_combinaciones:
            self.new_schedule()

    def increase_index(self):
        self.current_course_index += 1
        self.senal_update_index.emit(self.current_course_index + 1)
        if self.current_course_index == len(self.combinaciones) - 1:
            self.senal_change_next_btn_state.emit(False)
        self.senal_update_schedule.emit(self.combinaciones[self.current_course_index])
        self.senal_change_prev_btn_state.emit(True)
    
    def decrease_index(self):
        self.current_course_index -= 1
        self.senal_update_index.emit(self.current_course_index + 1)
        if self.current_course_index == 0:
            self.senal_change_prev_btn_state.emit(False)
        self.senal_update_schedule.emit(self.combinaciones[self.current_course_index])
        self.senal_change_next_btn_state.emit(True)
    
    def increase_ofg_index(self):
        self.current_ofg_combination_index += 1
        self.senal_update_index_ofg.emit(self.current_ofg_combination_index + 1)
        if self.current_ofg_combination_index == len(self.ofg_combinations) - 1:
            self.senal_change_next_btn_state_ofg.emit(False)
        self.senal_update_schedule_ofg.emit(self.ofg_combinations[self.current_ofg_combination_index])
        self.update_ofg_info()
        self.senal_change_prev_btn_state_ofg.emit(True)
    
    def decrease_ofg_index(self):
        self.current_ofg_combination_index -= 1
        self.senal_update_index_ofg.emit(self.current_ofg_combination_index + 1)
        if self.current_ofg_combination_index == 0:
            self.senal_change_prev_btn_state_ofg.emit(False)
        self.senal_update_schedule_ofg.emit(self.ofg_combinations[self.current_ofg_combination_index])
        self.update_ofg_info()
        self.senal_change_next_btn_state_ofg.emit(True)        
        
    def update_ofg_info(self):
        ofg = self.find_ofg()
        ofg_course_info = self.db.recuperar_curso(ofg[c.SIGLA])
        if ofg_course_info is None:
            print("No se encontró el curso en la base de datos") # TODO display error
            return
        ofg_info = OFG(
            sigla=ofg_course_info[c.SIGLA],
            nombre=ofg_course_info[c.NOMBRE],
            creditos=ofg_course_info[c.CREDITOS],
            permite_retiro=ofg_course_info[c.PERMITE_RETIRO],
            aprob_especial=ofg_course_info[c.APROB_ESPECIAL],
            descripcion=ofg_course_info[c.DESCRIPCION],
        )
        self.senal_update_ofg_info.emit(ofg_info)
    
    def find_ofg(self) -> GroupedSection:
        current_combination = self.ofg_combinations[self.current_ofg_combination_index]
        return next(course for course in current_combination if course[c.ID_CURSO] not in [course[c.ID] for course in self.current_combination])
    
    def choose_ofg(self):
        # TODO this currently resets the combinations
        ofg = self.find_ofg()
        self.retrieve_course(ofg[c.SIGLA])
        self.senal_cambiar_seccion.emit(ofg[c.ID_CURSO], ofg[c.SECCIONES][0])
    
    def update_ofg_filter(self, filter: Filter, area: str):
        self.filter = filter
        self.retrieve_ofg_area(area)
    
    def save_combination(self, nombre_combinacion):
        if not self.combinaciones: # Evita que se guarde una combinacion vacia
            # TODO display error
            return
        courses = []
        for course in self.combinaciones[self.current_course_index]:
            courses.append(course[c.SIGLA])
        data = {
            c.COMBINACION_ACTUAL: self.current_course_index,
            c.CURSOS: courses
        }
        with open(f'{c.PATH_SAVED_COMBINATIONS}{nombre_combinacion}.json', 'w') as f:
            json.dump(data, f)
        self.senal_actualizar_combinaciones_guardadas.emit()
    
    def load_combination(self, nombre_combinacion):
        self.cursos.clear()
        self.senal_limpiar_lista_cursos.emit()
        with open(f'{c.PATH_SAVED_COMBINATIONS}{nombre_combinacion}', 'r') as f:
            data = json.load(f)
        for course in data[c.CURSOS][0:-1]:
            self.retrieve_course(course, False)
        self.retrieve_course(data[c.CURSOS][-1], True)
        self.current_course_index = data[c.COMBINACION_ACTUAL]
        self.senal_update_schedule.emit(self.combinaciones[self.current_course_index])
        self.senal_update_index.emit(self.current_course_index + 1)
        self.senal_change_next_btn_state.emit(not self.current_course_index == len(self.combinaciones) - 1)
        self.senal_change_prev_btn_state.emit(not self.current_course_index == 0)
    
    def delete_combination(self, nombre_combinacion):
        os.remove(f'{c.PATH_SAVED_COMBINATIONS}{nombre_combinacion}')
        self.senal_actualizar_combinaciones_guardadas.emit()
        
    def update_topes_filter(self, attr: str, value: bool):
        self.topes_filter = replace(self.topes_filter, **{attr: value})
        self.new_schedule()

    def download_course_info(self, sigla: str):
        self.scraper.download_course_program_and_requirements(sigla)

if __name__ == "__main__":

    def hook(type_, value, traceback):
        print(type_)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication(sys.argv)
    main = Logic()
    main.retrieve_course("IIC1005")
    main.retrieve_course("MAT1630")

    sys.exit(app.exec())
