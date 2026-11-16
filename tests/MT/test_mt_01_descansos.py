"""MT-01: Registro de Descansos durante la Jornada (RF-01).

Caja blanca sobre WorkdayManager.registrar_descanso con DatabaseAdapter y AuditLogger
simulados (mock). El caso de superposición se verifica además contra SQLite real para
comprobar la consulta SQL.
"""
from unittest.mock import MagicMock

import pytest

from services.workday_manager import WorkdayManager
from tests.conftest import contar

pytestmark = pytest.mark.unit
DIA = "2026-10-30"
ID_JORNADA, ID_USUARIO = 1, 1


@pytest.fixture
def mock_ctx():
    """Precondiciones: jornada abierta simulada y mock de la BD sin descansos previos."""
    db, audit = MagicMock(), MagicMock()
    db.obtener_uno.return_value = None
    return WorkdayManager(db, audit), db, audit


def test_mt_01_01_registrar_descanso_valido_duracion_minutos(mock_ctx):
    manager, db, _ = mock_ctx
    assert manager.registrar_descanso(
        ID_JORNADA, ID_USUARIO, f"{DIA} 10:00:00", f"{DIA} 10:30:00") is True
    assert db.ejecutar.call_args.args[1] == (
        ID_JORNADA, f"{DIA} 10:00:00", f"{DIA} 10:30:00", 30)


def test_mt_01_02_rechazar_fin_anterior_al_inicio(mock_ctx):
    manager, db, audit = mock_ctx
    with pytest.raises(ValueError, match="anterior"):
        manager.registrar_descanso(
            ID_JORNADA, ID_USUARIO, f"{DIA} 10:30:00", f"{DIA} 10:00:00")
    db.ejecutar.assert_not_called()
    assert audit.registrar_evento.call_args.args[3] is False


def test_mt_01_03_rechazar_fin_igual_al_inicio(mock_ctx):
    manager, db, _ = mock_ctx
    with pytest.raises(ValueError, match="anterior"):
        manager.registrar_descanso(
            ID_JORNADA, ID_USUARIO, f"{DIA} 10:00:00", f"{DIA} 10:00:00")
    db.ejecutar.assert_not_called()


def test_mt_01_04_rechazar_descanso_superpuesto(mock_ctx, db_adapter, mock_logger,
                                                crear_usuario, crear_jornada):
    # (a) Con BD simulada que reporta un descanso solapado
    manager, db, _ = mock_ctx
    db.obtener_uno.return_value = {"1": 1}
    with pytest.raises(ValueError, match="superpone"):
        manager.registrar_descanso(
            ID_JORNADA, ID_USUARIO, f"{DIA} 10:15:00", f"{DIA} 10:45:00")
    db.ejecutar.assert_not_called()

    # (b) Con SQLite real: el solapamiento se rechaza y el contiguo se acepta
    id_u = crear_usuario("medico_mt01")
    id_j = crear_jornada(id_u)
    real = WorkdayManager(db_adapter, mock_logger)
    real.registrar_descanso(id_j, id_u, f"{DIA} 10:00:00", f"{DIA} 10:30:00")
    with pytest.raises(ValueError, match="superpone"):
        real.registrar_descanso(id_j, id_u, f"{DIA} 10:15:00", f"{DIA} 10:45:00")
    assert contar(db_adapter, "descansos") == 1
    assert real.registrar_descanso(id_j, id_u, f"{DIA} 10:30:00", f"{DIA} 11:00:00") is True
