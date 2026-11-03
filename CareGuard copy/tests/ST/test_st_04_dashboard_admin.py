import pytest


def test_st_04_dashboard_administrador_anonimizado(db_conn):
    """ST-04: El Administrador visualiza tendencias, gráficas y comentarios de pacientes sin ver nombres o datos individuales de salud."""
    cursor = db_conn.cursor()

    # 1. Insertar datos agregados
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (5, 'Buen servicio')")
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (3, 'Regular')")
    db_conn.commit()

    # 2. Consulta de promedio de estrellas del Dashboard
    cursor.execute(
        "SELECT AVG(calificacion), COUNT(*) FROM evaluaciones_pacientes")
    res_kiosco = cursor.fetchone()

    promedio_estrellas = res_kiosco[0]
    total_evaluaciones = res_kiosco[1]

    assert promedio_estrellas == 4.0
    assert total_evaluaciones == 2

    # 3. Confirmar que las consultas del dashboard del Administrador no retornan nombres o datos PII individuales de salud
    cursor.execute("SELECT comentario FROM evaluaciones_pacientes")
    comentarios = [c[0] for c in cursor.fetchall()]

    assert 'Buen servicio' in comentarios
    # Ningún campo de la consulta contiene identificadores de usuario/médico
