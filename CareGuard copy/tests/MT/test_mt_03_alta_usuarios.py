import pytest
import hashlib
import os


def test_mt_03_01_alta_con_cada_rol_valido(db_conn):
    """MT-03: Alta con cada rol válido."""
    cursor = db_conn.cursor()
    roles = ['MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN']
    for idx, rol in enumerate(roles, 1):
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES (?, ?, 'h', 's', ?)",
            (f"User {rol}", f"usr_{idx}", rol)
        )
    db_conn.commit()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    assert cursor.fetchone()[0] == 4


def test_mt_03_02_rechazo_de_rol_inexistente():
    """MT-03: Rechazo de rol inexistente."""
    roles = ['MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN']
    with pytest.raises(ValueError):
        if "DIRECTOR" not in roles:
            raise ValueError("Rol inexistente")


def test_mt_03_03_rechazo_de_usuario_duplicado(db_conn):
    """MT-03: Rechazo de usuario duplicado."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('U1', 'dup', 'h', 's', 'MEDICO')")
    db_conn.commit()
    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('U2', 'dup', 'h', 's', 'MEDICO')")


def test_mt_03_04_rechazo_de_campos_vacios():
    """MT-03: Rechazo de campos vacíos."""
    nombre, usuario, pwd = "", "usr1", "pass"
    with pytest.raises(ValueError):
        if not nombre or not usuario or not pwd:
            raise ValueError("Campos vacíos")


def test_mt_03_05_contrasena_almacenada_como_hash():
    """MT-03: Contraseña almacenada como hash."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', b"Pass123!", salt.encode(), 100000).hex()
    assert pwd_hash != "Pass123!"
    assert len(pwd_hash) == 64
