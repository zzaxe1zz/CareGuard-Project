from datetime import datetime
from typing import Optional, Dict, Any, List
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from utils.security import sanitizar_texto


class WorkdayManager:
    HORAS_TURNO_ESTANDAR = 8.0

    def __init__(self, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def registrar_entrada(self, id_usuario: int) -> int:
        """Registra el inicio de turno para un profesional médico o enfermero."""
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        hora_entrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
            INSERT INTO jornadas (id_usuario, fecha, hora_entrada)
            VALUES (?, ?, ?)
        """
        id_jornada = self.db.ejecutar(
            query, (id_usuario, fecha_actual, hora_entrada))
        self.audit.registrar_evento(
            id_usuario, "MEDICO", "CHECK_IN", True, f"Jornada ID {id_jornada} iniciada")
        return id_jornada

    def registrar_salida(self, id_jornada: int, id_usuario: int) -> Dict[str, Any]:
        """Calcula horas trabajadas, determina horas extra y cierra la jornada laboral."""
        jornada = self.db.obtener_uno(
            "SELECT hora_entrada FROM jornadas WHERE id_jornada = ?", (id_jornada,))
        if not jornada:
            raise ValueError("Jornada no encontrada.")

        hora_salida_dt = datetime.now()
        hora_entrada_dt = datetime.strptime(
            jornada["hora_entrada"], "%Y-%m-%d %H:%M:%S")

        duracion_total = (
            hora_salida_dt - hora_entrada_dt).total_seconds() / 3600.0
        horas_trabajadas = round(duracion_total, 2)
        horas_extra = round(
            max(0.0, horas_trabajadas - self.HORAS_TURNO_ESTANDAR), 2)

        hora_salida_str = hora_salida_dt.strftime("%Y-%m-%d %H:%M:%S")
        query = """
            UPDATE jornadas 
            SET hora_salida = ?, horas_trabajadas = ?, horas_extra = ?
            WHERE id_jornada = ?
        """
        self.db.ejecutar(
            query, (hora_salida_str, horas_trabajadas, horas_extra, id_jornada))

        self.audit.registrar_evento(
            id_usuario, "MEDICO", "CHECK_OUT", True,
            f"Jornada ID {id_jornada} cerrada. Horas trab: {horas_trabajadas}, Horas extra: {horas_extra}"
        )

        return {
            "id_jornada": id_jornada,
            "horas_trabajadas": horas_trabajadas,
            "horas_extra": horas_extra
        }

    def registrar_descanso(self, id_jornada: int, id_usuario: int, hora_inicio_str: str, hora_fin_str: str) -> bool:
        """
        Valida y almacena un periodo de descanso tomado durante la jornada (RF-01).
        MT-01: Lanza ValueError ante incoherencias de horario (inicio >= fin).
        """
        try:
            inicio_dt = datetime.strptime(hora_inicio_str, "%Y-%m-%d %H:%M:%S")
            fin_dt = datetime.strptime(hora_fin_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(
                "Formato de fecha u hora inválido. Utilice 'YYYY-MM-DD HH:MM:SS'.")

        if inicio_dt >= fin_dt:
            self.audit.registrar_evento(id_usuario, "MEDICO", "REGISTRO_DESCANSO",
                                        False, "Horario incoherente: fin anterior o igual a inicio")
            raise ValueError(
                "La hora de inicio debe ser estrictamente anterior a la hora de finalización.")

        duracion_minutos = int((fin_dt - inicio_dt).total_seconds() / 60)

        query = """
            INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos)
            VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar(query, (id_jornada, hora_inicio_str,
                         hora_fin_str, duracion_minutos))
        self.audit.registrar_evento(id_usuario, "MEDICO", "REGISTRO_DESCANSO", True,
                                    f"Descanso de {duracion_minutos} min registrado en jornada {id_jornada}")
        return True

    def obtener_historial_semanal(self, id_usuario: int) -> List[Dict[str, Any]]:
        """Obtiene las jornadas del usuario de los últimos 7 días."""
        query = """
            SELECT id_jornada, fecha, hora_entrada, hora_salida, horas_trabajadas, horas_extra
            FROM jornadas
            WHERE id_usuario = ? AND fecha >= date('now', '-7 days')
            ORDER BY fecha DESC
        """
        filas = self.db.obtener_todos(query, (id_usuario,))
        return [dict(f) for f in filas]
