"""ST-01: Consulta de Historial Personal Restringido (aislamiento entre profesionales)."""
import pytest

from controllers.medical_controller import MedicalController

pytestmark = pytest.mark.system


@pytest.fixture
def mundo(db_adapter, mock_logger, crear_usuario, crear_jornada, crear_estado, sesion):
    a = crear_usuario("medico_a", "MEDICO", nombre="Médico A")
    b = crear_usuario("enfermero_b", "ENFERMERO", nombre="Enfermero B")
    jA = crear_jornada(a, 0, horas_extra=3.0)
    jB = crear_jornada(b, 0, horas_extra=1.0)
    db_adapter.ejecutar("INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos) VALUES (?, '2026-10-30 12:00:00', '2026-10-30 12:30:00', 30)", (jA,))
    db_adapter.ejecutar("INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos) VALUES (?, '2026-10-30 13:00:00', '2026-10-30 13:20:00', 20)", (jB,))
    crear_estado(a, jA, 9, animo="AnimoSoloA", notas="NOTA_PRIVADA_A")
    crear_estado(b, jB, 4, animo="AnimoSoloB", notas="NOTA_PRIVADA_B")
    ctrl = lambda i, r: MedicalController(sesion(i, r), db_adapter, mock_logger)
    return ctrl(a, "MEDICO"), ctrl(b, "ENFERMERO"), jA, jB


def test_st_01_01_sesion_medico_a_jornadas_horas_extra_descansos_y_animo(mundo):
    ctrl_a, _, jA, _ = mundo
    r = ctrl_a.consultar_resumen_semanal()
    assert [f["id_jornada"] for f in r["filas"]] == [jA]
    assert r["filas"][0]["horas_extra"] == 3.0
    assert r["pausas"] == 1                                   # descansos del propio usuario
    assert (r["filas"][0]["estado_animo"], r["filas"][0]["nivel_estres"]) == ("AnimoSoloA", 9)
    assert [j["id_jornada"] for j in ctrl_a.consultar_historial_propio()] == [jA]


def test_st_01_02_sesion_enfermero_b_solo_sus_propios_registros(mundo):
    _, ctrl_b, _, jB = mundo
    r = ctrl_b.consultar_resumen_semanal()
    assert [f["id_jornada"] for f in r["filas"]] == [jB]
    assert r["pausas"] == 1
    assert [f["estado_animo"] for f in r["filas"]] == ["AnimoSoloB"]
    assert [j["id_jornada"] for j in ctrl_b.consultar_historial_propio()] == [jB]


def test_st_01_03_sin_datos_de_a_visibles_para_b(mundo):
    _, ctrl_b, jA, _ = mundo
    vistos = str(ctrl_b.consultar_resumen_semanal()) + str(ctrl_b.consultar_historial_propio())
    assert "NOTA_PRIVADA_A" not in vistos and "AnimoSoloA" not in vistos
    assert all(f["id_jornada"] != jA for f in ctrl_b.consultar_resumen_semanal()["filas"])
    assert all(j["id_jornada"] != jA for j in ctrl_b.consultar_historial_propio())
