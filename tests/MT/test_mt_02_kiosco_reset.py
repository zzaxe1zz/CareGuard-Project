"""MT-02: Restablecimiento de Interfaz por Envío e Inactividad (InactivityTimer / KioskView).

El kiosco usa InactivityTimer en modo Tkinter (widget.after) y la clase conserva el modo
original con hilo daemon; ambos modos se prueban con un reloj simulado (sin esperar 30 s).
"""
import sys
import time
import types
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from utils import reset_timer
from utils.reset_timer import InactivityTimer

pytestmark = pytest.mark.unit


class RelojFalso:
    """Sustituye a time.time: el tiempo solo avanza cuando la prueba lo indica."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def avanzar(self, segundos):
        self.t += segundos


@pytest.fixture
def reloj(monkeypatch):
    r = RelojFalso()
    monkeypatch.setattr(reset_timer, "time", SimpleNamespace(time=r, sleep=lambda s: None))
    return r


def _timer_tkinter():
    """Modo usado por el kiosco: widget.after(1000, _tick). El widget se simula."""
    llamadas, widget = [], MagicMock()
    timer = InactivityTimer(30, lambda: llamadas.append(1), widget=widget)
    timer.iniciar()
    return timer, llamadas


def _correr_hilo_simulado(monkeypatch, reloj, segundos):
    """Ejecuta el bucle _run del modo hilo de forma síncrona: cada sleep(1) avanza el
    reloj un segundo y el bucle se detiene al llegar a `segundos`."""
    llamadas = []
    timer = InactivityTimer(30, lambda: llamadas.append(1))
    timer._running = True
    timer._last_activity_time = reloj()
    pasos = {"n": 0}

    def sleep(_):
        reloj.avanzar(1)
        pasos["n"] += 1
        if pasos["n"] >= segundos:
            timer._running = False

    monkeypatch.setattr(reset_timer, "time", SimpleNamespace(time=reloj, sleep=sleep))
    timer._run()
    return llamadas


def _importar_kiosk_view(monkeypatch):
    """KioskView importa customtkinter, tkinter y views.ui_kit; se simulan para probar sin pantalla."""
    ctk = types.ModuleType("customtkinter")
    ctk.CTkToplevel = type("CTkToplevel", (), {})
    tk = types.ModuleType("tkinter")
    tk.messagebox = MagicMock()
    ui_kit = MagicMock()
    import views
    monkeypatch.setitem(sys.modules, "customtkinter", ctk)
    monkeypatch.setitem(sys.modules, "tkinter", tk)
    monkeypatch.setitem(sys.modules, "tkinter.messagebox", tk.messagebox)
    monkeypatch.setitem(sys.modules, "views.ui_kit", ui_kit)
    monkeypatch.setattr(views, "ui_kit", ui_kit, raising=False)
    monkeypatch.delitem(sys.modules, "views.components.kiosk_view", raising=False)
    import views.components.kiosk_view as kv
    return kv


def test_mt_02_01_reinicio_interfaz_al_confirmar_envio(monkeypatch):
    kv = _importar_kiosk_view(monkeypatch)
    vista = MagicMock()
    vista.estrellas.get.return_value = 4
    vista.combo_personal.get.return_value = kv.SIN_INDICAR
    vista.entry_comentario.get.return_value = "Buen trato"

    kv.KioskView._enviar_evaluacion(vista)

    # Se registra la evaluación y se muestra la pantalla de agradecimiento
    vista.controller.registrar_evaluacion_anonima.assert_called_once_with(4, "Buen trato", "")
    vista.form.pack_forget.assert_called_once()
    vista.gracias.pack.assert_called_once()
    # ...y se programa el reinicio automático de la interfaz
    vista.after.assert_called_once_with(4000, vista._resetear_pantalla)

    # Al ejecutarse el reinicio, la interfaz queda lista para el siguiente paciente
    kv.KioskView._resetear_pantalla(vista)
    vista.gracias.pack_forget.assert_called()
    vista.estrellas.set.assert_called_with(0)
    vista.combo_personal.set.assert_called_with(kv.SIN_INDICAR)
    vista.entry_comentario.delete.assert_called_with(0, "end")
    assert vista._id_gracias is None


def test_mt_02_02_sin_reinicio_a_los_29s_inactividad(monkeypatch, reloj):
    # Modo Tkinter (el que usa el kiosco)
    timer, llamadas = _timer_tkinter()
    reloj.avanzar(29)
    timer._tick()
    assert llamadas == []
    # Modo hilo original
    assert _correr_hilo_simulado(monkeypatch, RelojFalso(), 29) == []


def test_mt_02_03_reinicio_a_los_30s_inactividad(monkeypatch, reloj):
    # Modo Tkinter
    timer, llamadas = _timer_tkinter()
    reloj.avanzar(30)
    timer._tick()
    assert llamadas == [1]
    reloj.avanzar(29)                 # la cuenta vuelve a empezar tras el reinicio
    timer._tick()
    assert llamadas == [1]
    # La actividad del usuario también reinicia la cuenta
    timer.registrar_actividad()
    reloj.avanzar(29)
    timer._tick()
    assert llamadas == [1]
    # Modo hilo original
    assert _correr_hilo_simulado(monkeypatch, RelojFalso(), 30) == [1]


def test_mt_02_04_hilo_principal_sin_bloqueo():
    # Modo Tkinter: no crea hilos, solo programa widget.after y regresa de inmediato
    widget = MagicMock()
    timer = InactivityTimer(30, lambda: None, widget=widget)
    t0 = time.perf_counter()
    timer.iniciar()
    assert time.perf_counter() - t0 < 0.5
    assert timer._timer_thread is None
    widget.after.assert_called_once_with(1000, timer._tick)
    timer.detener()
    widget.after_cancel.assert_called_once()

    # Modo hilo: iniciar() regresa de inmediato y el hilo es daemon
    timer2 = InactivityTimer(30, lambda: None)
    t0 = time.perf_counter()
    timer2.iniciar()
    try:
        assert time.perf_counter() - t0 < 0.5
        assert timer2._timer_thread.is_alive() and timer2._timer_thread.daemon is True
    finally:
        timer2.detener()
