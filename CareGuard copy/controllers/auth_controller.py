from typing import Optional
from database.db_adapter import DatabaseAdapter
from database.audit_logger import AuditLogger
from models.dto import SessionDTO
from utils.security import verificar_password, sanitizar_texto


class AuthController:
    def __init__(self, db: Optional[DatabaseAdapter] = None, audit: Optional[AuditLogger] = None):
        self.db = db or DatabaseAdapter()
        self.audit = audit or AuditLogger()

    def login(self, usuario_raw: str, password_raw: str) -> Optional[SessionDTO]:
        """Inicia sesión detectando automáticamente el rol del usuario desde la BD."""
        usuario = sanitizar_texto(usuario_raw)

        query = """
            SELECT id_usuario, nombre, usuario, hash_password, salt, rol, estado
            FROM usuarios
            WHERE usuario = ? AND estado = 'ACTIVO'
        """
        usuario_db = self.db.obtener_uno(query, (usuario,))

        if not usuario_db:
            self.audit.registrar_evento(
                None, "DESCONOCIDO", "LOGIN", False, f"Usuario no encontrado: {usuario}")
            return None

        if not verificar_password(password_raw, usuario_db["hash_password"], usuario_db["salt"]):
            self.audit.registrar_evento(
                usuario_db["id_usuario"], usuario_db["rol"], "LOGIN", False, "Contraseña incorrecta")
            return None

        rol_detectado = usuario_db["rol"].upper()
        self.audit.registrar_evento(
            usuario_db["id_usuario"], rol_detectado, "LOGIN", True, "Autenticación exitosa")

        return SessionDTO(
            id_usuario=usuario_db["id_usuario"],
            nombre=usuario_db["nombre"],
            usuario=usuario_db["usuario"],
            rol=rol_detectado
        )
