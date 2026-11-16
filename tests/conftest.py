import logging
import os
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from database.audit_logger import AuditLogger
from database.db_adapter import DatabaseAdapter
from models.dto import SessionDTO
from utils.security import generar_salt, hash_password

SCHEMA_PATH = os.path.join(os.path.dirname(
    __file__), "..", "database", "schema.sql")

FMT = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def db_adapter(tmp_path):
    """DatabaseAdapter real sobre un archivo SQLite temporal con el schema.sql real.

    No se usa ':memory:' porque DatabaseAdapter abre una conexión nueva por consulta
    y cada conexión a ':memory:' sería una BD vacía distinta.
    """
    return DatabaseAdapter(str(tmp_path / "test.db"), schema_path=SCHEMA_PATH)


@pytest.fixture
def db_conn(db_adapter):
    """Conexión directa a la misma BD, para verificaciones con SQL."""
    conn = db_adapter.obtener_conexion()
    yield conn
    conn.close()


@pytest.fixture
def mock_logger():
    return MagicMock(spec=AuditLogger)


@pytest.fixture
def audit_real(tmp_path):
    """AuditLogger real escribiendo en un auditoria.log temporal."""
    logger = logging.getLogger("CareGuardAudit")
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)
    ruta = tmp_path / "auditoria.log"
    audit = AuditLogger(str(ruta))
    audit.ruta = ruta
    yield audit
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)


# ---------- Fábricas de datos ----------

@pytest.fixture
def crear_usuario(db_adapter):
    def _crear(usuario, rol="MEDICO", nombre=None, password="clave1234"):
        salt = generar_salt()
        return db_adapter.ejecutar(
            "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES (?, ?, ?, ?, ?)",
            (nombre or f"Nombre {usuario}", usuario,
             hash_password(password, salt), salt, rol))
    return _crear


@pytest.fixture
def crear_jornada(db_adapter):
    def _crear(id_usuario, dias_atras=0, horas_extra=0.0, horas_trabajadas=None):
        dt = datetime.now() - timedelta(days=dias_atras)
        fecha = dt.strftime("%Y-%m-%d")
        trab = horas_trabajadas if horas_trabajadas is not None else 8.0 + horas_extra
        return db_adapter.ejecutar(
            """INSERT INTO jornadas (id_usuario, fecha, hora_entrada, hora_salida,
                                     horas_trabajadas, horas_extra)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (id_usuario, fecha, f"{fecha} 07:00:00", f"{fecha} 20:00:00", trab, horas_extra))
    return _crear


@pytest.fixture
def crear_estado(db_adapter):
    def _crear(id_usuario, id_jornada, estres, dias_atras=0, animo="Estable", notas=""):
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime(FMT)
        return db_adapter.ejecutar(
            """INSERT INTO estados_emocionales
               (id_usuario, id_jornada, fecha_registro, nivel_estres, estado_animo, notas)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (id_usuario, id_jornada, fecha, estres, animo, notas))
    return _crear


@pytest.fixture
def sesion():
    def _sesion(id_usuario, rol, usuario="u"):
        return SessionDTO(id_usuario=id_usuario, nombre=f"N {usuario}",
                          usuario=usuario, rol=rol)
    return _sesion


def contar(db_adapter, tabla):
    return db_adapter.obtener_uno(f"SELECT COUNT(*) AS c FROM {tabla}")["c"]
