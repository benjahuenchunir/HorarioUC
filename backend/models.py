from typing import TypedDict
from dataclasses import dataclass

class GroupedSection(TypedDict):
    id_curso: int
    sigla: str
    nombre: str
    secciones: list[int]
    nrcs: list[int]
    profesores: list[str]
    campuses: list[str]
    en_ingles: list[bool]
    formatos: list[str]
    horario: dict[str, dict]

class Course(TypedDict):
    id: int
    sigla: str
    nombre: str
    permite_retiro: bool
    aprob_especial: bool
    area: str | None
    creditos: int
    descripcion: str
    secciones: list[GroupedSection]

@dataclass
class Filter():
    campus: str
    formato: str
    creditos: str
    en_ingles: str
    permite_retiro: str

