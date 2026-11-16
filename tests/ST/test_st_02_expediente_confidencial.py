"""ST-02: Consulta de Expediente Emocional Confidencial (flujo de Psicología)."""
import pytest

from controllers.psychology_controller import PsychologyController
from services.burnout_engine import BurnoutEngine

pytestmark = pytest.mark.system


@pytest.fixture
def mundo(db_adapter, mock_logger, crear_usuario, crear_jornada, crear_estado, sesion):
    med = crear_usuario("med_st02", "MEDICO", nombre="Dra. Expediente")
    psi = crear_usuario("psi_st02", "PSICOLOGO")
    for dias, est in [(2, 8), (1, 7), (0, 9)]:
        crear_estado(med, crear_jornada(med, dias, horas_extra=5.0), est, dias, animo="Agotado", notas=f"nota{dias}")
    BurnoutEngine(db_adapter, mock_logger).evaluar_sobrecarga(med)   # alerta activa del flujo real
    ctrl = PsychologyController(sesion(psi, "PSICOLOGO", "psi"), db_adapter, mock_logger)
    return ctrl, med, db_adapter, mock_logger, sesion


def test_st_02_01_seleccion_del_profesional_con_alerta_activa(mundo):
    ctrl, med, *_ = mundo
    activas = [a for a in ctrl.consultar_bandeja_alertas() if a.estado in ("PENDIENTE", "EN_ATENCION")]
    assert [a.id_usuario for a in activas] == [med]
    assert activas[0].nombre_profesional == "Dra. Expediente"


def test_st_02_02_apertura_del_expediente(mundo):
    ctrl, med, db, log, sesion = mundo
    alerta = ctrl.consultar_bandeja_alertas()[0]
    exp = ctrl.consultar_expediente_confidencial(alerta.id_usuario)
    assert exp["medico"]["id_usuario"] == med and exp["medico"]["nombre"] == "Dra. Expediente"
    assert any(c.args[2] == "CONSULTA_EXPEDIENTE_CONFIDENCIAL" for c in log.registrar_evento.call_args_list)
    with pytest.raises(ValueError, match="no encontrado"):
        ctrl.consultar_expediente_confidencial(9999)
    for rol in ("MEDICO", "ENFERMERO", "ADMIN"):            # otros roles no pueden abrirlo
        with pytest.raises(PermissionError):
            PsychologyController(sesion(1, rol), db, log)


def test_st_02_03_historial_de_estres_animo_y_jornadas_visibles(mundo):
    ctrl, med, *_ = mundo
    exp = ctrl.consultar_expediente_confidencial(med)
    assert [e["nivel_estres"] for e in exp["historial_emocional"]] == [9, 7, 8]
    assert {e["estado_animo"] for e in exp["historial_emocional"]} == {"Agotado"}
    assert len(exp["historial_jornadas"]) == 3
    assert all(j["horas_extra"] == 5.0 for j in exp["historial_jornadas"])
