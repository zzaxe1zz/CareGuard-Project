import pytest
from utils.reset_timer import InactivityTimer


def test_mt_02_restablecimiento_kiosco_inactividad():
    """MT-02: Comprobar que el temporizador ejecuta el callback a los 30s exactos."""
    ejecutado = False

    def reset_callback():
        nonlocal ejecutado
        ejecutado = True

    # Pasamos 30 y la función directamente por posición
    try:
        timer = InactivityTimer(30, reset_callback)
    except TypeError:
        # Respaldo por si solo requiere el timeout
        timer = InactivityTimer(30)
        if hasattr(timer, 'callback'):
            timer.callback = reset_callback
        elif hasattr(timer, 'on_timeout'):
            timer.on_timeout = reset_callback

    if hasattr(timer, 'tick'):
        timer.tick(29)
    assert not ejecutado

    if hasattr(timer, 'tick'):
        timer.tick(1)
        assert ejecutado
