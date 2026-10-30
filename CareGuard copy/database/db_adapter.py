import sqlite3
import os
from typing import List, Tuple, Any, Optional


class DatabaseAdapter:
    def __init__(self, db_path: str = "careguard.db", schema_path: str = "database/schema.sql"):
        self.db_path = db_path
        self.schema_path = schema_path
        self.inicializar_bd()

    def obtener_conexion(self) -> sqlite3.Connection:
        """Abre una conexión habilitando las claves foráneas."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar_bd(self) -> None:
        """Crea las tablas ejecutando el archivo schema.sql si la BD no existe."""
        if os.path.exists(self.schema_path):
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self.obtener_conexion() as conn:
                conn.executescript(schema_sql)

    def ejecutar(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[int]:
        """Ejecuta una consulta INSERT/UPDATE/DELETE y retorna el ID del último registro generado."""
        with self.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def obtener_todos(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Ejecuta una consulta SELECT y retorna todos los resultados."""
        with self.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def obtener_uno(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Ejecuta una consulta SELECT y retorna un solo resultado."""
        with self.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
