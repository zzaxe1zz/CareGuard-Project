"""ST-05: Control de Acceso Estricto y Aislamiento de Vistas (RBAC) + auditoría."""
import pytest

from controllers.admin_controller import AdminController
from controllers.medical_controller import MedicalController
from controllers.psychology_controller import PsychologyController

pytestmark = pytest.mark.system

# rol -> controladores (módulos) que le deben estar vedados
MATRIZ = {
    "MEDICO": [PsychologyController, AdminController],
    "ENFERMERO": [PsychologyController, AdminController],
    "ADMIN": [MedicalController, PsychologyController],
    "PACIENTE": [MedicalController, PsychologyController, AdminController],  # Paciente/Kiosco
}


def _denegar(rol, db, audit, sesion):
    for controlador in MATRIZ[rol]:
        with pytest.raises(PermissionError):
            controlador(sesion(7, rol, "intruso"), db, audit)


def test_st_05_01_acceso_denegado_medico(db_adapter, mock_logger, sesion):
    _denegar("MEDICO", db_adapter, mock_logger, sesion)


def test_st_05_02_acceso_denegado_enfermero(db_adapter, mock_logger, sesion):
    _denegar("ENFERMERO", db_adapter, mock_logger, sesion)


def test_st_05_03_acceso_denegado_administrador(db_adapter, mock_logger, sesion):
    _denegar("ADMIN", db_adapter, mock_logger, sesion)


def test_st_05_04_acceso_denegado_paciente_kiosco(db_adapter, mock_logger, sesion):
    _denegar("PACIENTE", db_adapter, mock_logger, sesion)


def test_st_05_05_intentos_registrados_en_auditoria_log(db_adapter, audit_real, sesion):
    intentos = 0
    for rol, controladores in MATRIZ.items():
        for controlador in controladores:
            with pytest.raises(PermissionError):
                controlador(sesion(7, rol, "intruso"), db_adapter, audit_real)
            intentos += 1
    lineas = audit_real.ruta.read_text(encoding="utf-8").splitlines()
    denegados = [l for l in lineas if "DENEGADO/FALLO" in l]
    assert len(denegados) == intentos
    assert all("Usuario_ID: 7" in l and "Accion: ACCESO_MODULO_" in l for l in denegados)
    for rol in MATRIZ:
        assert any(f"Rol: {rol}" in l for l in denegados)
