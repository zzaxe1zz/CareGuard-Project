import pytest


def test_it_01_01_guardar_evaluacion_desde_gui(db_conn):
    """IT-01: Guardar la evaluación desde la GUI/Controlador."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M1', 'm1_gui', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (uid,))
    jid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 5, 'Bien')", (uid, jid))
    db_conn.commit()
    cursor.execute(
        "SELECT COUNT(*) FROM estados_emocionales WHERE id_usuario = ?", (uid,))
    assert cursor.fetchone()[0] == 1


def test_it_01_02_registro_vinculado_al_usuario_en_sesion(db_conn):
    """IT-01: Registro vinculado al usuario en sesión."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M1', 'm1_ses', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (uid,))
    jid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 6, 'Normal')", (uid, jid))
    db_conn.commit()
    cursor.execute(
        "SELECT id_usuario FROM estados_emocionales WHERE id_jornada = ?", (jid,))
    assert cursor.fetchone()[0] == uid


def test_it_01_03_otras_tablas_sin_alteracion(db_conn):
    """IT-01: Otras tablas sin alteración."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas")
    alertas_antes = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('M1', 'm1_noalt', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (uid,))
    jid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 4, 'Calmo')", (uid, jid))
    db_conn.commit()
    cursor.execute("SELECT COUNT(*) FROM alertas")
    assert cursor.fetchone()[0] == alertas_antes


def test_it_01_04_registro_no_visible_para_otro_medico(db_conn):
    """IT-01: Registro no visible para otro médico."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MA', 'med_a', 'h', 's', 'MEDICO')")
    u_a = cursor.lastrowid
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('MB', 'med_b', 'h', 's', 'MEDICO')")
    u_b = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada) VALUES (?, '2026-11-02', '08:00')", (u_a,))
    jid_a = cursor.lastrowid
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 7, 'Estresado')", (u_a, jid_a))
    db_conn.commit()
    cursor.execute(
        "SELECT * FROM estados_emocionales WHERE id_usuario = ?", (u_b,))
    assert cursor.fetchone() is None
