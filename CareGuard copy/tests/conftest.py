import pytest
import sqlite3
import os
from unittest.mock import MagicMock
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger

SCHEMA_PATH = os.path.join(os.path.dirname(
    __file__), "..", "database", "schema.sql")


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    else:
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                hash_password TEXT NOT NULL,
                salt TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN')),
                estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO')),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS jornadas (
                id_jornada INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha DATE NOT NULL,
                hora_entrada DATETIME NOT NULL,
                hora_salida DATETIME,
                horas_trabajadas REAL DEFAULT 0.0,
                horas_extra REAL DEFAULT 0.0,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS descansos (
                id_descanso INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jornada INTEGER NOT NULL,
                hora_inicio DATETIME NOT NULL,
                hora_fin DATETIME NOT NULL,
                duracion_minutos INTEGER NOT NULL,
                FOREIGN KEY (id_jornada) REFERENCES jornadas (id_jornada) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS estados_emocionales (
                id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_jornada INTEGER NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                nivel_estres INTEGER NOT NULL CHECK (nivel_estres BETWEEN 1 AND 10),
                estado_animo TEXT NOT NULL,
                notas TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
                FOREIGN KEY (id_jornada) REFERENCES jornadas (id_jornada) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS alertas (
                id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo TEXT NOT NULL CHECK (tipo IN ('ALGORITMO', 'VOLUNTARIO')),
                estado TEXT NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EN_ATENCION', 'CERRADA')),
                motivo TEXT NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS bitacora_psicologia (
                id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
                id_alerta INTEGER NOT NULL,
                id_psicologo INTEGER NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                observacion TEXT NOT NULL,
                FOREIGN KEY (id_alerta) REFERENCES alertas (id_alerta) ON DELETE CASCADE,
                FOREIGN KEY (id_psicologo) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS evaluaciones_pacientes (
                id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                calificacion INTEGER NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
                comentario TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def db_adapter(db_conn):
    adapter = DatabaseAdapter(":memory:")
    adapter.conn = db_conn
    return adapter


@pytest.fixture
def mock_logger():
    return MagicMock(spec=AuditLogger)
