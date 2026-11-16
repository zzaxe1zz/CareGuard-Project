from datetime import datetime
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

    def obtener_jornada_abierta(self) -> Optional[Dict[str, Any]]:
        fila = self.db.obtener_uno(
            """SELECT id_jornada, hora_entrada FROM jornadas
               WHERE id_usuario = ? AND hora_salida IS NULL
               ORDER BY id_jornada DESC LIMIT 1""",
            (self.session.id_usuario,))
        return dict(fila) if fila else None

    HORAS_MAX_TURNO_ABIERTO = 16

    def cerrar_jornada_olvidada(self) -> Optional[str]:
        """Si quedó un turno abierto de hace más de 16 h (se olvidó registrar la salida),
        lo cierra SIN horas registradas para no generar horas extra ni alertas falsas.
        Devuelve la hora de entrada de ese turno, o None si no había nada que cerrar."""
        abierta = self.obtener_jornada_abierta()
        if not abierta:
            return None
        try:
            entrada = datetime.strptime(abierta["hora_entrada"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        if (datetime.now() - entrada).total_seconds() <= self.HORAS_MAX_TURNO_ABIERTO * 3600:
            return None
        self.db.ejecutar(
            """UPDATE jornadas SET hora_salida = hora_entrada, horas_trabajadas = 0.0,
               horas_extra = 0.0 WHERE id_jornada = ?""", (abierta["id_jornada"],))
        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "CIERRE_JORNADA_OLVIDADA", True,
            f"Jornada ID {abierta['id_jornada']} (entrada {abierta['hora_entrada']}) cerrada sin horas")
        return abierta["hora_entrada"]

    def iniciar_jornada(self) -> int:
        if self.obtener_jornada_abierta():
            raise ValueError("Ya tiene una jornada activa sin cerrar.")
        return self.workday_manager.registrar_entrada(self.session.id_usuario)

    def registrar_descanso(self, id_jornada: int, hora_inicio: str, hora_fin: str) -> bool:
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

        animo_limpio = sanitizar_texto(estado_animo)
        notas_limpias = sanitizar_texto(notas)

        query_emo = """
            INSERT INTO estados_emocionales (id_usuario, id_jornada, fecha_registro, nivel_estres, estado_animo, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        # Hora local explícita (CURRENT_TIMESTAMP de SQLite sería UTC)
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.ejecutar(query_emo, (self.session.id_usuario, id_jornada, ahora,
                         nivel_estres, animo_limpio, notas_limpias))
        self.audit.registrar_evento(self.session.id_usuario, self.session.rol,
                                    "EVALUACION_EMOCIONAL", True, f"Estrés: {nivel_estres}")

        id_alerta = self.burnout_engine.evaluar_sobrecarga(
            self.session.id_usuario)

        return {
            "resumen_jornada": res_jornada,
            "alerta_generada": id_alerta is not None,
            "id_alerta": id_alerta
        }

    def solicitar_apoyo_psicologico(self, notas: str = "") -> int:
        return self.burnout_engine.solicitar_apoyo_voluntario(self.session.id_usuario, sanitizar_texto(notas))

    def consultar_historial_propio(self) -> List[Dict[str, Any]]:
        """Aislamiento estricto: consulta únicamente el historial del usuario autenticado (RF-03)."""
        return self.workday_manager.obtener_historial_semanal(self.session.id_usuario)

    def consultar_resumen_semanal(self) -> Dict[str, Any]:
        uid = self.session.id_usuario
        filas = self.db.obtener_todos(
            """SELECT j.id_jornada, j.fecha, j.hora_entrada, j.hora_salida,
                      j.horas_trabajadas, j.horas_extra,
                      e.estado_animo, e.nivel_estres
               FROM jornadas j
               LEFT JOIN estados_emocionales e ON e.id_jornada = j.id_jornada
               WHERE j.id_usuario = ? AND j.fecha >= date('now', '-7 days')
               ORDER BY j.fecha DESC, j.id_jornada DESC""", (uid,))
        registros = [dict(f) for f in filas]

        horas = sum(r["horas_trabajadas"] or 0.0 for r in registros)
        estres = [r["nivel_estres"] for r in registros if r["nivel_estres"] is not None]
        promedio = sum(estres) / len(estres) if estres else None

        res = self.db.obtener_uno(
            """SELECT COUNT(*) AS n FROM descansos d
               JOIN jornadas j ON d.id_jornada = j.id_jornada
               WHERE j.id_usuario = ? AND j.fecha >= date('now', '-7 days')""", (uid,))
        return {
            "horas_semana": round(horas, 1),
            "promedio_estres": round(promedio, 1) if promedio is not None else None,
            "pausas": res["n"] if res else 0,
            "filas": registros,
        }

    def obtener_notificaciones_pendientes(self) -> List[Dict[str, Any]]:
        filas = self.db.obtener_todos(
            "SELECT id_notificacion, mensaje FROM notificaciones WHERE id_usuario = ? AND leido = 0",
            (self.session.id_usuario,))
        return [dict(f) for f in filas]

    def marcar_notificacion_leida(self, id_notificacion: int) -> None:
        self.db.ejecutar(
            "UPDATE notificaciones SET leido = 1 WHERE id_notificacion = ? AND id_usuario = ?",
            (id_notificacion, self.session.id_usuario))
