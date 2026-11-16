import os
import sqlite3
from contextlib import closing
from typing import Any, List, Optional, Tuple

from utils.paths import DB_PATH, SCHEMA_PATH


class DatabaseAdapter:
    def __init__(self, db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH):
        self.db_path = db_path
        self.schema_path = schema_path
        self.inicializar_bd()

    def obtener_conexion(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar_bd(self) -> None:
        if os.path.exists(self.schema_path):
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with closing(self.obtener_conexion()) as conn:
                conn.executescript(schema_sql)
                self._migrar(conn)
                conn.commit()

    @staticmethod
    def _migrar(conn: sqlite3.Connection) -> None:
        """Agrega columnas nuevas a bases de datos creadas con versiones anteriores."""
        cols = [r["name"] for r in conn.execute(
            "PRAGMA table_info(evaluaciones_pacientes)")]
        if "personal_medico" not in cols:
            conn.execute(
                "ALTER TABLE evaluaciones_pacientes ADD COLUMN personal_medico TEXT")

    def ejecutar(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[int]:
        with closing(self.obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def obtener_todos(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        with closing(self.obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def obtener_uno(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        with closing(self.obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
