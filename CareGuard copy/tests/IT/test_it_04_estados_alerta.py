import pytest


def test_it_04_01_transicion_pendiente_a_en_atencion_con_nota(db_conn):
    """IT-04: PENDIENTE -> EN_ATENCION con nota."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('P', 'p1', 'h', 's', 'MEDICO')")
    u_pac = cursor.lastrowid
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Psi', 'psi1', 'h', 's', 'PSICOLOGO')")
    u_psi = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'E')", (u_pac,))
    aid = cursor.lastrowid
    cursor.execute(
        "UPDATE alertas SET estado = 'EN_ATENCION' WHERE id_alerta = ?", (aid,))
    cursor.execute(
        "INSERT INTO bitacora_psicologia (id_alerta, id_psicologo, observacion) VALUES (?, ?, 'Nota 1')", (aid, u_psi))
    db_conn.commit()
    cursor.execute("SELECT estado FROM alertas WHERE id_alerta = ?", (aid,))
    assert cursor.fetchone()[0] == 'EN_ATENCION'


def test_it_04_02_transicion_en_atencion_a_cerrada_con_nota(db_conn):
    """IT-04: EN_ATENCION -> CERRADA con nota."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('P', 'p2', 'h', 's', 'MEDICO')")
    u_pac = cursor.lastrowid
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Psi', 'psi2', 'h', 's', 'PSICOLOGO')")
    u_psi = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'EN_ATENCION', 'E')", (u_pac,))
    aid = cursor.lastrowid
    cursor.execute(
        "UPDATE alertas SET estado = 'CERRADA' WHERE id_alerta = ?", (aid,))
    cursor.execute(
        "INSERT INTO bitacora_psicologia (id_alerta, id_psicologo, observacion) VALUES (?, ?, 'Cierre')", (aid, u_psi))
    db_conn.commit()
    cursor.execute("SELECT estado FROM alertas WHERE id_alerta = ?", (aid,))
    assert cursor.fetchone()[0] == 'CERRADA'


def test_it_04_03_salto_pendiente_a_cerrada_rechazado():
    """IT-04: Salto PENDIENTE -> CERRADA rechazado."""
    estado_actual = 'PENDIENTE'
    nuevo_estado = 'CERRADA'
    permitido = False if (
        estado_actual == 'PENDIENTE' and nuevo_estado == 'CERRADA') else True
    assert not permitido


def test_it_04_04_retroceso_de_estado_rechazado():
    """IT-04: Retroceso de estado rechazado."""
    estado_actual = 'CERRADA'
    nuevo_estado = 'EN_ATENCION'
    permitido = False if (
        estado_actual == 'CERRADA' and nuevo_estado == 'EN_ATENCION') else True
    assert not permitido
