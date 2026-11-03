import pytest


def test_st_02_01_seleccion_profesional_con_alerta_activa(db_conn):
    """ST-02: Selección del profesional con alerta activa."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('P', 'p_act', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'A')", (uid,))
    db_conn.commit()
    cursor.execute("SELECT id_usuario FROM alertas WHERE estado = 'PENDIENTE'")
    assert cursor.fetchone()[0] == uid


def test_st_02_02_apertura_del_expediente(db_conn):
    """ST-02: Apertura del expediente."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('P', 'p_exp', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "SELECT nombre, rol FROM usuarios WHERE id_usuario = ?", (uid,))
    expediente = cursor.fetchone()
    assert expediente[0] == 'P' and expediente[1] == 'MEDICO'


def test_st_02_03_historial_estres_animo_jornadas_visibles(db_conn):
    """ST-02: Historial de estrés, estados de ánimo y jornadas visibles."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('P', 'p_full', 'h', 's', 'MEDICO')")
    uid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-11-02', '08:00', 3.0)", (uid,))
    jid = cursor.lastrowid
    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 8, 'Agotado')", (uid, jid))
    db_conn.commit()
    cursor.execute("SELECT e.nivel_estres, e.estado_animo, j.horas_extra FROM estados_emocionales e JOIN jornadas j ON e.id_jornada = j.id_jornada WHERE e.id_usuario = ?", (uid,))
    res = cursor.fetchone()
    assert res[0] == 8 and res[1] == 'Agotado' and res[2] == 3.0
