DATABASE = "horario_uc"

TABLA_CURSOS = "cursos"
TABLA_SECCIONES = "secciones"

COLUMNAS_CURSOS = [
    {
        "name": "id",
        "type": "INT",
        "length": 10,
        "primary_key": True,
        "auto_increment": True,
        "not_null": True,
    },
    {
        "name": "sigla",
        "type": "VARCHAR",
        "length": 11,
        "not_null": True,
        "unique": True,
    },
    {
        "name": "nombre",
        "type": "VARCHAR",
        "length": 200,
        "not_null": True,
    },
    {
        "name": "permite_retiro",
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": "aprob_especial",
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": "formato",
        "type": "VARCHAR",
        "length": 15,
        "not_null": True,
    },
    {
        "name": "area",
        "type": "VARCHAR",
        "length": 30,
    },
    {
        "name": "creditos",
        "type": "INT",
        "length": 2,
        "not_null": True,
    },
    {
        "name": "descripcion",
        "type": "VARCHAR",
        "length": 1000,
        "not_null": True,
    }
]

COLUMNAS_SECCIONES = [
    {
        "name": "id_curso",
        "type": "INT",
        "length": 10,
        "primary_key": True,
        "not_null": True,
        "foreign_key": {"table": TABLA_CURSOS, "column": "id", "on_delete": "CASCADE"},
    },
    {
        "name": "seccion",
        "type": "INT",
        "length": 2,
        "primary_key": True,
        "not_null": True,
    },
    {
        "name": "profesor",
        "type": "VARCHAR",
        "length": 100,
        "not_null": True,
    },
    {
        "name": "campus",
        "type": "VARCHAR",
        "length": 30,
        "not_null": True,
    },
    {
        "name": "en_ingles",
        "type": "BOOLEAN",
        "length": None,
        "not_null": True,
    },
    {
        "name": "horario",
        "type": "VARCHAR",
        "length": 100,
        "not_null": True,
    }
]
