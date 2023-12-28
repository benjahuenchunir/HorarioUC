ID = "id"
SIGLA = "sigla"
NOMBRE = "nombre"
PERMITE_RETIRO = "permite_retiro"
APROB_ESPECIAL = "aprob_especial"
AREA = "area"
CREDITOS = "creditos"
DESCRIPCION = "descripcion"

ID_CURSO = "id_curso"
SECCION = "seccion"
NRC = "nrc"
PROFESOR = "profesor"
CAMPUS = "campus"
EN_INGLES = "en_ingles"
HORARIO = "horario"
FORMATO = "formato"
SECCIONES = "secciones"

NRCS = "nrcs"
PROFESORES = "profesores"
CAMPUSES = "campuses"
FORMATOS = "formatos"

SIGLA_CATEDRA = "CLAS"
SIGLA_LAB = "LAB"
SIGLA_AYUDANTIA = "AYU"
SIGLA_TALLER = "TAL"
SIGLA_PRACTICA = "PRA"
SIGLA_TERRENO = "TER"
SIGLA_TESIS = "TES"
SIGLA_LIB = "LIB"
SIGLA_SUP = "SUP"
TIPOS_CLASES = [SIGLA_CATEDRA, SIGLA_LAB, SIGLA_AYUDANTIA, SIGLA_TALLER, SIGLA_PRACTICA, SIGLA_TERRENO, SIGLA_TESIS, SIGLA_LIB, SIGLA_SUP]

TODAS = 0

ARTES = "Artes"
CSOC = "Ciencias sociales"
CTEC = "Ciencia y tecnologia"
EISU = "Ecologia y sustentabilidad"
FFIL = "Formacion filosofica"
FTEO = "Formacion teologica"
HUMS = "Humanidades"
PMAT = "Pensamiento matematico"
SBIE = "Salud y bienestar"
OFG = {
    ARTES: "ARTS",
    CSOC: "CSOC",
    CTEC: "CTEC",
    EISU: "EISU",
    FFIL: "FFIL",
    FTEO: "FTEO",
    HUMS: "HUMS",
    PMAT: "PMAT",
    SBIE: "SBIE",
}

CUALQUIERA = "Cualquiera"
OPCIONES_CAMPUS = [CUALQUIERA, "San Joaquín", "Casa Central", "Lo Contador", "Oriente", "Villarrica", "Campus externo"]
OPCIONES_FORMATO = [CUALQUIERA, "Presencial", "Remoto", "Híbrido", "Remoto con Act.Presencial"]
OPCIONES_CREDITOS = [CUALQUIERA, "5", "10"]
OPCIONES_EN_INGLES = [CUALQUIERA, "SI", "NO"]
OPCIONES_PERMITE_RETIRO = [CUALQUIERA, "SI", "NO"]

STRING_TO_BOOL = {"SI": 1, "NO": 0}
PATH_SAVED_COMBINATIONS = "saved_combinations/"

CURSOS = "cursos"
COMBINACION_ACTUAL = "combinacion_actual"

SHORT_FORM_TO_SIGLA = {
    "cat": SIGLA_CATEDRA,
    "lab": SIGLA_LAB,
    "ayu": SIGLA_AYUDANTIA,
    "tal": SIGLA_TALLER,
}