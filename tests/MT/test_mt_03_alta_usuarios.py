"""MT-03: Alta de Usuarios, Roles y Credenciales (AdminController.registrar_usuario)."""
import pytest

from controllers.admin_controller import AdminController
from tests.conftest import contar
from utils.security import verificar_password

pytestmark = pytest.mark.unit


@pytest.fixture
def admin(db_adapter, mock_logger, sesion):
    return AdminController(sesion(1, "ADMIN", "admin"), db_adapter, mock_logger)


def test_mt_03_01_alta_con_cada_rol_valido(admin, db_adapter):
    for rol in ["MEDICO", "ENFERMERO", "PSICOLOGO", "ADMIN"]:
        id_u = admin.registrar_usuario(f"Nombre {rol}", f"user_{rol}", "Pass2026!", rol)
        fila = db_adapter.obtener_uno(
            "SELECT rol, estado FROM usuarios WHERE id_usuario = ?", (id_u,))
        assert fila["rol"] == rol and fila["estado"] == "ACTIVO"
    assert contar(db_adapter, "usuarios") == 4


def test_mt_03_02_rechazo_de_rol_inexistente(admin, db_adapter):
    with pytest.raises(ValueError, match="Rol"):
        admin.registrar_usuario("Dir", "director1", "Pass2026!", "DIRECTOR")
    assert contar(db_adapter, "usuarios") == 0


def test_mt_03_03_rechazo_de_usuario_duplicado(admin, db_adapter):
    admin.registrar_usuario("Uno", "dup", "Pass2026!", "MEDICO")
    with pytest.raises(ValueError, match="ya existe"):
        admin.registrar_usuario("Otro", "dup", "Pass2026!", "ENFERMERO")
    assert contar(db_adapter, "usuarios") == 1


def test_mt_03_04_rechazo_de_campos_vacios(admin, db_adapter):
    casos = [("", "u1", "Pass2026!", "MEDICO"), ("N", "", "Pass2026!", "MEDICO"),
             ("N", "u1", "", "MEDICO"), ("N", "u1", "Pass2026!", ""),
             ("   ", "u1", "Pass2026!", "MEDICO")]
    for nombre, usuario, password, rol in casos:
        with pytest.raises(ValueError):
            admin.registrar_usuario(nombre, usuario, password, rol)
    assert contar(db_adapter, "usuarios") == 0


def test_mt_03_05_contrasena_almacenada_como_hash(admin, db_adapter):
    plana = "MedPass2026!"
    id_u = admin.registrar_usuario("Dr. García", "dr_garcia", plana, "MEDICO")
    fila = db_adapter.obtener_uno(
        "SELECT hash_password, salt FROM usuarios WHERE id_usuario = ?", (id_u,))
    assert fila["hash_password"] != plana and plana not in fila["hash_password"]
    assert len(fila["hash_password"]) == 64 and len(fila["salt"]) == 32
    assert verificar_password(plana, fila["hash_password"], fila["salt"])
    assert not verificar_password("otra", fila["hash_password"], fila["salt"])
    # misma contraseña, distinta sal => distinto hash
    admin.registrar_usuario("Otro", "otro_user", plana, "MEDICO")
    hashes = [f["hash_password"] for f in db_adapter.obtener_todos("SELECT hash_password FROM usuarios")]
    assert hashes[0] != hashes[1]
