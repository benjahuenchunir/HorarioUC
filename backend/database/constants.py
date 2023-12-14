import global_constants as c

DATABASE_NAME = "horario_uc"
DATABASE_CREDENTIALS = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": DATABASE_NAME
}

TABLA_CURSOS = "cursos"
TABLA_SECCIONES = "secciones"

COLUMNAS_CURSOS = [
    {
        "name": c.ID,
        "type": "INT",
        "length": 10,
        "primary_key": True,
        "auto_increment": True,
        "not_null": True,
    },
    {
        "name": c.SIGLA,
        "type": "VARCHAR",
        "length": 11,
        "not_null": True,
        "unique": True,
    },
    {
        "name": c.NOMBRE,
        "type": "VARCHAR",
        "length": 200,
        "not_null": True,
    },
    {
        "name": c.PERMITE_RETIRO,
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": c.APROB_ESPECIAL,
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": c.AREA,
        "type": "VARCHAR",
        "length": 30,
    },
    {
        "name": c.CREDITOS,
        "type": "INT",
        "length": 2,
        "not_null": True,
    },
    {
        "name": c.DESCRIPCION,
        "type": "VARCHAR",
        "length": 1000,
        "not_null": True,
    },
]

COLUMNAS_SECCIONES = [
    {
        "name": c.ID_CURSO,
        "type": "INT",
        "length": 10,
        "primary_key": True,
        "not_null": True,
        "foreign_key": {"table": TABLA_CURSOS, "column": "id", "on_delete": "CASCADE"},
    },
    {
        "name": c.SECCION,
        "type": "INT",
        "length": 2,
        "primary_key": True,
        "not_null": True,
    },
    {
        "name": c.NRC,
        "type": "INT",
        "length": 10,
        "not_null": True,  
    },
    {
        "name": c.PROFESOR,
        "type": "VARCHAR",
        "length": 100,
        "not_null": True,
    },
    {
        "name": c.CAMPUS,
        "type": "VARCHAR",
        "length": 30,
        "not_null": True,
    },
    {
        "name": c.EN_INGLES,
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": c.FORMATO,
        "type": "VARCHAR",
        "length": 15,
        "not_null": True,
    },
    {
        "name": c.HORARIO,
        "type": "JSON",
        "not_null": True,
    },
]
