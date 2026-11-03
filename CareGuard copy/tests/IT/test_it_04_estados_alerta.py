import pytest


def test_it_04_transicion_estado_alerta_y_bitacora(db_conn):
    """IT-04: Transición de estados (PENDIENTE -> EN_ATENCION -> CERRADA) y registro de nota en bitácora por el Psicólogo."""
    cursor = db_conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Paciente', 'dr_paciente', 'h', 's', 'MEDICO')"
    )
    id_paciente = cursor.lastrowid

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Psi. Torres', 'psi_torres', 'h', 's', 'PSICOLOGO')"
    )
    id_psicologo = cursor.lastrowid

    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Estrés alto sostenido')",
        (id_paciente,)
    )
    alerta_id = cursor.lastrowid
    db_conn.commit()

    # 1. Pasar PENDIENTE -> EN_ATENCION y registrar nota en bitácora
    cursor.execute(
        "UPDATE alertas SET estado = 'EN_ATENCION' WHERE id_alerta = ?", (alerta_id,))
    cursor.execute(
        "INSERT INTO bitacora_psicologia (id_alerta, id_psicologo, observacion) VALUES (?, ?, 'Primera sesión agendada')",
        (alerta_id, id_psicologo)
    )
    db_conn.commit()

    # 2. Pasar EN_ATENCION -> CERRADA
    cursor.execute(
        "UPDATE alertas SET estado = 'CERRADA' WHERE id_alerta = ?", (alerta_id,))
    db_conn.commit()

    # Validar actualización de estado
    cursor.execute(
        "SELECT estado FROM alertas WHERE id_alerta = ?", (alerta_id,))
    assert cursor.fetchone()[0] == 'CERRADA'

    # Validar entrada en la bitácora del psicólogo
    cursor.execute(
        "SELECT id_psicologo, observacion FROM bitacora_psicologia WHERE id_alerta = ?", (alerta_id,))
    nota = cursor.fetchone()
    assert nota[0] == id_psicologo
    assert nota[1] == 'Primera sesión agendada'


def test_it_04_rechazo_salto_estado_invalido(db_conn):
    """IT-04: Rechazar salto directo o estado no contemplado por la restricción CHECK."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Test', 'dr_test_alerta', 'h', 's', 'MEDICO')"
    )
    user_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Prueba')",
        (user_id,)
    )
    alerta_id = cursor.lastrowid
    db_conn.commit()

    with pytest.raises(Exception):
        cursor.execute(
            "UPDATE alertas SET estado = 'ARCHIVADA' WHERE id_alerta = ?", (alerta_id,))
