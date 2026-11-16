"""IT-01: Estado de Ánimo y Nivel de Estrés (MedicalController -> BD)."""
import pytest

from controllers.medical_controller import MedicalController
from tests.conftest import contar

pytestmark = pytest.mark.integration


@pytest.fixture
def ctx(db_adapter, mock_logger, crear_usuario, sesion):
    a, b = crear_usuario("medico_a", "MEDICO"), crear_usuario("medico_b", "MEDICO")
    ctrl_a = MedicalController(sesion(a, "MEDICO", "medico_a"), db_adapter, mock_logger)
    ctrl_b = MedicalController(sesion(b, "MEDICO", "medico_b"), db_adapter, mock_logger)
    return ctrl_a, ctrl_b, a, b, db_adapter


def test_it_01_01_guardar_la_evaluacion(ctx):
    """Guardar la evaluación (la GUI invoca este mismo método del controlador)."""
    ctrl_a, _, _, _, db = ctx
    id_j = ctrl_a.iniciar_jornada()
    for invalido in (0, 11):                       # fuera de rango: no se guarda
        with pytest.raises(ValueError):
            ctrl_a.finalizar_jornada_y_evaluar(id_j, invalido, "X")
    assert contar(db, "estados_emocionales") == 0
    ctrl_a.finalizar_jornada_y_evaluar(id_j, 6, "Agotado", "Turno largo")
    fila = db.obtener_uno("SELECT * FROM estados_emocionales")
    assert (fila["nivel_estres"], fila["estado_animo"], fila["notas"]) == (6, "Agotado", "Turno largo")
    assert fila["id_jornada"] == id_j
    assert db.obtener_uno("SELECT hora_salida FROM jornadas WHERE id_jornada = ?", (id_j,))["hora_salida"]


def test_it_01_02_registro_vinculado_al_usuario_en_sesion(ctx):
    ctrl_a, ctrl_b, a, b, db = ctx
    for ctrl in (ctrl_a, ctrl_b):                  # con ambos usuarios: un id fijo no pasaría
        ctrl.finalizar_jornada_y_evaluar(ctrl.iniciar_jornada(), 5, "Estable")
    filas = db.obtener_todos("SELECT id_usuario FROM estados_emocionales ORDER BY id_estado")
    assert [f["id_usuario"] for f in filas] == [a, b]


def test_it_01_03_otras_tablas_sin_alteracion(ctx):
    ctrl_a, _, _, _, db = ctx
    antes = {t: contar(db, t) for t in ("usuarios", "descansos", "alertas", "bitacora_psicologia",
                                         "evaluaciones_pacientes", "citas", "notificaciones")}
    ctrl_a.finalizar_jornada_y_evaluar(ctrl_a.iniciar_jornada(), 4, "Estable")
    assert {t: contar(db, t) for t in antes} == antes
    assert contar(db, "estados_emocionales") == 1


def test_it_01_04_registro_no_visible_para_otro_medico(ctx):
    ctrl_a, ctrl_b, _, _, _ = ctx
    ctrl_a.finalizar_jornada_y_evaluar(ctrl_a.iniciar_jornada(), 5, "Reservado", "NOTA_CONFIDENCIAL_A")
    filas_a = ctrl_a.consultar_resumen_semanal()["filas"]
    assert [f["estado_animo"] for f in filas_a] == ["Reservado"]
    assert all(f["estado_animo"] is None for f in ctrl_b.consultar_resumen_semanal()["filas"])
    assert "Reservado" not in str(ctrl_b.consultar_resumen_semanal())
    assert "NOTA_CONFIDENCIAL_A" not in str(ctrl_b.consultar_historial_propio())
