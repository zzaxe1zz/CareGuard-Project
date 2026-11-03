import pytest


def test_it_05_evaluacion_paciente_kiosco_exitosa(db_conn):
    """IT-05: Guardar calificación anónima y comentario opcional sin asociar claves foráneas de usuario."""
    cursor = db_conn.cursor()

    # 1. Calificación con comentario
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (?, ?)",
        (5, 'Excelente servicio del equipo de urgencias')
    )
    db_conn.commit()
    eval1_id = cursor.lastrowid

    # 2. Calificación sin comentario
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (?, ?)",
        (4, None)
    )
    db_conn.commit()
    eval2_id = cursor.lastrowid

    # Validar inserción sin requerir id_usuario
    cursor.execute(
        "SELECT calificacion, comentario FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (eval1_id,))
    res1 = cursor.fetchone()
    assert res1[0] == 5
    assert res1[1] == 'Excelente servicio del equipo de urgencias'

    cursor.execute(
        "SELECT calificacion, comentario FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (eval2_id,))
    res2 = cursor.fetchone()
    assert res2[0] == 4
    assert res2[1] is None


def test_it_05_evaluacion_paciente_calificacion_invalida(db_conn):
    """IT-05: Rechazar calificaciones fuera del rango (1 a 5)."""
    cursor = db_conn.cursor()

    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (?, ?)",
            (0, 'Inválido menor a 1')
        )

    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (?, ?)",
            (6, 'Inválido mayor a 5')
        )
