from datetime import datetime
from typing import List, Optional
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from utils.security import sanitizar_texto


class KioskController:
    def __init__(self, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def listar_personal(self) -> List[str]:
        filas = self.db.obtener_todos(
            """SELECT nombre FROM usuarios
               WHERE rol IN ('MEDICO', 'ENFERMERO') AND estado = 'ACTIVO'
               ORDER BY nombre""")
        return [f["nombre"] for f in filas]

    def registrar_evaluacion_anonima(self, calificacion: int, comentario_raw: str = "",
                                     personal_medico: str = "") -> int:
        if not (1 <= calificacion <= 5):
            raise ValueError(
                "La calificación debe estar entre 1 y 5 estrellas.")

        comentario = sanitizar_texto(comentario_raw)
        personal = sanitizar_texto(personal_medico) or None

        query = """
            INSERT INTO evaluaciones_pacientes (calificacion, comentario, fecha_registro, personal_medico)
            VALUES (?, ?, ?, ?)
        """
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_eval = self.db.ejecutar(query, (calificacion, comentario, ahora, personal))
        self.audit.registrar_evento(
            None, "PACIENTE", "EVALUACION_KIOSCO", True, f"Calificación: {calificacion} estrellas")
        return id_eval
