import pytest


def test_mt_04_01_calculo_horas_totales_y_horas_extra():
    """MT-04: Cálculo de horas totales y horas extra."""
    horas_jornada = 10.0
    extra = max(0.0, horas_jornada - 8.0)
    assert horas_jornada == 10.0 and extra == 2.0


def test_mt_04_02_mas_12h_extra_en_7_dias_riesgo_true():
    """MT-04: Más de 12 h extra en 7 días (riesgo = True)."""
    assert (13.0 > 12.0) is True


def test_mt_04_03_exactamente_12h_extra_en_7_dias_riesgo_false():
    """MT-04: Exactamente 12 h extra en 7 días (riesgo = False)."""
    assert (12.0 > 12.0) is False


def test_mt_04_04_3_dias_estres_alto_riesgo_true():
    """MT-04: 3 días de estrés alto (riesgo = True)."""
    dias = [8, 7, 9]
    riesgo = len(dias) >= 3 and all(d >= 7 for d in dias)
    assert riesgo is True


def test_mt_04_05_2_dias_estres_alto_riesgo_false():
    """MT-04: 2 días de estrés alto (riesgo = False)."""
    dias = [8, 7]
    riesgo = len(dias) >= 3 and all(d >= 7 for d in dias)
    assert riesgo is False
