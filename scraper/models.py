from typing import TypedDict

class Section(TypedDict):
    id_curso: int
    seccion: int
    nrc: int
    profesor: str
    campus: str
    en_ingles: bool
    horario: dict
    formato: str

class Course(TypedDict):
    id: int
    sigla: str
    nombre: str
    permite_retiro: bool
    aprob_especial: bool
    area: str | None
    creditos: int
    descripcion: str
    secciones: list[Section]