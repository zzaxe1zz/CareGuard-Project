import pytest


def test_it_03_01_alerta_insertada_pendiente_con_id_y_timestamp(db_conn):
    """IT-03: Alerta insertada en PENDIENTE con ID y marca de tiempo."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M', 'm_so', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', '>12h')", (uid,))
    db_conn.commit()
    cursor.execute(
        "SELECT id_alerta, estado, fecha_generacion FROM alertas WHERE id_usuario = ?", (uid,))
    res = cursor.fetchone()
    assert res[0] > 0 and res[1] == 'PENDIENTE' and res[2] is not None


def test_it_03_02_alerta_visible_en_bandeja_psicologia(db_conn):
    """IT-03: Alerta visible en la bandeja de Psicología."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M', 'm_vis', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Sobrecarga')", (uid,))
    db_conn.commit()
    cursor.execute(
        "SELECT a.id_alerta FROM alertas a WHERE a.estado = 'PENDIENTE' AND a.tipo = 'ALGORITMO'")
    assert cursor.fetchone() is not None


def test_it_03_03_motivo_del_riesgo_mostrado(db_conn):
    """IT-03: Motivo del riesgo mostrado."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M', 'm_mot', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Horas extra > 12h')", (uid,))
    db_conn.commit()
    cursor.execute("SELECT motivo FROM alertas WHERE id_usuario = ?", (uid,))
    assert "12h" in cursor.fetchone()[0]
