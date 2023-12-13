import mysql.connector
import os
import subprocess
import datetime
import constants as c
import sample_data as s
from icecream import ic

# Conexion con la base de datos
acceso_bd = {"host" : "localhost",
             "user" : "root",
             "password" : "",
             }

# Obtenemos la raíz de la carpeta del proyecto
carpeta_principal = os.path.dirname(__file__)

carpeta_respaldo = os.path.join(carpeta_principal, "respaldo")

class BaseDatos:
    # Conexión y cursor
    def __init__(self, **kwargs):
        self.conector = mysql.connector.connect(**kwargs)
        self.cursor = self.conector.cursor()
        self.host = kwargs["host"]
        self.usuario = kwargs["user"]
        self.contrasena = kwargs["password"]
        self.conexion_cerrada = False
        # Avisa de que se abrió la conexión con el servidor
        print("Se abrió la conexión con el servidor.")
    
    #Decoradora para el reporte de bases de datos en el servidor
    def reporte_bd(funcion_parametro):
        def interno(self, nombre_bd):
            funcion_parametro(self, nombre_bd) # type: ignore
            BaseDatos.mostrar_bd(self)
        return interno
    
    # Decorador para el cierre del cursor y la base de datos
    def conexion(funcion_parametro):
        def interno(self, *args, **kwargs):
            try:
                if self.conexion_cerrada:
                    self.conector = mysql.connector.connect(
                        host = self.host,
                        user = self.usuario,
                        password = self.contrasena
                    )
                    self.cursor = self.conector.cursor()
                    self.conexion_cerrada = False
                    print("Se abrió la conexión con el servidor.")
                # Se llama a la función externa
                funcion_parametro(self, *args, **kwargs) # type: ignore
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
                    print("Se cerró la conexión con el servidor.")
                    self.conexion_cerrada = True
        return interno

    # Decorador para comprobar si existe una base de datos
    def comprueba_bd(funcion_parametro):
        def interno(self, nombre_bd, *args):
            # Verifica si la base de datos existe en el servidor
            sql = f"SHOW DATABASES LIKE '{nombre_bd}'"
            self.cursor.execute(sql)
            resultado = self.cursor.fetchone()
            
            # Si la base de datos no existe, muestra un mensaje de error
            if not resultado:
                print(f'La base de datos {nombre_bd} no existe.')
                return
            # Ejecuta la función decorada y devuelve el resultado
            return funcion_parametro(self, nombre_bd, *args) # type: ignore
        return interno
    
    @conexion
    def mostrar_bd(self):
        try:
            # Se informa de que se están obteniendo las bases de datos
            print("Aquí tienes el listado de las bases de datos del servidor:")
            # Realiza la consulta para mostrar las bases de datos
            self.cursor.execute("SHOW DATABASES")
            resultado = self.cursor.fetchall()
            # Recorre los resultados y los muestra por pantalla
            for bd in resultado:
                print(f"-{bd[0]}.")
        except:
            # Si ocurre una excepción, se avisa en la consola
            print("No se pudieron obtener las bases de datos. Comprueba la conexión con el servidor.")
    
    #Crear bases de datos
    @conexion
    @reporte_bd
    def crear_bd(self, nombre_bd):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}")
            print(f"Se creó la base de datos {nombre_bd} o ya estaba creada.")
        except:
            print(f"Ocurrió un error al intentar crear la base de datos {nombre_bd}.")
    
    @conexion
    @comprueba_bd
    def crear_tabla(self, nombre_bd: str, nombre_tabla: str, columnas: list[dict]):
        try:
            #String para guardar el string con las columnas y tipos de datos
            columnas_string = ""
            # Lista para guardar las claves primarias
            primary_keys = []
            # Lista para guardar las claves foráneas
            foreign_keys = []
            #Se itera la lista que se le pasa como argumento (cada diccionario)
            for columna in columnas:
                #formamos el string con nombre, tipo y longitud
                if columna['type'].lower() in ['bool', 'boolean']:
                    columnas_string += f"{columna['name']} {columna['type']}"
                else:
                    columnas_string += f"{columna['name']} {columna['type']}({columna['length']})"
                #Si es clave primaria, auto_increment o no admite valores nulos, lo añade al string
                if columna.get('primary_key', False):
                    primary_keys.append(columna['name'])
                if columna.get('auto_increment', False):
                    columnas_string += " AUTO_INCREMENT"
                if columna.get('not_null', False):
                    columnas_string += " NOT NULL"
                if columna.get('unique', False):  # Check if 'unique' key exists and if it's set to True
                    columnas_string += " UNIQUE"
                if 'foreign_key' in columna:
                    foreign_keys.append((columna['name'], columna['foreign_key']['table'], columna['foreign_key']['column'], columna['foreign_key'].get('on_delete', 'NO ACTION')))
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
            # Le indica que base de datos utilizar
            self.cursor.execute(f"USE {nombre_bd}")
            #Se crea la tabla juntando la instrucción SQL con el string generado
            sql = f"CREATE TABLE {nombre_tabla} ({columnas_string});"
            #Se ejecuta la instrucción
            self.cursor.execute(sql)
            #Se hace efectiva
            self.conector.commit()
            # Se informa de que la creación se ha efectuado correctamente.
            print("Se creó la tabla correctamente.")
        except Exception as e:
            print("Ocurrió un error al intentar crear la tabla.")
            print(e)
    
    #Consultas SQL 
    @conexion   
    def consulta(self, sql):
        try:
            self.cursor.execute(sql)
            print("Esta es la salida de la instrucción que has introducido:")
            print(self.cursor.fetchall())
        except:
            print("Ocurrió un error. Revisa la instrucción SQL.")
    
    # Método para insertar registros en una tabla
    @conexion
    def insertar_registro(self, nombre_bd, nombre_tabla, registros):
        self.cursor.execute(f"USE {nombre_bd}")

        if not registros:  # Si la lista está vacía
            print("La lista de registro está vacía.")
            return

        # Obtener las columnas del primer registro
        columnas = list(registros[0].keys())
        columnas_string = ', '.join(columnas)

        # Crear una lista de strings de valores para cada registro
        for registro in registros:
            valores = [registro[columna] for columna in columnas]
            valores_string = ', '.join([f"'{valor}'" for valor in valores])

            # Crear la instrucción de inserción
            sql = f"INSERT INTO {nombre_tabla} ({columnas_string}) VALUES ({valores_string})"
            try:
                self.cursor.execute(sql)
                self.conector.commit()
                print(f"Registro {registro} añadido a la tabla.")
            except Exception as e:
                print(f"Ocurrió un error al intentar insertar el registro {registro}:\n {e}")
    
    def crear_dependencias(self):
        self.crear_bd(c.DATABASE)
        self.crear_tabla(c.DATABASE, c.TABLA_CURSOS, c.COLUMNAS_CURSOS)
        self.crear_tabla(c.DATABASE, c.TABLA_SECCIONES, c.COLUMNAS_SECCIONES)

if __name__ == "__main__":
    # Conectar a la base de datos y crear las tablas necesarias
    bd = BaseDatos(**acceso_bd)
    bd.crear_dependencias()
    bd.insertar_registro(c.DATABASE, c.TABLA_CURSOS, s.SAMPLE_CURSOS)
    bd.insertar_registro(c.DATABASE, c.TABLA_SECCIONES, s.SAMPLE_SECCIONES)
    