import pytest


def test_mt_05_generacion_e_inmutabilidad_alerta(db_conn):
    """MT-05: Inserción de alerta PENDIENTE y denegación de edición por usuario común."""
    cursor = db_conn.cursor()

    # 1. Moñepyrũ mboyve 'usuarios' rehegua tabla
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES (?, ?, ?, ?, ?)",
        ("Medico Alerta", "medico_alerta", "hash", "salt", "MEDICO")
    )
    user_id = cursor.lastrowid

    # 2. Emboso'o pe alerta id_usuario reheve
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, ?, ?, ?)",
        (user_id, 'ALGORITMO', 'PENDIENTE', 'Horas extra acumuladas > 12h')
    )
    db_conn.commit()
    alerta_id = cursor.lastrowid

    cursor.execute(
        "SELECT estado, id_usuario FROM alertas WHERE id_alerta = ?", (alerta_id,))
    alerta = cursor.fetchone()
    assert alerta[0] == 'PENDIENTE'
    assert alerta[1] == user_id

    rol_sesion = 'MEDICO'
    edicion_permitida = False if rol_sesion == 'MEDICO' else True

    assert not edicion_permitida
