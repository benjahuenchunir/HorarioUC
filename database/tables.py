from typing import TypedDict

class CourseDTO(TypedDict):
    id: int
    sigla: str
    nombre: str
    permite_retiro: bool
    aprob_especial: bool
    formato: str
    area: str
    creditos: int
    descripcion: str

class SectionDTO(TypedDict):
    id_curso: int
    seccion: int
    profesor: str
    campus: str
    en_ingles: bool
    horario: str