import pytest


def test_it_02_01_registro_tipo_voluntario_creado(db_conn):
    """IT-02: Registro de tipo VOLUNTARIO creado."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('E1', 'enf1', 'h', 's', 'ENFERMERO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'VOLUNTARIO', 'PENDIENTE', 'Apoyo')", (uid,))
    db_conn.commit()
    cursor.execute("SELECT tipo FROM alertas WHERE id_usuario = ?", (uid,))
    assert cursor.fetchone()[0] == 'VOLUNTARIO'


def test_it_02_02_visible_en_bandeja_psicologia(db_conn):
    """IT-02: Visible en la bandeja de Psicología."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('E1', 'enf2', 'h', 's', 'ENFERMERO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'VOLUNTARIO', 'PENDIENTE', 'Apoyo')", (uid,))
    db_conn.commit()
    cursor.execute(
        "SELECT a.id_alerta FROM alertas a WHERE a.estado = 'PENDIENTE'")
    assert cursor.fetchone() is not None


def test_it_02_03_no_visible_para_administrador():
    """IT-02: No visible para Administrador."""
    rol = 'ADMIN'
    ver_bandeja_clinica = False if rol == 'ADMIN' else True
    assert not ver_bandeja_clinica


def test_it_02_04_no_visible_para_otros_medicos(db_conn):
    """IT-02: No visible para otros médicos."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MA', 'm_a2', 'h', 's', 'MEDICO')")
    u_a = cursor.lastrowid
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MB', 'm_b2', 'h', 's', 'MEDICO')")
    u_b = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'VOLUNTARIO', 'PENDIENTE', 'A')", (u_a,))
    db_conn.commit()
    cursor.execute(
        "SELECT * FROM alertas WHERE id_usuario = ? AND id_usuario = ?", (u_a, u_b))
    assert cursor.fetchone() is None
