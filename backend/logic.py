from database.database import Database
from database.constants import TABLA_CURSOS, TABLA_SECCIONES
import global_constants as c
from scraper.scraper import Scraper
from mappers import mapCourseToModel, mapCourseToDTO, mapSectionsToDTO
from icecream import ic
from backend.scraper.models import Course
from backend.database.tables import SectionDTO

class Logic:
    def __init__(self) -> None:
        self.db = Database()
        self.scraper = Scraper()
    
    def retrieve_course(self, course_id):
        """
        Tries to retrieve a course from the database and if it doesn't exist, it scrapes it from the website.
        """
        resultado = self.db.recuperar_curso(course_id)
        if resultado is None:
            print("No existe el curso en la base de datos, se procederá a buscarlo en la página web")
            curso = self.scrape_course(course_id)
            if curso is None:
                # TODO display error
                return
            return ic(curso)
        else:
            print("El curso existe en la base de datos")
            secciones = self.db.recuperar_secciones(resultado[c.ID])
            curso = mapCourseToModel(resultado, secciones)
            return ic(curso)
    
    def scrape_course(self, sigla) -> Course | None:
        course = self.scraper.find_course_info(sigla)
        if course is None:
            # TODO display error
            return
        mapped_course = mapCourseToDTO(course)
        # TODO transaction
        # Updates the database with the new course and its sections.
        course_id = self.db.insertar_registro(TABLA_CURSOS, [mapped_course])[-1]
        course[c.ID] = course_id
        mapped_sections = mapSectionsToDTO(course[c.SECCIONES], course_id)
        self.db.insertar_registro(TABLA_SECCIONES, mapped_sections)
        return course        

if __name__ == "__main__":
    l = Logic()
    curso = l.retrieve_course("IIC1005")
    print(curso[c.SECCIONES][0][c.HORARIO])
    print(type(curso[c.SECCIONES][0][c.HORARIO]))
