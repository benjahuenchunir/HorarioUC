from backend.database.tables import CourseDTO, SectionDTO
from backend.scraper.models import Course, Section
import global_constants as c
import json

def mapCourseToModel(course: CourseDTO, secciones: list[SectionDTO]) -> Course:
    return Course(
        id=course[c.ID],
        sigla=course[c.SIGLA],
        nombre=course[c.NOMBRE],
        permite_retiro=course[c.PERMITE_RETIRO],
        aprob_especial=course[c.APROB_ESPECIAL],
        area=course[c.AREA],
        creditos=course[c.CREDITOS],
        descripcion=course[c.DESCRIPCION],
        secciones=[mapSectionToModel(section) for section in secciones]
    )

def mapSectionToModel(section: SectionDTO) -> Section:
    return Section(
        seccion=section[c.SECCION],
        nrc=section[c.NRC],
        profesor=section[c.PROFESOR],
        campus=section[c.CAMPUS],
        en_ingles=section[c.EN_INGLES],
        horario=json.loads(section[c.HORARIO]),
        formato=section[c.FORMATO],
    )

def mapCourseToDTO(course: Course) -> CourseDTO:
    return CourseDTO(
        id=course[c.ID],
        sigla=course[c.SIGLA],
        nombre=course[c.NOMBRE],
        permite_retiro=course[c.PERMITE_RETIRO],
        aprob_especial=course[c.APROB_ESPECIAL],
        area=course[c.AREA],
        creditos=course[c.CREDITOS],
        descripcion=course[c.DESCRIPCION]
    )

def mapSectionToDTO(section: Section, course_id: int) -> SectionDTO:
    horario = {k: list(v) for k, v in section[c.HORARIO].items()}
    horario_json = json.dumps(horario)
    return SectionDTO(
        id_curso=course_id,
        seccion=section[c.SECCION],
        nrc=section[c.NRC],
        profesor=section[c.PROFESOR],
        campus=section[c.CAMPUS],
        en_ingles=section[c.EN_INGLES],
        horario=horario_json,
        formato=section[c.FORMATO],
    )

def mapSectionsToDTO(sections: list[Section], course_id: int) -> list[SectionDTO]:
    return [mapSectionToDTO(section, course_id) for section in sections]