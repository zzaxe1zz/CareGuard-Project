import pytest


def test_it_01_registro_estado_animo_exitoso(db_conn):
    """IT-01: Probar el flujo completo de registro de estado emocional y vinculación al usuario en sesión."""
    cursor = db_conn.cursor()

    # 1. Crear dos usuarios para validar el aislamiento de datos por usuario en sesión
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Garcia', 'dr_garcia', 'h', 's', 'MEDICO')"
    )
    user_a_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Lopez', 'dr_lopez', 'h', 's', 'MEDICO')"
    )
    user_b_id = cursor.lastrowid

    # 2. Crear jornada activa para el usuario A
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '2026-11-02 08:00:00')",
        (user_a_id,)
    )
    jornada_a_id = cursor.lastrowid
    db_conn.commit()

    # 3. Registrar estado emocional para el usuario A
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, ?, ?)",
        (user_a_id, jornada_a_id, 4, 'Tranquilo')
    )
    db_conn.commit()

    # 4. Validar vinculación correcta al usuario A
    cursor.execute(
        "SELECT nivel_estres, estado_animo FROM estados_emocionales WHERE id_usuario = ?", (user_a_id,))
    reg_a = cursor.fetchone()
    assert reg_a is not None
    assert reg_a[0] == 4
    assert reg_a[1] == 'Tranquilo'

    # 5. Validar que el registro NO es visible para el usuario B (aislamiento de datos)
    cursor.execute(
        "SELECT * FROM estados_emocionales WHERE id_usuario = ?", (user_b_id,))
    assert cursor.fetchone() is None


def test_it_01_registro_estado_animo_estres_fuera_de_rango(db_conn):
    """IT-01: Rechazar inserción cuando el nivel de estrés viola la restricción CHECK (1 a 10)."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Test', 'dr_test', 'h', 's', 'MEDICO')"
    )
    user_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '2026-11-02 08:00:00')",
        (user_id,)
    )
    jornada_id = cursor.lastrowid
    db_conn.commit()

    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, ?, ?)",
            (user_id, jornada_id, 11, 'Estrasado')
        )
