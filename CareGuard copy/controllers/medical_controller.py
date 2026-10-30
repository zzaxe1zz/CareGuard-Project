from typing import Optional, List, Dict, Any
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from services.workday_manager import WorkdayManager
from services.burnout_engine import BurnoutEngine
from models.dto import SessionDTO
from utils.security import sanitizar_texto


class MedicalController:
    def __init__(self, session: SessionDTO, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        if session.rol.upper() not in ['MEDICO', 'ENFERMERO']:
            raise PermissionError("Acceso no autorizado al módulo médico.")

        self.session = session
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()
        self.workday_manager = WorkdayManager(self.db, self.audit)
        self.burnout_engine = BurnoutEngine(self.db, self.audit)

    def iniciar_jornada(self) -> int:
        """Registra el inicio de turno laboral."""
        return self.workday_manager.registrar_entrada(self.session.id_usuario)

    def registrar_descanso(self, id_jornada: int, hora_inicio: str, hora_fin: str) -> bool:
        """Registra un periodo de descanso durante el turno (RF-01)."""
        return self.workday_manager.registrar_descanso(id_jornada, self.session.id_usuario, hora_inicio, hora_fin)

    def finalizar_jornada_y_evaluar(
        self, id_jornada: int, nivel_estres: int, estado_animo: str, notas: str = ""
    ) -> Dict[str, Any]:
        """
        Cierra la jornada, registra la evaluación emocional (RF-02) y ejecuta
        la evaluación determinista de sobrecarga (RF-13, RF-14).
        """
        if not (1 <= nivel_estres <= 10):
            raise ValueError("El nivel de estrés debe estar entre 1 y 10.")

        res_jornada = self.workday_manager.registrar_salida(
            id_jornada, self.session.id_usuario)

        # Registro confidencial de estado emocional
        animo_limpio = sanitizar_texto(estado_animo)
        notas_limpias = sanitizar_texto(notas)

        query_emo = """
            INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo, notas)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.ejecutar(query_emo, (self.session.id_usuario,
                         id_jornada, nivel_estres, animo_limpio, notas_limpias))
        self.audit.registrar_evento(self.session.id_usuario, self.session.rol,
                                    "EVALUACION_EMOCIONAL", True, f"Estrés: {nivel_estres}")

        # Evaluación en el motor determinista
        id_alerta = self.burnout_engine.evaluar_sobrecarga(
            self.session.id_usuario)

        return {
            "resumen_jornada": res_jornada,
            "alerta_generada": id_alerta is not None,
            "id_alerta": id_alerta
        }

    def solicitar_apoyo_psicologico(self, notas: str = "") -> int:
        """Envía una solicitud voluntaria confidencial al área de Psicología (RF-04)."""
        return self.burnout_engine.solicitar_apoyo_voluntario(self.session.id_usuario, sanitizar_texto(notas))

    def consultar_historial_propio(self) -> List[Dict[str, Any]]:
        """Aislamiento estricto: consulta únicamente el historial del usuario autenticado (RF-03)."""
        return self.workday_manager.obtener_historial_semanal(self.session.id_usuario)
