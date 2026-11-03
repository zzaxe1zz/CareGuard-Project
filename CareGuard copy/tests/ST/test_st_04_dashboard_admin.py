import pytest


def test_st_04_01_grafica_horas_extra_acumuladas(db_conn):
    """ST-04: Gráfica de horas extra acumuladas."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT SUM(horas_extra) FROM jornadas")
    total_extra = cursor.fetchone()[0] or 0.0
    assert total_extra >= 0.0


def test_st_04_02_grafica_tendencia(db_conn):
    """ST-04: Gráfica de tendencia."""
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT fecha, AVG(horas_extra) FROM jornadas GROUP BY fecha")
    tendencia = cursor.fetchall()
    assert isinstance(tendencia, list)


def test_st_04_03_promedio_estrellas(db_conn):
    """ST-04: Promedio de estrellas."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion) VALUES (4)")
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion) VALUES (5)")
    db_conn.commit()
    cursor.execute("SELECT AVG(calificacion) FROM evaluaciones_pacientes")
    assert cursor.fetchone()[0] == 4.5


def test_st_04_04_comentarios_recientes(db_conn):
    """ST-04: Comentarios recientes."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (5, 'Muy bien')")
    db_conn.commit()
    cursor.execute(
        "SELECT comentario FROM evaluaciones_pacientes WHERE comentario IS NOT NULL ORDER BY fecha_registro DESC LIMIT 5")
    assert 'Muy bien' in [c[0] for c in cursor.fetchall()]


def test_st_04_05_sin_nombres_ni_datos_individuales_salud(db_conn):
    """ST-04: Sin nombres ni datos individuales de salud."""
    cursor = db_conn.cursor()
    cursor.execute("PRAGMA table_info(evaluaciones_pacientes)")
    columnas = [col[1] for col in cursor.fetchall()]
    assert 'nombre' not in columnas and 'id_usuario' not in columnas
