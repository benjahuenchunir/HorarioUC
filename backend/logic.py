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
from backend.models import Course, GroupedSection
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal
from itertools import product

class Logic(QWidget):
    senal_enviar_cursos = pyqtSignal(list)
    senal_add_course = pyqtSignal(dict)
    senal_update_schedule = pyqtSignal(tuple)
    senal_new_schedule = pyqtSignal(tuple, int, int)
    senal_change_next_btn_state = pyqtSignal(bool)
    senal_change_prev_btn_state = pyqtSignal(bool)
    senal_update_index = pyqtSignal(int)
    
    senal_new_schedule_ofg = pyqtSignal(tuple, int, int)
    senal_update_schedule_ofg = pyqtSignal(tuple)
    senal_change_next_btn_state_ofg = pyqtSignal(bool)
    senal_change_prev_btn_state_ofg = pyqtSignal(bool)
    senal_update_index_ofg = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.scraper = Scraper()
        self.cursos: dict[int, Course] = {}
        
        self.secciones: dict[int, int] = {} # dict for storing the selected sections of each course
        self.combinaciones: list = []
        self.__current_course_index = 0
        self.tope_lab = False
        self.tope_ayudantia = False
        
        self.current_combination: list[Course] = []
        self.ofg_combinations = []
        self.current_ofg_combination_index = 0
    
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

    def retrieve_course(self, sigla_curso: str):
        """
        Tries to retrieve a course from the database and if it doesn't exist, it scrapes it from the website.
        """
        if sigla_curso == "":
            return
        sigla_curso = sigla_curso.upper()
        if any(sigla_curso == course[c.SIGLA].upper() for course in self.cursos.values()):
            return
        print("Buscando curso en la base de datos: ", sigla_curso, "...")
        resultado = self.db.recuperar_curso(sigla_curso)
        if resultado is None:
            print(
                "No existe el curso en la base de datos, se procederá a buscarlo en la página web"
            )
            tupla_curso = self.scrape_course(sigla_curso)
            if tupla_curso is None:
                # TODO display error
                return
            resultado, secciones = tupla_curso
        else:
            print("El curso existe en la base de datos")
            secciones = self.db.recuperar_secciones(resultado[c.ID])
        curso = mapCourseToModel(resultado, secciones)
        self.cursos[curso[c.ID]] = curso
        self.senal_add_course.emit(curso)
        self.new_schedule()

    def scrape_course(self, sigla) -> tuple[CourseDTO, list[SectionDTO]] | None:
        course = self.scraper.find_course_info(sigla)
        if course is None:
            # TODO display error
            return
        course, sections = course
        # TODO transaction
        # Updates the database with the new course and its sections.
        self.insert_course(course, sections)
        self.retrieve_all_courses()
        return course, sections
    
    def retrieve_ofg_area(self, area):
        if area == "-":
            return
        self.save_current_combination()
        self.ofg_combinations.clear()
        ofgs = self.db.recuperar_ofgs(area)
        ofg_courses: list[Course] = []
        if not ofgs:
            ofgs = self.scrape_ofg_area(area)
            if not ofgs:
                return # TODO display error
            for curso, secciones in ofgs.values():
                ofg_courses.append(mapCourseToModel(curso, secciones))
        else:
            for ofg in ofgs:
                secciones = self.db.recuperar_secciones(ofg[c.ID])
                if not secciones:
                    return # TODO display error
                ofg_courses.append(mapCourseToModel(ofg, secciones))
        for ofg in ofg_courses:
            combinaciones = self.generate_course_combinations(self.current_combination + [ofg])
            self.ofg_combinations.extend(combinaciones)
        self.current_ofg_combination_index = 0
        self.senal_new_schedule_ofg.emit(self.ofg_combinations[self.current_ofg_combination_index], len(self.ofg_combinations), self.current_ofg_combination_index + 1)
        if len(self.ofg_combinations) > 1:
            self.senal_change_next_btn_state_ofg.emit(True)
    
    def save_current_combination(self):
        self.current_combination.clear()
        if not self.combinaciones:
            return
        for groupedSection in self.combinaciones[self.current_course_index]:
            curso = self.cursos[groupedSection[c.ID_CURSO]].copy()
            curso[c.SECCIONES] = [groupedSection]
            self.current_combination.append(curso)
    
    def scrape_ofg_area(self, area):
        url = f"https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg={c.OFG[area]}&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
        courses = self.scraper.parse_url(url)
        if not courses:
            ... # TODO display error
        for course, sections in courses.values():
            self.insert_course(course, sections)
        self.retrieve_all_courses()
        return courses
    
    def insert_course(self, course: CourseDTO, sections: list):
        course_id = self.db.insertar_registro(TABLA_CURSOS, [course])[-1]
        course[c.ID] = course_id
        for section in sections:
            section[c.ID_CURSO] = course_id
        self.db.insertar_registro(TABLA_SECCIONES, sections)

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
        schedule_per_day = {}
        for course in combination:  # Catedra con catedra
            for key, value in course[c.HORARIO][c.SIGLA_CATEDRA].items():
                if key not in schedule_per_day:
                    schedule_per_day[key] = value.copy()
                else:
                    if any(val in schedule_per_day[key] for val in value):
                        return False
                    else:
                        schedule_per_day[key].extend(value.copy())
        for i, course in enumerate(combination):  # Catedra con taller
            for key, modules in course[c.HORARIO][c.SIGLA_CATEDRA].items():
                for j, other_course in enumerate(combination):
                    if (
                        i != j
                        and key in other_course[c.HORARIO][c.SIGLA_TALLER]
                        and any(val in other_course[c.HORARIO][c.SIGLA_TALLER][key] for val in modules)
                    ):
                        return False
        if not self.tope_lab:
            for i, course in enumerate(combination):  # Catedra con lab
                for key, modules in course[c.HORARIO][c.SIGLA_CATEDRA].items():
                    for j, other_course in enumerate(combination):
                        if (
                            i != j
                            and key in other_course[c.HORARIO][c.SIGLA_LAB]
                            and any(val in other_course[c.HORARIO][c.SIGLA_LAB][key] for val in modules)
                        ):
                            return False
        if not self.tope_ayudantia:
            for i, course in enumerate(combination):  # Catedra con ayudantia
                for key, modules in course[c.HORARIO][c.SIGLA_CATEDRA].items():
                    for j, other_course in enumerate(combination):
                        if (
                            i != j
                            and key in other_course[c.HORARIO][c.SIGLA_AYUDANTIA]
                            and any(
                                val in other_course[c.HORARIO][c.SIGLA_AYUDANTIA][key] for val in modules
                            )
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
    
    def delete_course(self, course_id):
        del self.cursos[course_id]
        if course_id in self.secciones:
            del self.secciones[course_id]
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
        self.senal_change_prev_btn_state_ofg.emit(True)
    
    def decrease_ofg_index(self):
        self.current_ofg_combination_index -= 1
        self.senal_update_index_ofg.emit(self.current_ofg_combination_index + 1)
        if self.current_ofg_combination_index == 0:
            self.senal_change_prev_btn_state_ofg.emit(False)
        self.senal_update_schedule_ofg.emit(self.ofg_combinations[self.current_ofg_combination_index])
        self.senal_change_next_btn_state_ofg.emit(True)


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
