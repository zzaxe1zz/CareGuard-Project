from typing import Optional
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from utils.security import sanitizar_texto


class KioskController:
    def __init__(self, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def registrar_evaluacion_anonima(self, calificacion: int, comentario_raw: str = "") -> int:
        """Registra retroalimentación pública de pacientes sin almacenar claves foráneas (RF-09)."""
        if not (1 <= calificacion <= 5):
            raise ValueError(
                "La calificación debe estar entre 1 y 5 estrellas.")

        comentario = sanitizar_texto(comentario_raw)

        query = """
            INSERT INTO evaluaciones_pacientes (calificacion, comentario)
            VALUES (?, ?)
        """
        id_eval = self.db.ejecutar(query, (calificacion, comentario))
        self.audit.registrar_evento(
            None, "PACIENTE", "EVALUACION_KIOSCO", True, f"Calificación: {calificacion} estrellas")
        return id_eval
