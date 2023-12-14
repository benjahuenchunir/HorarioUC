from database.database import Database
from database.constants import TABLA_CURSOS, TABLA_SECCIONES, DATABASE_NAME
import constants as c
from scraper.scraper import Scraper
from mappers import mapCourseToModel, mapCourseToDTO
from icecream import ic

class Logic:
    def __init__(self) -> None:
        self.db = Database()
        self.scraper = Scraper()
    
    def find_course_info(self, sigla):
        course = self.scraper.find_course_info(sigla)
        if course is None:
            # TODO display error
            return
        mapped_course, mapped_sections = mapCourseToDTO(course)
        course_id = self.db.insertar_registro(DATABASE_NAME, TABLA_CURSOS, [mapped_course])[-1]
        self.db.insertar_registro(DATABASE_NAME, TABLA_SECCIONES, self.add_course_id(mapped_sections, course_id))
    
    def add_course_id(self, sections: list, course_id: int):
        for section in sections:
            section[c.ID_CURSO] = course_id
        return sections

if __name__ == "__main__":
    l = Logic()
