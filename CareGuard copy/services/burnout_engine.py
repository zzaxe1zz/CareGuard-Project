from datetime import datetime
from typing import Optional, List, Dict, Any
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger


class BurnoutEngine:
    UMBRAL_HORAS_EXTRA_SEMANAL = 12.0
    UMBRAL_ESTRES_ALTO = 7
    DIAS_ESTRES_CONSECUTIVOS = 3

    def __init__(self, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def evaluar_sobrecarga(self, id_usuario: int) -> Optional[int]:
        """
        Evalúa el historial de los últimos 7 días para detectar patrones de burnout (RF-13, RF-14).
        MT-04: Ejecuta la evaluación determinista.
        """
        motivos: List[str] = []

        # Regla 1: Suma de horas extra en los últimos 7 días > 12.0 horas
        query_horas = """
            SELECT SUM(horas_extra) as total_extra
            FROM jornadas
            WHERE id_usuario = ? AND fecha >= date('now', '-7 days')
        """
        res_horas = self.db.obtener_uno(query_horas, (id_usuario,))
        total_extra = res_horas["total_extra"] if res_horas and res_horas["total_extra"] else 0.0

        if total_extra > self.UMBRAL_HORAS_EXTRA_SEMANAL:
            motivos.append(
                f"Sobrecarga horaria: {total_extra:.1f}h extra acumuladas en 7 días (Límite: {self.UMBRAL_HORAS_EXTRA_SEMANAL}h).")

        # Regla 2: Registros de nivel de estrés >= 7 en los últimos 3 turnos
        query_estres = """
            SELECT nivel_estres
            FROM estados_emocionales
            WHERE id_usuario = ?
            ORDER BY fecha_registro DESC
            LIMIT ?
        """
        filas_estres = self.db.obtener_todos(
            query_estres, (id_usuario, self.DIAS_ESTRES_CONSECUTIVOS))
        niveles = [f["nivel_estres"] for f in filas_estres]

        if len(niveles) >= self.DIAS_ESTRES_CONSECUTIVOS and all(n >= self.UMBRAL_ESTRES_ALTO for n in niveles):
            motivos.append(
                f"Estrés crónico sostenido: Nivel >= {self.UMBRAL_ESTRES_ALTO} registrado en los últimos {self.DIAS_ESTRES_CONSECUTIVOS} turnos.")

        if motivos:
            motivo_completo = " | ".join(motivos)
            id_alerta = self._generar_alerta_inmutable(
                id_usuario, "ALGORITMO", motivo_completo)
            return id_alerta

        return None

    def solicitar_apoyo_voluntario(self, id_usuario: int, notas: str = "") -> int:
        """Procesa solicitudes directas y confidenciales del médico hacia Psicología (RF-04)."""
        motivo = "Solicitud directa de acompañamiento psicológico emitida por el usuario."
        if notas:
            motivo += f" Nota: {notas}"

        return self._generar_alerta_inmutable(id_usuario, "VOLUNTARIO", motivo)

    def _generar_alerta_inmutable(self, id_usuario: int, tipo: str, motivo: str) -> int:
        """Inserta de forma inmutable una alerta en estado PENDIENTE (RF-14)."""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            INSERT INTO alertas (id_usuario, fecha_generacion, tipo, estado, motivo)
            VALUES (?, ?, ?, 'PENDIENTE', ?)
        """
        id_alerta = self.db.ejecutar(
            query, (id_usuario, fecha_actual, tipo, motivo))
        self.audit.registrar_evento(
            id_usuario, "SISTEMA" if tipo == "ALGORITMO" else "MEDICO",
            "GENERAR_ALERTA", True,
            f"Alerta ID {id_alerta} ({tipo}) registrada: {motivo}"
        )
        return id_alerta
