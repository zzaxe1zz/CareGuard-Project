"""MT-05: Generación e Inmutabilidad de la Alerta (BurnoutEngine + triggers de schema.sql)."""
import sqlite3
from datetime import datetime, timedelta

import pytest

from services.burnout_engine import BurnoutEngine
from tests.conftest import FMT, contar

pytestmark = pytest.mark.unit


@pytest.fixture
def alerta(db_adapter, mock_logger, crear_usuario, crear_jornada):
    id_u = crear_usuario("medico_mt05")
    crear_jornada(id_u, 0, horas_extra=13.0)
    return BurnoutEngine(db_adapter, mock_logger).evaluar_sobrecarga(id_u), id_u


def test_mt_05_01_alerta_creada_en_estado_pendiente(db_adapter, alerta):
    id_alerta, _ = alerta
    fila = db_adapter.obtener_uno("SELECT estado, tipo FROM alertas WHERE id_alerta = ?", (id_alerta,))
    assert (fila["estado"], fila["tipo"]) == ("PENDIENTE", "ALGORITMO")


def test_mt_05_02_id_profesional_y_marca_tiempo_correctos(db_adapter, alerta):
    id_alerta, id_u = alerta
    fila = db_adapter.obtener_uno("SELECT id_usuario, fecha_generacion FROM alertas WHERE id_alerta = ?", (id_alerta,))
    assert fila["id_usuario"] == id_u
    generada = datetime.strptime(fila["fecha_generacion"], FMT)
    assert abs(datetime.now() - generada) < timedelta(minutes=1)


def test_mt_05_03_edicion_de_alerta_rechazada(db_adapter, alerta):
    id_alerta, _ = alerta
    for columna, valor in [("motivo", "alterado"), ("tipo", "VOLUNTARIO"), ("id_usuario", 999),
                           ("fecha_generacion", "2000-01-01 00:00:00"), ("id_alerta", 777)]:
        with pytest.raises(sqlite3.DatabaseError, match="inmutable"):
            db_adapter.ejecutar(f"UPDATE alertas SET {columna} = ? WHERE id_alerta = ?", (valor, id_alerta))
    # el estado sí puede cambiar (lo usa Psicología)
    db_adapter.ejecutar("UPDATE alertas SET estado = 'EN_ATENCION' WHERE id_alerta = ?", (id_alerta,))
    assert db_adapter.obtener_uno("SELECT estado FROM alertas WHERE id_alerta = ?", (id_alerta,))["estado"] == "EN_ATENCION"


def test_mt_05_04_borrado_de_alerta_rechazado(db_adapter, alerta):
    id_alerta, _ = alerta
    with pytest.raises(sqlite3.DatabaseError, match="inmutable"):
        db_adapter.ejecutar("DELETE FROM alertas WHERE id_alerta = ?", (id_alerta,))
    assert contar(db_adapter, "alertas") == 1
