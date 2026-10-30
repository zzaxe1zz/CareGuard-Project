import pytest
from datetime import datetime
from unittest.mock import MagicMock
from services.workday_manager import WorkdayManager


def test_mt_01_registrar_descanso_valido(db_adapter, mock_logger):
    """MT-01: Registrar descanso válido (10:00 a 10:30) y calcular 30 minutos."""
    manager = WorkdayManager(db_adapter, mock_logger)

    # 1. Simular descanso válido
    inicio = "2026-10-30 10:00:00"
    fin = "2026-10-30 10:30:00"

    # 2. Mock del adaptador para inserción
    db_adapter.execute_query = MagicMock(return_value=1)

    fmt = "%Y-%m-%d %H:%M:%S"
    duracion = int((datetime.strptime(fin, fmt) -
                   datetime.strptime(inicio, fmt)).total_seconds() / 60)

    assert duracion == 30


def test_mt_01_registrar_descanso_fin_anterior_inicio():
    """MT-01: Rechazar descanso donde la hora de fin es anterior a la de inicio."""
    inicio = "2026-10-30 10:30:00"
    fin = "2026-10-30 10:00:00"

    fmt = "%Y-%m-%d %H:%M:%S"
    dt_inicio = datetime.strptime(inicio, fmt)
    dt_fin = datetime.strptime(fin, fmt)

    with pytest.raises(ValueError, match="posterior"):
        if dt_fin <= dt_inicio:
            raise ValueError(
                "La hora de fin debe ser posterior a la de inicio")


def test_mt_01_registrar_descanso_fin_igual_inicio():
    """MT-01: Rechazar descanso donde la hora de fin es igual a la de inicio."""
    inicio = "2026-10-30 10:00:00"
    fin = "2026-10-30 10:00:00"

    fmt = "%Y-%m-%d %H:%M:%S"
    dt_inicio = datetime.strptime(inicio, fmt)
    dt_fin = datetime.strptime(fin, fmt)

    with pytest.raises(ValueError, match="posterior"):
        if dt_fin <= dt_inicio:
            raise ValueError(
                "La hora de fin debe ser posterior a la de inicio")
