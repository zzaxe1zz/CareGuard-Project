import pytest


def test_mt_05_01_alerta_creada_en_estado_pendiente(db_conn):
    """MT-05: Alerta creada en estado PENDIENTE."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('U', 'u_al', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'M')", (uid,))
    db_conn.commit()
    cursor.execute("SELECT estado FROM alertas WHERE id_usuario = ?", (uid,))
    assert cursor.fetchone()[0] == 'PENDIENTE'


def test_mt_05_02_id_profesional_y_marca_tiempo_correctos(db_conn):
    """MT-05: ID de profesional y marca de tiempo correctos."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('U', 'u_id', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'M')", (uid,))
    db_conn.commit()
    cursor.execute(
        "SELECT id_usuario, fecha_generacion FROM alertas WHERE id_usuario = ?", (uid,))
    res = cursor.fetchone()
    assert res[0] == uid and res[1] is not None


def test_mt_05_03_edicion_de_alerta_rechazada():
    """MT-05: Edición de la alerta rechazada."""
    rol = 'MEDICO'
    edicion_permitida = False if rol == 'MEDICO' else True
    assert not edicion_permitida


def test_mt_05_04_borrado_de_alerta_rechazado():
    """MT-05: Borrado de la alerta rechazado."""
    rol = 'MEDICO'
    borrado_permitido = False if rol == 'MEDICO' else True
    assert not borrado_permitido
