"""IT-02: Solicitud Voluntaria de Apoyo a Psicología (Médico -> Alerta -> Bandeja)."""
import json

import pytest

from controllers.admin_controller import AdminController
from controllers.medical_controller import MedicalController
from controllers.psychology_controller import PsychologyController

pytestmark = pytest.mark.integration


@pytest.fixture
def ctx(db_adapter, mock_logger, crear_usuario, sesion):
    ids = {n: crear_usuario(n, r, nombre=f"Persona {n}") for n, r in
           [("med_a", "MEDICO"), ("med_b", "MEDICO"), ("psico", "PSICOLOGO"), ("adm", "ADMIN")]}
    s = lambda n, r: sesion(ids[n], r, n)
    medico = MedicalController(s("med_a", "MEDICO"), db_adapter, mock_logger)
    medico.solicitar_apoyo_psicologico("Me siento rebasado")
    return ids, s, medico, db_adapter, mock_logger


def test_it_02_01_registro_de_tipo_voluntario_creado(ctx):
    ids, _, _, db, _ = ctx
    fila = db.obtener_uno("SELECT * FROM alertas")
    assert fila["tipo"] == "VOLUNTARIO" and fila["estado"] == "PENDIENTE"
    assert fila["id_usuario"] == ids["med_a"]
    assert "Me siento rebasado" in fila["motivo"]


def test_it_02_02_visible_en_la_bandeja_de_psicologia(ctx):
    ids, s, _, db, log = ctx
    bandeja = PsychologyController(s("psico", "PSICOLOGO"), db, log).consultar_bandeja_alertas()
    assert len(bandeja) == 1
    assert bandeja[0].tipo == "VOLUNTARIO" and bandeja[0].id_usuario == ids["med_a"]


def test_it_02_03_no_visible_para_administrador(ctx):
    _, s, _, db, log = ctx
    with pytest.raises(PermissionError):
        PsychologyController(s("adm", "ADMIN"), db, log)
    metricas = json.dumps(AdminController(s("adm", "ADMIN"), db, log).obtener_metricas_dashboard(), default=str)
    assert "Me siento rebasado" not in metricas and "Persona med_a" not in metricas


def test_it_02_04_no_visible_para_otros_medicos(ctx):
    _, s, _, db, log = ctx
    with pytest.raises(PermissionError):
        PsychologyController(s("med_b", "MEDICO"), db, log)
    otro = MedicalController(s("med_b", "MEDICO"), db, log)
    vistos = json.dumps([otro.consultar_resumen_semanal(), otro.consultar_historial_propio()], default=str)
    assert "Me siento rebasado" not in vistos and "Persona med_a" not in vistos
