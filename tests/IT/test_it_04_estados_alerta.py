"""IT-04: Gestión de Estado de Alertas y Bitácora (PsychologyController)."""
import pytest

from controllers.psychology_controller import PsychologyController
from tests.conftest import contar

pytestmark = pytest.mark.integration


@pytest.fixture
def ctx(db_adapter, mock_logger, crear_usuario, sesion):
    med = crear_usuario("med_it04", "MEDICO")
    psi = crear_usuario("psi_it04", "PSICOLOGO")

    def nueva_alerta():
        return db_adapter.ejecutar(
            "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'm')", (med,))

    ctrl = PsychologyController(sesion(psi, "PSICOLOGO", "psi"), db_adapter, mock_logger)
    return ctrl, nueva_alerta, psi, db_adapter


def estado(db, id_alerta):
    return db.obtener_uno("SELECT estado FROM alertas WHERE id_alerta = ?", (id_alerta,))["estado"]


def test_it_04_01_pendiente_a_en_atencion_con_nota(ctx):
    ctrl, nueva, psi, db = ctx
    id_a = nueva()
    assert ctrl.actualizar_estado_alerta(id_a, "EN_ATENCION", "Se contactó al profesional") is True
    assert estado(db, id_a) == "EN_ATENCION"
    nota = db.obtener_uno("SELECT * FROM bitacora_psicologia WHERE id_alerta = ?", (id_a,))
    assert nota["observacion"] == "Se contactó al profesional" and nota["id_psicologo"] == psi
    assert ctrl.consultar_notas(id_a)[0]["observacion"] == "Se contactó al profesional"


def test_it_04_02_en_atencion_a_cerrada_con_nota(ctx):
    ctrl, nueva, _, db = ctx
    id_a = nueva()
    ctrl.actualizar_estado_alerta(id_a, "EN_ATENCION", "inicio")
    ctrl.actualizar_estado_alerta(id_a, "CERRADA", "caso resuelto")
    assert estado(db, id_a) == "CERRADA"
    assert contar(db, "bitacora_psicologia") == 2


def test_it_04_03_salto_pendiente_a_cerrada_rechazado(ctx):
    ctrl, nueva, _, db = ctx
    id_a = nueva()
    with pytest.raises(ValueError, match="Transición"):
        ctrl.actualizar_estado_alerta(id_a, "CERRADA", "salto")
    assert estado(db, id_a) == "PENDIENTE" and contar(db, "bitacora_psicologia") == 0
    # otros rechazos: estado inexistente y alerta inexistente
    with pytest.raises(ValueError, match="no válido"):
        ctrl.actualizar_estado_alerta(id_a, "ARCHIVADA", "x")
    with pytest.raises(ValueError, match="no encontrada"):
        ctrl.actualizar_estado_alerta(9999, "EN_ATENCION", "x")


def test_it_04_04_retroceso_de_estado_rechazado(ctx):
    ctrl, nueva, _, db = ctx
    escenarios = [(["EN_ATENCION"], "PENDIENTE"),
                  (["EN_ATENCION", "CERRADA"], "EN_ATENCION"),
                  (["EN_ATENCION", "CERRADA"], "PENDIENTE")]
    for pasos, retroceso in escenarios:
        id_a = nueva()
        for p in pasos:
            ctrl.actualizar_estado_alerta(id_a, p, "avance")
        ultimo, notas = estado(db, id_a), contar(db, "bitacora_psicologia")
        with pytest.raises(ValueError, match="Transición"):
            ctrl.actualizar_estado_alerta(id_a, retroceso, "retroceso")
        assert estado(db, id_a) == ultimo and contar(db, "bitacora_psicologia") == notas
