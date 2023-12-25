from typing import TypedDict
from dataclasses import dataclass
import global_constants as gc

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

class OFG(TypedDict):
    sigla: str
    nombre: str
    creditos: int
    permite_retiro: bool
    aprob_especial: bool
    descripcion: str

@dataclass
class Filter():
    campus: str = gc.OPCIONES_CAMPUS[0]
    formato: str = gc.OPCIONES_FORMATO[0]
    creditos: str = gc.OPCIONES_CREDITOS[0]
    en_ingles: str = gc.OPCIONES_EN_INGLES[0]
    permite_retiro: str = gc.OPCIONES_PERMITE_RETIRO[0]
