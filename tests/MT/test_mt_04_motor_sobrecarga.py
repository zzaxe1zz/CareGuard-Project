"""MT-04: Cálculo de Horas y Regla de Sobrecarga (WorkdayManager + BurnoutEngine)."""
from datetime import datetime, timedelta

import pytest

from services.burnout_engine import BurnoutEngine
from services.workday_manager import WorkdayManager
from tests.conftest import FMT, contar

pytestmark = pytest.mark.unit


@pytest.fixture
def medico(crear_usuario):
    return crear_usuario("medico_mt04")


@pytest.fixture
def motor(db_adapter, mock_logger):
    return BurnoutEngine(db_adapter, mock_logger)


def test_mt_04_01_calculo_horas_totales_y_horas_extra(db_adapter, mock_logger, medico):
    manager = WorkdayManager(db_adapter, mock_logger)
    for horas, extra in [(10, 2.0), (8, 0.0), (6, 0.0)]:
        entrada = (datetime.now() - timedelta(hours=horas)).strftime(FMT)
        id_j = db_adapter.ejecutar(
            "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, ?, ?)",
            (medico, entrada[:10], entrada))
        res = manager.registrar_salida(id_j, medico)
        assert res["horas_trabajadas"] == pytest.approx(horas, abs=0.01)
        assert res["horas_extra"] == pytest.approx(extra, abs=0.01)
        fila = db_adapter.obtener_uno(
            "SELECT horas_extra, hora_salida FROM jornadas WHERE id_jornada = ?", (id_j,))
        assert fila["hora_salida"] is not None
        assert fila["horas_extra"] == pytest.approx(extra, abs=0.01)


def test_mt_04_02_mas_12h_extra_en_7_dias_riesgo_true(db_adapter, motor, medico, crear_jornada):
    crear_jornada(medico, 0, horas_extra=6.5)
    crear_jornada(medico, 1, horas_extra=6.5)            # 13.0 h en 7 días
    id_alerta = motor.evaluar_sobrecarga(medico)
    assert id_alerta is not None
    fila = db_adapter.obtener_uno("SELECT tipo, estado, motivo FROM alertas WHERE id_alerta = ?", (id_alerta,))
    assert (fila["tipo"], fila["estado"]) == ("ALGORITMO", "PENDIENTE")
    assert "Sobrecarga horaria" in fila["motivo"]


def test_mt_04_03_exactamente_12h_extra_en_7_dias_riesgo_false(db_adapter, motor, medico, crear_jornada):
    crear_jornada(medico, 0, horas_extra=6.0)
    crear_jornada(medico, 1, horas_extra=6.0)            # exactamente 12.0 h
    assert motor.evaluar_sobrecarga(medico) is None
    assert contar(db_adapter, "alertas") == 0


def test_mt_04_04_3_dias_estres_alto_riesgo_true(db_adapter, motor, medico, crear_jornada, crear_estado):
    for dias, nivel in [(2, 8), (1, 7), (0, 9)]:
        crear_estado(medico, crear_jornada(medico, dias), nivel, dias)
    id_alerta = motor.evaluar_sobrecarga(medico)
    assert id_alerta is not None
    motivo = db_adapter.obtener_uno("SELECT motivo FROM alertas WHERE id_alerta = ?", (id_alerta,))["motivo"]
    assert "Estrés crónico" in motivo


def test_mt_04_05_2_dias_estres_alto_riesgo_false(db_adapter, motor, medico, crear_jornada, crear_estado):
    for dias, nivel in [(1, 8), (0, 9)]:
        crear_estado(medico, crear_jornada(medico, dias), nivel, dias)
    assert motor.evaluar_sobrecarga(medico) is None
    assert contar(db_adapter, "alertas") == 0
