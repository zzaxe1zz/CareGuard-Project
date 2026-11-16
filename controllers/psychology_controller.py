from datetime import datetime
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
        estado_upper = nuevo_estado.upper()
        if estado_upper not in ['PENDIENTE', 'EN_ATENCION', 'CERRADA']:
            raise ValueError("Estado de alerta no válido.")

        nota_limpia = sanitizar_texto(nota_seguimiento)

        query_update = "UPDATE alertas SET estado = ? WHERE id_alerta = ?"
        self.db.ejecutar(query_update, (estado_upper, id_alerta))

        if nota_limpia:
            query_nota = """
                INSERT INTO bitacora_psicologia (id_alerta, id_psicologo, fecha_registro, observacion)
                VALUES (?, ?, ?, ?)
            """
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.ejecutar(
                query_nota, (id_alerta, self.session.id_usuario, ahora, nota_limpia))

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

    def consultar_notas(self, id_alerta: int) -> List[Dict[str, Any]]:
        filas = self.db.obtener_todos(
            """SELECT b.fecha_registro, b.observacion, u.nombre AS psicologo
               FROM bitacora_psicologia b
               JOIN usuarios u ON u.id_usuario = b.id_psicologo
               WHERE b.id_alerta = ?
               ORDER BY b.fecha_registro DESC, b.id_nota DESC""", (id_alerta,))
        return [dict(f) for f in filas]

    def agendar_cita(self, id_medico: int, fecha_hora: str, notas: str = "",
                     id_alerta: Optional[int] = None) -> int:
        """Programa una cita de cuidado y notifica al profesional (RF-08).
        Si se indica id_alerta y está PENDIENTE, pasa a EN_ATENCION solo cuando la cita
        quedó agendada (una alerta sin fecha de cita confirmada sigue pendiente)."""
        try:
            fecha_dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Fecha u hora de la cita inválida.")
        if fecha_dt < datetime.now():
            raise ValueError("La cita debe programarse en una fecha y hora futuras.")

        notas_limpias = sanitizar_texto(notas)
        id_cita = self.db.ejecutar(
            """INSERT INTO citas (id_usuario, id_psicologo, fecha_hora, estado, notas)
               VALUES (?, ?, ?, 'PROGRAMADA', ?)""",
            (id_medico, self.session.id_usuario, fecha_hora, notas_limpias))
        mensaje = f"Se le ha agendado una cita de acompañamiento para el día {fecha_hora}."
        if notas_limpias:
            mensaje += f" Nota: {notas_limpias}"
        self.db.ejecutar(
            "INSERT INTO notificaciones (id_usuario, mensaje) VALUES (?, ?)",
            (id_medico, mensaje))
        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "AGENDAR_CITA", True,
            f"Cita ID {id_cita} para profesional ID {id_medico} el {fecha_hora}")
        if id_alerta is not None:
            fila = self.db.obtener_uno(
                "SELECT estado FROM alertas WHERE id_alerta = ? AND id_usuario = ?",
                (id_alerta, id_medico))
            if fila and fila["estado"] == "PENDIENTE":
                self.actualizar_estado_alerta(id_alerta, "EN_ATENCION", "")
        return id_cita

    def listar_pacientes(self) -> List[Dict[str, Any]]:
        filas = self.db.obtener_todos(
            """SELECT u.id_usuario, u.nombre, u.rol,
                      (SELECT COUNT(*) FROM alertas a WHERE a.id_usuario = u.id_usuario) AS total_alertas,
                      (SELECT COUNT(*) FROM alertas a WHERE a.id_usuario = u.id_usuario
                         AND a.estado != 'CERRADA') AS alertas_abiertas,
                      (SELECT MIN(c.fecha_hora) FROM citas c WHERE c.id_usuario = u.id_usuario
                         AND c.estado = 'PROGRAMADA' AND c.fecha_hora >= ?) AS proxima_cita
               FROM usuarios u
               WHERE u.rol IN ('MEDICO', 'ENFERMERO') AND u.estado = 'ACTIVO'
               ORDER BY u.nombre""",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        return [dict(f) for f in filas]

    def consultar_historial_paciente(self, id_usuario: int) -> Dict[str, Any]:
        datos = self.consultar_expediente_confidencial(id_usuario)
        rol = self.db.obtener_uno("SELECT rol FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        datos["medico"]["rol"] = rol["rol"] if rol else ""
        datos["alertas"] = [dict(f) for f in self.db.obtener_todos(
            """SELECT id_alerta, fecha_generacion, tipo, estado, motivo FROM alertas
               WHERE id_usuario = ? ORDER BY fecha_generacion DESC""", (id_usuario,))]
        datos["citas"] = [dict(f) for f in self.db.obtener_todos(
            """SELECT c.fecha_hora, c.estado, c.notas, u.nombre AS psicologo
               FROM citas c JOIN usuarios u ON u.id_usuario = c.id_psicologo
               WHERE c.id_usuario = ? ORDER BY c.fecha_hora DESC""", (id_usuario,))]
        datos["notas"] = [dict(f) for f in self.db.obtener_todos(
            """SELECT b.id_alerta, b.fecha_registro, b.observacion, u.nombre AS psicologo
               FROM bitacora_psicologia b
               JOIN alertas a ON a.id_alerta = b.id_alerta
               JOIN usuarios u ON u.id_usuario = b.id_psicologo
               WHERE a.id_usuario = ? ORDER BY b.fecha_registro DESC, b.id_nota DESC""",
            (id_usuario,))]
        return datos
