from backend.database.tables import CourseDTO, SectionDTO
from backend.models import Course, GroupedSection
import global_constants as c
from itertools import groupby
from operator import itemgetter
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
        secciones=group_courses_by_schedule(course[c.ID], secciones)
    )

def group_courses_by_schedule(course_id: int, sections: list[SectionDTO]) -> list[GroupedSection]:
    """
    Groups the sections of a course by the horario dict.
    """
    sections.sort(key=itemgetter(c.HORARIO))

    return [
        GroupedSection(
            id_curso=course_id,
            secciones=[section[c.SECCION] for section in sections],
            nrcs=[section[c.NRC] for section in sections],
            profesores=[section[c.PROFESOR] for section in sections],
            campuses=[section[c.CAMPUS] for section in sections],
            en_ingles=[section[c.EN_INGLES] for section in sections],
            formatos=[section[c.FORMATO] for section in sections],
            horario=json.loads(horario),
        )
        for horario, sections in groupby(sections, key=itemgetter(c.HORARIO))
    ]
