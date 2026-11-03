import pytest


def test_st_02_consulta_expediente_emocional_confidencial(db_conn):
    """ST-02: El Psicólogo selecciona a un profesional con alerta activa y visualiza su historial emocional y jornadas."""
    cursor = db_conn.cursor()

    # 1. Crear Profesional (Paciente) y Psicólogo
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Evaluado', 'dr_eval', 'h', 's', 'MEDICO')"
    )
    id_paciente = cursor.lastrowid

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Psi. Lider', 'psi_lider', 'h', 's', 'PSICOLOGO')"
    )
    id_psicologo = cursor.lastrowid

    # 2. Registrar historial emocional, jornada y alerta activa
    cursor.execute(
        "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-11-01', '2026-11-01 08:00:00', 4.0)",
        (id_paciente,)
    )
    id_jornada = cursor.lastrowid

    cursor.execute(
        "INSERT INTO estados_emocionales (id_usuario, id_jornada, nivel_estres, estado_animo) VALUES (?, ?, 8, 'Agotado')",
        (id_paciente, id_jornada)
    )

    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Estrés alto')",
        (id_paciente,)
    )
    db_conn.commit()

    # 3. El Psicólogo abre el expediente del profesional con alerta activa
    cursor.execute(
        """
        SELECT u.nombre, e.nivel_estres, e.estado_animo, j.horas_extra 
        FROM usuarios u
        JOIN estados_emocionales e ON u.id_usuario = e.id_usuario
        JOIN jornadas j ON u.id_usuario = j.id_usuario
        WHERE u.id_usuario = ?
        """,
        (id_paciente,)
    )
    expediente = cursor.fetchone()

    assert expediente is not None
    assert expediente[0] == 'Dr. Evaluado'
    assert expediente[1] == 8
    assert expediente[2] == 'Agotado'
    assert expediente[3] == 4.0
