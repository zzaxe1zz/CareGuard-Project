from typing import Optional, List, Dict, Any
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from models.dto import SessionDTO
from utils.security import generar_salt, hash_password, sanitizar_texto


class AdminController:
    def __init__(self, session: SessionDTO, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        if session.rol.upper() != 'ADMIN':
            raise PermissionError(
                "Acceso denegado: Privilegios de Administrador requeridos.")

        self.session = session
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def registrar_usuario(self, nombre_raw: str, usuario_raw: str, password_raw: str, rol_raw: str) -> int:
        """Crea una nueva cuenta aplicando hashing PBKDF2 y validando datos (RF-12)."""
        nombre = sanitizar_texto(nombre_raw)
        usuario = sanitizar_texto(usuario_raw)
        rol = sanitizar_texto(rol_raw).upper()

        if rol not in ['MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN']:
            raise ValueError("Rol especificado no válido.")

        if len(password_raw) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")

        salt = generar_salt()
        pwd_hash = hash_password(password_raw, salt)

        query = """
            INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol, estado)
            VALUES (?, ?, ?, ?, ?, 'ACTIVO')
        """
        try:
            id_nuevo = self.db.ejecutar(
                query, (nombre, usuario, pwd_hash, salt, rol))
            self.audit.registrar_evento(
                self.session.id_usuario, self.session.rol, "ALTA_USUARIO", True,
                f"Nuevo usuario ID {id_nuevo} ({usuario}) con rol {rol}"
            )
            return id_nuevo
        except Exception as e:
            self.audit.registrar_evento(
                self.session.id_usuario, self.session.rol, "ALTA_USUARIO", False, str(e))
            raise ValueError(
                "El nombre de usuario ya existe o hubo un problema de BD.")

    def obtener_metricas_dashboard(self) -> Dict[str, Any]:
        """Calcula agregados y promedios anonimizados para el Dashboard gráfico (RF-11)."""
        query_extra = """
            SELECT u.rol, SUM(j.horas_extra) as total_horas_extra
            FROM jornadas j
            JOIN usuarios u ON j.id_usuario = u.id_usuario
            WHERE j.fecha >= date('now', '-30 days')
            GROUP BY u.rol
        """
        extra_por_rol = [dict(f) for f in self.db.obtener_todos(query_extra)]

        query_satisfaccion = "SELECT AVG(calificacion) as promedio_estrellas, COUNT(*) as total_evaluaciones FROM evaluaciones_pacientes"
        res_sat = self.db.obtener_uno(query_satisfaccion)

        query_comentarios = """
            SELECT calificacion, comentario, fecha_registro
            FROM evaluaciones_pacientes
            ORDER BY fecha_registro DESC
            LIMIT 10
        """
        comentarios_recientes = [
            dict(f) for f in self.db.obtener_todos(query_comentarios)]

        self.audit.registrar_evento(
            self.session.id_usuario, self.session.rol, "CONSULTA_DASHBOARD_METRICAS", True)

        return {
            "horas_extra_agregadas": extra_por_rol,
            "promedio_satisfaccion": round(res_sat["promedio_estrellas"] or 0.0, 2),
            "total_evaluaciones": res_sat["total_evaluaciones"],
            "comentarios_recientes": comentarios_recientes
        }
