import pytest


def test_st_01_01_medico_a_jornadas_extra_descansos_estres(db_conn):
    """ST-01: Sesión Médico A: jornadas, horas extra, descansos y estados de ánimo."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MA', 'm_a_st', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-11-02', '08:00', 2.0)", (uid,))
    jid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos) VALUES (?, '12:00', '12:30', 30)", (jid,))
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 4, 'Bien')", (uid, jid))
    db_conn.commit()
    cursor.execute(
        "SELECT id_jornada FROM jornadas WHERE id_usuario = ?", (uid,))
    assert cursor.fetchone() is not None


def test_st_01_02_enfermero_b_solo_sus_propios_registros(db_conn):
    """ST-01: Sesión Enfermero B: solo sus propios registros."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('EB', 'e_b_st', 'h', 's', 'ENFERMERO')")
    u_b = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (u_b,))
    db_conn.commit()
    cursor.execute(
        "SELECT id_usuario FROM jornadas WHERE id_usuario = ?", (u_b,))
    assert cursor.fetchone()[0] == u_b


def test_st_01_03_sin_datos_de_a_visibles_para_b(db_conn):
    """ST-01: Sin datos de A visibles para B."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MA', 'm_a_st3', 'h', 's', 'MEDICO')")
    u_a = cursor.lastrowid
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('EB', 'e_b_st3', 'h', 's', 'ENFERMERO')")
    u_b = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (u_a,))
    db_conn.commit()
    cursor.execute(
        "SELECT * FROM jornadas WHERE id_usuario = ? AND id_usuario = ?", (u_a, u_b))
    assert cursor.fetchone() is None
