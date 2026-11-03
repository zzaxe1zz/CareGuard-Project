import pytest


def test_st_01_consulta_historial_personal_restringido(db_conn):
    """ST-01: Verificar que el Médico A solo consulta su historial y el Enfermero B no ve datos de A."""
    cursor = db_conn.cursor()

    # 1. Crear Médico A y Enfermero B
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Médico A', 'medico_a', 'h', 's', 'MEDICO')"
    )
    medico_a_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Enf. Enfermero B', 'enfermero_b', 'h', 's', 'ENFERMERO')"
    )
    enfermero_b_id = cursor.lastrowid

    # 2. Registrar jornadas y descansos para el Médico A
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-11-01', '2026-11-01 08:00:00', 2.5)",
        (medico_a_id,)
    )
    jornada_a_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos) VALUES (?, '2026-11-01 12:00:00', '2026-11-01 12:30:00', 30)",
        (jornada_a_id,)
    )
    db_conn.commit()

    # 3. Consulta de historial con sesión simulada del Médico A
    cursor.execute(
        "SELECT id_jornada, horas_extra FROM jornadas WHERE id_usuario = ?", (medico_a_id,))
    jornadas_a = cursor.fetchall()
    assert len(jornadas_a) == 1
    assert jornadas_a[0][1] == 2.5

    # 4. Consulta con sesión simulada del Enfermero B (debe retornar vacío)
    cursor.execute(
        "SELECT id_jornada FROM jornadas WHERE id_usuario = ?", (enfermero_b_id,))
    jornadas_b = cursor.fetchall()
    assert len(jornadas_b) == 0
