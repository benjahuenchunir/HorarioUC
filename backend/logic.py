import os
import sys
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
    senal_add_course = pyqtSignal(dict)
    senal_update_schedule = pyqtSignal(tuple)
    senal_new_schedule = pyqtSignal(tuple, int, int)
    
    senal_change_next_btn_state = pyqtSignal(bool)
    senal_change_prev_btn_state = pyqtSignal(bool)
    senal_update_index = pyqtSignal(int)

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

    
    @property
    def current_course_index(self):
        return self.__current_course_index

    @current_course_index.setter
    def current_course_index(self, value):
        self.__current_course_index = max(0, min(value, len(self.combinaciones) - 1))

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
        ic(curso)
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
        course_id = self.db.insertar_registro(TABLA_CURSOS, [course])[-1]
        course[c.ID] = course_id
        for section in sections:
            section[c.ID_CURSO] = course_id
        self.db.insertar_registro(TABLA_SECCIONES, sections)
        return course, sections

    def generate_course_combinations(self):
        """
        Generates all the possible combinations of courses that can be taken together.
        """
        filtered_courses: list[list[GroupedSection]] = []
        for course in self.cursos.values():
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
        self.combinaciones = list(valid_combinations)
        ic(self.combinaciones)

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
        self.generate_course_combinations()
        self.current_course_index = 0
        self.senal_new_schedule.emit(self.combinaciones[self.current_course_index], len(self.combinaciones), self.current_course_index)
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
