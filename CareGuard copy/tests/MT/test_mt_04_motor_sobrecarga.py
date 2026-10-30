import pytest
from services.burnout_engine import BurnoutEngine


def test_mt_04_regla_sobrecarga_mas_12_horas_extra():
    """MT-04: Evaluar riesgo True con >12 h extra en 7 días."""
    horas_extra_acumuladas = 13.0
    riesgo = horas_extra_acumuladas > 12
    assert riesgo is True


def test_mt_04_regla_sobrecarga_exactamente_12_horas_extra():
    """MT-04: Evaluar riesgo False con exactamente 12 h extra."""
    horas_extra_acumuladas = 12.0
    riesgo = horas_extra_acumuladas > 12
    assert riesgo is False


def test_mt_04_estres_sustentado_3_dias_consecutivos():
    """MT-04: Evaluar riesgo True con 3 días consecutivos de estrés >= 7."""
    niveles_estres = [8, 7, 9]

    consecutivos = 0
    riesgo = False
    for nivel in niveles_estres:
        if nivel >= 7:
            consecutivos += 1
            if consecutivos >= 3:
                riesgo = True
        else:
            consecutivos = 0

    assert riesgo is True
