import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import mysql.connector
import backend.database.constants as c
import global_constants as gc
from backend.database.tables import SectionDTO, CourseDTO

class Database:
    # Conexión y cursor
    def __init__(self):
        self.conector = mysql.connector.connect(**c.DATABASE_CREDENTIALS)
        self.cursor = self.conector.cursor(dictionary=True)
        self.host = c.DATABASE_CREDENTIALS["host"]
        self.usuario = c.DATABASE_CREDENTIALS["user"]
        self.contrasena = c.DATABASE_CREDENTIALS["password"]
        self.database = c.DATABASE_CREDENTIALS["database"]
        self.conexion_cerrada = False
        # Avisa de que se abrió la conexión con el servidor
        print("Se abrió la conexión con el servidor.")
        self.crear_dependencias()

    # Decorador para el cierre del cursor y la base de datos
    def conexion(funcion_parametro):
        def interno(self, *args, **kwargs):
            try:
                if self.conexion_cerrada:
                    self.conector = mysql.connector.connect(
                        host=self.host, user=self.usuario, password=self.contrasena, database=self.database
                    )
                    self.cursor = self.conector.cursor(dictionary=True)
                    self.conexion_cerrada = False
                # Se llama a la función externa
                result = funcion_parametro(self, *args, **kwargs)  # type: ignore
                return result
            except Exception as e:
                # Se informa de un error en la llamada
                print("Ocurrió un error con la llamada.")
                print(e)
            finally:
                if self.conexion_cerrada:
                    pass
                else:
                    # Cerramos el cursor y la conexión
                    self.cursor.close()
                    self.conector.close()
                    self.conexion_cerrada = True

        return interno

    # Crear bases de datos
    @conexion
    def crear_bd(self, nombre_bd):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}")
            print(f"Se creó la base de datos {nombre_bd} o ya estaba creada.")
        except:
            print(f"Ocurrió un error al intentar crear la base de datos {nombre_bd}.")

    @conexion
    def crear_tabla(self, nombre_tabla: str, columnas: list[dict]):
        try:
            # String para guardar el string con las columnas y tipos de datos
            columnas_string = ""
            # Lista para guardar las claves primarias
            primary_keys = []
            # Lista para guardar las claves foráneas
            foreign_keys = []
            # Se itera la lista que se le pasa como argumento (cada diccionario)
            for columna in columnas:
                # formamos el string con nombre, tipo y longitud
                if columna["type"].lower() in ["bool", "boolean", "json"]:
                    columnas_string += f"{columna['name']} {columna['type']}"
                else:
                    columnas_string += (
                        f"{columna['name']} {columna['type']}({columna['length']})"
                    )
                # Si es clave primaria, auto_increment o no admite valores nulos, lo añade al string
                if columna.get("primary_key", False):
                    primary_keys.append(columna["name"])
                if columna.get("auto_increment", False):
                    columnas_string += " AUTO_INCREMENT"
                if columna.get("not_null", False):
                    columnas_string += " NOT NULL"
                if columna.get(
                    "unique", False
                ):  # Check if 'unique' key exists and if it's set to True
                    columnas_string += " UNIQUE"
                if "foreign_key" in columna:
                    foreign_keys.append(
                        (
                            columna["name"],
                            columna["foreign_key"]["table"],
                            columna["foreign_key"]["column"],
                            columna["foreign_key"].get("on_delete", "NO ACTION"),
                        )
                    )
                # Hace un salto de línea después de cada diccionario
                columnas_string += ",\n"
            # Elimina al final del string el salto de línea y la coma
            columnas_string = columnas_string[:-2]
            # Si hay claves primarias, se añaden al string
            if primary_keys:
                columnas_string += ",\n"
                columnas_string += "PRIMARY KEY (" + ",".join(primary_keys) + ")"
            # Si hay claves foráneas, se añaden al string
            for fk in foreign_keys:
                columnas_string += ",\n"
                columnas_string += f"FOREIGN KEY ({fk[0]}) REFERENCES {fk[1]}({fk[2]}) ON DELETE {fk[3]}"
            # Se crea la tabla juntando la instrucción SQL con el string generado
            sql = f"CREATE TABLE {nombre_tabla} ({columnas_string});"
            # Se ejecuta la instrucción
            self.cursor.execute(sql)
            # Se hace efectiva
            self.conector.commit()
            # Se informa de que la creación se ha efectuado correctamente.
            print("Se creó la tabla correctamente.")
        except Exception as e:
            print("Ocurrió un error al intentar crear la tabla.")
            print(e)

    # Consultas SQL
    @conexion
    def consulta(self, sql) -> list:
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("Ocurrió un error. Revisa la instrucción SQL.")
            print(e)
            return []

    # Método para insertar registros en una tabla
    @conexion
    def insertar_registro(self, nombre_tabla, registros) -> list[int]:

        if not registros:  # Si la lista está vacía
            print("La lista de registro está vacía.")
            return []

        # Obtener las columnas del primer registro
        columnas = list(registros[0].keys())
        if gc.ID in columnas:
            columnas.remove(gc.ID)
        columnas_string = ", ".join(columnas)

        inserted_ids = []
        
        # Crear una lista de strings de valores para cada registro
        for registro in registros:
            valores = [registro[columna] for columna in columnas]
            valores_string = ", ".join([f"'{valor}'" for valor in valores])

            # Crear la instrucción de inserción
            sql = f"INSERT INTO {nombre_tabla} ({columnas_string}) VALUES ({valores_string})"
            
            # Si hay claves duplicadas, se actualizan los valores
            updates = ", ".join([f"{columna}=VALUES({columna})" for columna in columnas])
            sql += f" ON DUPLICATE KEY UPDATE {updates}"

            try:
                self.cursor.execute(sql)
                self.conector.commit()
                inserted_id = self.cursor.lastrowid
                print(f"Inserción exitosa. ID: {inserted_id}")
                inserted_ids.append(inserted_id)
                print(f"Registro {registro} añadido a la tabla.")
            except Exception as e:
                print(
                    f"Ocurrió un error al intentar insertar el registro {registro}:\n {e}"
                )
        return inserted_ids

    def crear_dependencias(self):
        self.crear_bd(c.DATABASE_NAME)
        self.crear_tabla(c.TABLA_CURSOS, c.COLUMNAS_CURSOS)
        self.crear_tabla(c.TABLA_SECCIONES, c.COLUMNAS_SECCIONES)
    
    def recuperar_cursos(self) -> list[CourseDTO]:
        sql = f"SELECT * FROM {c.TABLA_CURSOS}"
        return self.consulta(sql)
    
    def recuperar_curso(self, sigla: str) -> CourseDTO | None:
        sql = f"SELECT * FROM {c.TABLA_CURSOS} WHERE {gc.SIGLA} = '{sigla}'"
        resultado = self.consulta(sql)
        if resultado:
            return CourseDTO(**resultado[0])
    
    def recuperar_secciones(self, id_curso: int) -> list[SectionDTO]:
        sql = f"SELECT * FROM {c.TABLA_SECCIONES} WHERE {gc.ID_CURSO} = {id_curso}"
        return self.consulta(sql)
    
    def recuperar_ofgs(self, area: str) -> list[CourseDTO]:
        sql = f"SELECT * FROM {c.TABLA_CURSOS} WHERE {gc.AREA} = '{area}'"
        return self.consulta(sql)


if __name__ == "__main__":
    bd = Database()
