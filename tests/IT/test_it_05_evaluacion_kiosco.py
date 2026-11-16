"""IT-05: Evaluación Anónima con Comentario en Kiosco (KioskController -> BD -> Dashboard)."""
import pytest

from controllers.admin_controller import AdminController
from controllers.kiosk_controller import KioskController
from tests.conftest import contar

pytestmark = pytest.mark.integration


@pytest.fixture
def ctx(db_adapter, mock_logger):
    return KioskController(db_adapter, mock_logger), db_adapter, mock_logger


def test_it_05_01_calificacion_valida_con_comentario(ctx):
    kiosko, db, _ = ctx
    id_e = kiosko.registrar_evaluacion_anonima(5, "Excelente atención")
    fila = db.obtener_uno("SELECT * FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (id_e,))
    assert (fila["calificacion"], fila["comentario"]) == (5, "Excelente atención")


def test_it_05_02_calificacion_valida_sin_comentario(ctx):
    kiosko, db, _ = ctx
    id_e = kiosko.registrar_evaluacion_anonima(3)
    fila = db.obtener_uno("SELECT * FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (id_e,))
    assert fila["calificacion"] == 3 and fila["comentario"] in ("", None)


def test_it_05_03_valores_fuera_de_rango_rechazados(ctx):
    kiosko, db, _ = ctx
    for valor in (0, 6, -1):
        with pytest.raises(ValueError, match="entre 1 y 5"):
            kiosko.registrar_evaluacion_anonima(valor, "x")
    with pytest.raises((ValueError, TypeError)):        # vacío (sin estrellas)
        kiosko.registrar_evaluacion_anonima(None, "x")
    assert contar(db, "evaluaciones_pacientes") == 0


def test_it_05_04_registro_sin_claves_foraneas_de_usuario_o_paciente(ctx):
    kiosko, db, _ = ctx
    columnas = [c["name"] for c in db.obtener_todos("PRAGMA table_info(evaluaciones_pacientes)")]
    assert not {"id_usuario", "id_paciente"} & set(columnas)
    assert db.obtener_todos("PRAGMA foreign_key_list(evaluaciones_pacientes)") == []
    # el personal médico mencionado (opcional) se guarda solo como texto
    id_e = kiosko.registrar_evaluacion_anonima(5, "ok", "Dr. Ejemplo")
    assert db.obtener_uno("SELECT personal_medico FROM evaluaciones_pacientes WHERE id_evaluacion = ?",
                          (id_e,))["personal_medico"] == "Dr. Ejemplo"


def test_it_05_05_comentario_disponible_para_el_dashboard(ctx, sesion):
    kiosko, db, log = ctx
    kiosko.registrar_evaluacion_anonima(4, "Personal muy atento")
    metricas = AdminController(sesion(1, "ADMIN"), db, log).obtener_metricas_dashboard()
    assert any(c["comentario"] == "Personal muy atento" and c["calificacion"] == 4
               for c in metricas["comentarios_recientes"])
