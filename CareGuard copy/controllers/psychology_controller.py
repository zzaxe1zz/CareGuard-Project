from typing import Optional, List, Dict, Any
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from models.dto import SessionDTO, AlertaDTO, ExpedienteDTO
from utils.security import sanitizar_texto


class PsychologyController:
    def __init__(self, session: SessionDTO, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        if session.rol.upper() != 'PSICOLOGO':
            raise PermissionError(
                "Acceso denegado: Se requieren privilegios de Psicología.")

        self.session = session
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def consultar_bandeja_alertas(self) -> List[AlertaDTO]:
        """Obtiene la lista de alertas inmutables generadas por el sistema o por médicos (RF-05)."""
        query = """
            SELECT a.id_alerta, a.id_usuario, u.nombre as nombre_profesional, 
                   a.fecha_generacion, a.tipo, a.estado, a.motivo
            FROM alertas a
            JOIN usuarios u ON a.id_usuario = u.id_usuario
            ORDER BY a.fecha_generacion DESC
        """
        filas = self.db.obtener_todos(query)
        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "CONSULTA_BANDEJA_ALERTAS", True)

        return [
            AlertaDTO(
                id_alerta=f["id_alerta"],
                id_usuario=f["id_usuario"],
                nombre_profesional=f["nombre_profesional"],
                fecha_generacion=f["fecha_generacion"],
                tipo=f["tipo"],
                estado=f["estado"],
                motivo=f["motivo"]
            )
            for f in filas
        ]

    def actualizar_estado_alerta(self, id_alerta: int, nuevo_estado: str, nota_seguimiento: str) -> bool:
        """Actualiza el estado de la alerta e ingresa notas en la bitácora de seguimiento (RF-06)."""
        estado_upper = nuevo_estado.upper()
        if estado_upper not in ['PENDIENTE', 'EN_ATENCION', 'CERRADA']:
            raise ValueError("Estado de alerta no válido.")

        nota_limpia = sanitizar_texto(nota_seguimiento)

        query_update = "UPDATE alertas SET estado = ? WHERE id_alerta = ?"
        self.db.ejecutar(query_update, (estado_upper, id_alerta))

        if nota_limpia:
            query_nota = """
                INSERT INTO bitacora_psicologia (id_alerta, id_psicologo, observacion)
                VALUES (?, ?, ?)
            """
            self.db.ejecutar(
                query_nota, (id_alerta, self.session.id_usuario, nota_limpia))

        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "ACTUALIZAR_ALERTA", True,
            f"Alerta ID {id_alerta} -> {estado_upper}"
        )
        return True

    def consultar_expediente_confidencial(self, id_medico: int) -> Dict[str, Any]:
        """Apertura protegida del expediente emocional e historial de jornadas de un médico (RF-07)."""
        query_usuario = "SELECT id_usuario, nombre FROM usuarios WHERE id_usuario = ?"
        medico = self.db.obtener_uno(query_usuario, (id_medico,))
        if not medico:
            raise ValueError("Médico no encontrado.")

        query_emocional = """
            SELECT fecha_registro, nivel_estres, estado_animo, notas
            FROM estados_emocionales
            WHERE id_usuario = ?
            ORDER BY fecha_registro DESC
        """
        registros_emocionales = [
            dict(f) for f in self.db.obtener_todos(query_emocional, (id_medico,))]

        query_jornadas = """
            SELECT fecha, horas_trabajadas, horas_extra
            FROM jornadas
            WHERE id_usuario = ?
            ORDER BY fecha DESC
        """
        registros_jornadas = [dict(f) for f in self.db.obtener_todos(
            query_jornadas, (id_medico,))]

        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "CONSULTA_EXPEDIENTE_CONFIDENCIAL", True,
            f"Expediente visto para Médico ID {id_medico}"
        )

        return {
            "medico": dict(medico),
            "historial_emocional": registros_emocionales,
            "historial_jornadas": registros_jornadas
        }
