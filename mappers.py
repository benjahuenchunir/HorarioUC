from database.tables import CourseDTO, SectionDTO
from scraper.models import Course, Section
import constants as c

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
        id_curso=section[c.ID_CURSO],
        seccion=section[c.SECCION],
        nrc=section[c.NRC],
        profesor=section[c.PROFESOR],
        campus=section[c.CAMPUS],
        en_ingles=section[c.EN_INGLES],
        horario=section[c.HORARIO],
        formato=section[c.FORMATO],
    )

def mapCourseToDTO(course: Course) -> tuple[CourseDTO, list[SectionDTO]]:
    return CourseDTO(
        id=course[c.ID],
        sigla=course[c.SIGLA],
        nombre=course[c.NOMBRE],
        permite_retiro=course[c.PERMITE_RETIRO],
        aprob_especial=course[c.APROB_ESPECIAL],
        area=course[c.AREA],
        creditos=course[c.CREDITOS],
        descripcion=course[c.DESCRIPCION]
    ), [mapSectionToDTO(section) for section in course[c.SECCIONES]]

def mapSectionToDTO(section: Section) -> SectionDTO:
    return SectionDTO(
        id_curso=section[c.ID_CURSO],
        seccion=section[c.SECCION],
        nrc=section[c.NRC],
        profesor=section[c.PROFESOR],
        campus=section[c.CAMPUS],
        en_ingles=section[c.EN_INGLES],
        horario=section[c.HORARIO],
        formato=section[c.FORMATO],
    )