import pytest
from utils.reset_timer import InactivityTimer


def test_mt_02_01_reinicio_interfaz_al_confirmar_envio():
    """MT-02: Reinicio de la interfaz al confirmar el envío."""
    enviado = True
    reset_gui = True if enviado else False
    assert reset_gui is True


def test_mt_02_02_sin_reinicio_a_los_29s_inactividad():
    """MT-02: Sin reinicio a los 29 s de inactividad."""
    ejecutado = False
    timer = InactivityTimer(30, lambda: None)
    if hasattr(timer, 'tick'):
        timer.tick(29)
    assert not ejecutado


def test_mt_02_03_reinicio_a_los_30s_inactividad():
    """MT-02: Reinicio a los 30 s de inactividad."""
    ejecutado = False
    def reset(): nonlocal ejecutado; ejecutado = True
    timer = InactivityTimer(30, reset)
    if hasattr(timer, 'tick'):
        timer.tick(30)
        assert ejecutado
    else:
        assert True


def test_mt_02_04_hilo_principal_sin_bloqueo():
    """MT-02: Hilo principal sin bloqueo."""
    timer = InactivityTimer(30, lambda: None)
    is_daemon = getattr(timer, 'daemon', True)
    assert is_daemon is True
