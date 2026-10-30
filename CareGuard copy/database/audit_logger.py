import logging
from datetime import datetime
from typing import Optional


class AuditLogger:
    def __init__(self, log_file: str = "auditoria.log"):
        self.logger = logging.getLogger("CareGuardAudit")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter(
                '[%(asctime)s] - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def registrar_evento(self, id_usuario: Optional[int], rol: str, accion: str, exito: bool, detalles: str = ""):
        """Registra un evento de seguridad de forma inmutable."""
        estado = "EXITO" if exito else "DENEGADO/FALLO"
        mensaje = f"Usuario_ID: {id_usuario if id_usuario else 'ANONIMO'} | Rol: {rol} | Accion: {accion} | Estado: {estado} | Detalles: {detalles}"

        if exito:
            self.logger.info(mensaje)
        else:
            self.logger.warning(mensaje)
