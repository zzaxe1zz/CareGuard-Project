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
        nombre = sanitizar_texto(nombre_raw)
        usuario = sanitizar_texto(usuario_raw)
        rol = sanitizar_texto(rol_raw).upper()

        if not nombre or not usuario:
            raise ValueError("El nombre completo y el username son obligatorios.")

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

        total_jornadas = self.db.obtener_uno(
            "SELECT COUNT(*) AS n FROM jornadas")["n"]
        alertas_por_estado = {r["estado"]: r["n"] for r in self.db.obtener_todos(
            "SELECT estado, COUNT(*) AS n FROM alertas GROUP BY estado")}
        # Promedio institucional (anonimizado) de estrés: últimos 7 días con registros
        tendencia = self.db.obtener_todos(
            """SELECT date(fecha_registro) AS dia, AVG(nivel_estres) AS prom
               FROM estados_emocionales
               GROUP BY dia ORDER BY dia DESC LIMIT 7""")
        tendencia_estres = [(r["dia"], round(r["prom"], 1))
                            for r in reversed(tendencia)]

        return {
            "horas_extra_agregadas": extra_por_rol,
            "promedio_satisfaccion": round(res_sat["promedio_estrellas"] or 0.0, 2),
            "total_evaluaciones": res_sat["total_evaluaciones"],
            "comentarios_recientes": comentarios_recientes,
            "total_horas_extra": round(sum(r["total_horas_extra"] or 0.0 for r in extra_por_rol), 1),
            "total_jornadas": total_jornadas,
            "alertas_por_estado": alertas_por_estado,
            "tendencia_estres": tendencia_estres,
        }

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        filas = self.db.obtener_todos(
            "SELECT id_usuario, nombre, usuario, rol, estado FROM usuarios ORDER BY rol, usuario")
        return [dict(f) for f in filas]

    def listar_evaluaciones(self, limite: int = 50) -> Dict[str, Any]:
        filas = self.db.obtener_todos(
            """SELECT calificacion, comentario, fecha_registro
               FROM evaluaciones_pacientes
               ORDER BY fecha_registro DESC, id_evaluacion DESC LIMIT ?""", (limite,))
        prom = self.db.obtener_uno(
            "SELECT AVG(calificacion) AS p, COUNT(*) AS n FROM evaluaciones_pacientes")
        return {
            "evaluaciones": [dict(f) for f in filas],
            "promedio": round(prom["p"] or 0.0, 1),
            "total": prom["n"],
        }
