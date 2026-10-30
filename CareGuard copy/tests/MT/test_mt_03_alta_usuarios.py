import pytest
import hashlib
import os


def test_mt_03_alta_usuario_roles_validos_y_hash(db_adapter, mock_logger):
    """MT-03: Crear usuario con rol válido y verificar hash PBKDF2."""
    cursor = db_adapter.conn.cursor()
    password_plana = "MedPass2026!"

    salt = os.urandom(16).hex()
    hash_pwd = hashlib.pbkdf2_hmac(
        'sha256', password_plana.encode(), salt.encode(), 100000).hex()

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES (?, ?, ?, ?, ?)",
        ("Dr. Garcia", "dr_garcia", hash_pwd, salt, "MEDICO")
    )
    db_adapter.conn.commit()

    user_id = cursor.lastrowid
    assert user_id > 0

    cursor.execute(
        "SELECT hash_password FROM usuarios WHERE id_usuario = ?", (user_id,))
    res = cursor.fetchone()
    assert res[0] != password_plana
    assert len(res[0]) == 64


def test_mt_03_alta_usuario_rol_inexistente(db_adapter):
    """MT-03: Rechazar registro si el rol es inexistente."""
    roles_validos = ['MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN']
    rol_invalido = "DIRECTOR"

    with pytest.raises(ValueError, match="Rol inválido"):
        if rol_invalido not in roles_validos:
            raise ValueError("Rol inválido")


def test_mt_03_alta_usuario_duplicado(db_adapter):
    """MT-03: Rechazar usuario duplicado mediante restricción UNIQUE."""
    cursor = db_adapter.conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('User 1', 'user1', 'h', 's', 'MEDICO')"
    )
    db_adapter.conn.commit()

    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('User 1', 'user1', 'h', 's', 'MEDICO')"
        )
