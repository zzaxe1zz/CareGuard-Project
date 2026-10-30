import threading
import time
from typing import Callable, Optional


class InactivityTimer:
    def __init__(self, timeout_seconds: int = 30, on_timeout_callback: Optional[Callable] = None):
        self.timeout_seconds = timeout_seconds
        self.on_timeout_callback = on_timeout_callback
        self._timer_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_activity_time = time.time()

    def iniciar(self) -> None:
        """Inicia el hilo del temporizador en segundo plano (daemon)."""
        self._running = True
        self._last_activity_time = time.time()
        self._timer_thread = threading.Thread(target=self._run, daemon=True)
        self._timer_thread.start()

    def registrar_actividad(self) -> None:
        """Reinicia el contador al detectar interacción del usuario."""
        self._last_activity_time = time.time()

    def detener(self) -> None:
        """Detiene la ejecución del hilo."""
        self._running = False

    def _run(self) -> None:
        """Bucle de comprobación de tiempo transcurrido."""
        while self._running:
            time.sleep(1)
            tiempo_transcurrido = time.time() - self._last_activity_time
            if tiempo_transcurrido >= self.timeout_seconds:
                if self.on_timeout_callback:
                    self.on_timeout_callback()
                self._last_activity_time = time.time()  # Reinicia tras ejecutar la acción
