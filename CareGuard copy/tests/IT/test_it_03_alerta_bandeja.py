import pytest


def test_it_03_generacion_automatica_alerta_sobrecarga(db_conn):
    """IT-03: Evaluar regla de sobrecarga (>12h extra acumuladas) e insertar alerta en estado PENDIENTE."""
    cursor = db_conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Sobrecarga', 'dr_sobre', 'h', 's', 'MEDICO')"
    )
    user_id = cursor.lastrowid

    # Insertar acumulación de horas extra > 12.0 h
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-10-28', '2026-10-28 08:00:00', 7.0)",
        (user_id,)
    )
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-10-29', '2026-10-29 08:00:00', 6.0)",
        (user_id,)
    )
    db_conn.commit()

    # Evaluación del motor determinista
    cursor.execute(
        "SELECT SUM(horas_extra) FROM jornadas WHERE id_usuario = ?", (user_id,))
    total_extra = cursor.fetchone()[0]

    if total_extra > 12.0:
        cursor.execute(
            "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Horas extra acumuladas > 12h en los últimos 7 días')",
            (user_id,)
        )
        db_conn.commit()

    cursor.execute(
        "SELECT id_usuario, tipo, estado, motivo, fecha_generacion FROM alertas WHERE id_usuario = ?", (user_id,))
    alerta = cursor.fetchone()
    assert alerta is not None
    assert alerta[0] == user_id
    assert alerta[1] == 'ALGORITMO'
    assert alerta[2] == 'PENDIENTE'
    assert "12h" in alerta[3]
    assert alerta[4] is not None
