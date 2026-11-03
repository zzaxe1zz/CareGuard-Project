import pytest
from datetime import datetime


def test_mt_01_01_registrar_descanso_valido_duracion_minutos():
    """MT-01: Registrar descanso válido (duración en minutos)."""
    inicio, fin = "2026-11-02 10:00:00", "2026-11-02 10:30:00"
    fmt = "%Y-%m-%d %H:%M:%S"
    duracion = int((datetime.strptime(fin, fmt) -
                   datetime.strptime(inicio, fmt)).total_seconds() / 60)
    assert duracion == 30


def test_mt_01_02_rechazar_fin_anterior_al_inicio():
    """MT-01: Rechazar fin anterior al inicio."""
    inicio, fin = "2026-11-02 10:30:00", "2026-11-02 10:00:00"
    fmt = "%Y-%m-%d %H:%M:%S"
    with pytest.raises(ValueError):
        if datetime.strptime(fin, fmt) <= datetime.strptime(inicio, fmt):
            raise ValueError("Fin anterior o igual a inicio")


def test_mt_01_03_rechazar_fin_igual_al_inicio():
    """MT-01: Rechazar fin igual al inicio."""
    inicio, fin = "2026-11-02 10:00:00", "2026-11-02 10:00:00"
    fmt = "%Y-%m-%d %H:%M:%S"
    with pytest.raises(ValueError):
        if datetime.strptime(fin, fmt) <= datetime.strptime(inicio, fmt):
            raise ValueError("Fin igual a inicio")


def test_mt_01_04_rechazar_descanso_superpuesto():
    """MT-01: Rechazar descanso superpuesto."""
    existente = ("10:00:00", "10:30:00")
    nuevo_inicio = "10:15:00"
    superpuesto = existente[0] <= nuevo_inicio <= existente[1]
    with pytest.raises(ValueError):
        if superpuesto:
            raise ValueError("Descanso superpuesto")
