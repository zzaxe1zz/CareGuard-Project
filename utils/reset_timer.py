import threading
import time
from typing import Callable, Optional


class InactivityTimer:
    """Temporizador de inactividad.

    Si se le pasa `widget`, usa el bucle de eventos de Tkinter (`widget.after`),
    que es la forma correcta: Tkinter NO es seguro entre hilos y el callback del
    hilo anterior tocaba widgets desde un hilo secundario. Sin `widget` conserva
    el comportamiento original con hilo daemon.
    """

    def __init__(self, timeout_seconds: int = 30,
                 on_timeout_callback: Optional[Callable] = None, widget=None):
        self.timeout_seconds = timeout_seconds
        self.on_timeout_callback = on_timeout_callback
        self.widget = widget
        self._timer_thread: Optional[threading.Thread] = None
        self._after_id = None
        self._running = False
        self._last_activity_time = time.time()

    def iniciar(self) -> None:
        self._running = True
        self._last_activity_time = time.time()
        if self.widget is not None:
            self._programar()
        else:
            self._timer_thread = threading.Thread(
                target=self._run, daemon=True)
            self._timer_thread.start()

    def registrar_actividad(self) -> None:
        self._last_activity_time = time.time()

    def detener(self) -> None:
        self._running = False
        if self.widget is not None and self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _programar(self) -> None:
        try:
            self._after_id = self.widget.after(1000, self._tick)
        except Exception:
            self._running = False

    def _tick(self) -> None:
        if not self._running:
            return
        if time.time() - self._last_activity_time >= self.timeout_seconds:
            self._last_activity_time = time.time()
            if self.on_timeout_callback:
                self.on_timeout_callback()
        self._programar()

    def _run(self) -> None:
        while self._running:
            time.sleep(1)
            if time.time() - self._last_activity_time >= self.timeout_seconds:
                if self.on_timeout_callback:
                    self.on_timeout_callback()
                self._last_activity_time = time.time()
