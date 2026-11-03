import pytest


def test_it_02_solicitud_apoyo_voluntario_crea_alerta(db_conn):
    """IT-02: Enviar solicitud voluntaria de apoyo y verificar la alerta PENDIENTE en la bandeja de Psicología."""
    cursor = db_conn.cursor()

    # 1. Crear profesional solicitante y usuario psicólogo
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Enf. Ramos', 'enf_ramos', 'h', 's', 'ENFERMERO')"
    )
    id_enfermero = cursor.lastrowid

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Psi. Morales', 'psi_morales', 'h', 's', 'PSICOLOGO')"
    )
    id_psicologo = cursor.lastrowid
    db_conn.commit()

    # 2. Generar alerta voluntaria
    cursor.execute(
        "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'VOLUNTARIO', 'PENDIENTE', 'Solicitud voluntaria de contención emocional')",
        (id_enfermero,)
    )
    db_conn.commit()
    alerta_id = cursor.lastrowid

    # 3. Verificar que la alerta esté visible en la bandeja de psicología
    cursor.execute(
        "SELECT a.id_alerta, u.nombre, a.tipo, a.estado FROM alertas a JOIN usuarios u ON a.id_usuario = u.id_usuario WHERE a.id_alerta = ?",
        (alerta_id,)
    )
    alerta = cursor.fetchone()
    assert alerta[0] == alerta_id
    assert alerta[1] == 'Enf. Ramos'
    assert alerta[2] == 'VOLUNTARIO'
    assert alerta[3] == 'PENDIENTE'
