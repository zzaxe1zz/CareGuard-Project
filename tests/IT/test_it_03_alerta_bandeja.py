"""IT-03: Alerta de Sobrecarga en la Bandeja de Psicología (Motor -> BD -> Psicología)."""
from datetime import datetime, timedelta

import pytest

from controllers.psychology_controller import PsychologyController
from services.burnout_engine import BurnoutEngine
from tests.conftest import FMT

pytestmark = pytest.mark.integration


@pytest.fixture
def ctx(db_adapter, mock_logger, crear_usuario, crear_jornada, sesion):
    med = crear_usuario("med_it03", "MEDICO", nombre="Dr. Sobrecargado")
    psi = crear_usuario("psi_it03", "PSICOLOGO")
    crear_jornada(med, 0, horas_extra=7.0)
    crear_jornada(med, 1, horas_extra=7.0)   # 14 h extra
    id_alerta = BurnoutEngine(db_adapter, mock_logger).evaluar_sobrecarga(med)
    bandeja = PsychologyController(sesion(psi, "PSICOLOGO", "psi"), db_adapter, mock_logger)
    return med, id_alerta, bandeja, db_adapter


def test_it_03_01_alerta_insertada_en_pendiente_con_id_y_marca_de_tiempo(ctx):
    med, id_alerta, _, db = ctx
    fila = db.obtener_uno("SELECT * FROM alertas WHERE id_alerta = ?", (id_alerta,))
    assert fila["estado"] == "PENDIENTE" and fila["id_usuario"] == med
    assert abs(datetime.now() - datetime.strptime(fila["fecha_generacion"], FMT)) < timedelta(minutes=1)


def test_it_03_02_alerta_visible_en_la_bandeja_de_psicologia(ctx):
    med, id_alerta, bandeja, _ = ctx
    alertas = bandeja.consultar_bandeja_alertas()
    assert [a.id_alerta for a in alertas] == [id_alerta]
    assert alertas[0].nombre_profesional == "Dr. Sobrecargado" and alertas[0].estado == "PENDIENTE"


def test_it_03_03_motivo_del_riesgo_mostrado(ctx):
    _, _, bandeja, _ = ctx
    motivo = bandeja.consultar_bandeja_alertas()[0].motivo
    assert "Sobrecarga horaria" in motivo and "14.0h" in motivo
