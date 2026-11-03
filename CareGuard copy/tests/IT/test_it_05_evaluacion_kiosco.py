import pytest


def test_it_05_01_calificacion_valida_con_comentario(db_conn):
    """IT-05: Calificación válida con comentario."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (5, 'Excelente')")
    db_conn.commit()
    cursor.execute(
        "SELECT calificacion, comentario FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (cursor.lastrowid,))
    res = cursor.fetchone()
    assert res[0] == 5 and res[1] == 'Excelente'


def test_it_05_02_calificacion_valida_sin_comentario(db_conn):
    """IT-05: Calificación válida sin comentario."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (4, NULL)")
    db_conn.commit()
    cursor.execute(
        "SELECT calificacion, comentario FROM evaluaciones_pacientes WHERE id_evaluacion = ?", (cursor.lastrowid,))
    res = cursor.fetchone()
    assert res[0] == 4 and res[1] is None


def test_it_05_03_valores_fuera_de_rango_rechazados(db_conn):
    """IT-05: Valores fuera de rango (0, 6, vacío) rechazados."""
    cursor = db_conn.cursor()
    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (0, 'Malo')")
    with pytest.raises(Exception):
        cursor.execute(
            "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (6, 'Supra')")


def test_it_05_04_registro_sin_claves_foraneas_usuario_paciente(db_conn):
    """IT-05: Registro sin claves foráneas de usuario o paciente."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (5, 'Anonimo')")
    db_conn.commit()
    cursor.execute("PRAGMA table_info(evaluaciones_pacientes)")
    cols = [col[1] for col in cursor.fetchall()]
    assert 'id_usuario' not in cols and 'id_paciente' not in cols


def test_it_05_05_comentario_disponible_para_dashboard(db_conn):
    """IT-05: Comentario disponible para el Dashboard."""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (5, 'Para Dash')")
    db_conn.commit()
    cursor.execute(
        "SELECT comentario FROM evaluaciones_pacientes WHERE comentario IS NOT NULL")
    assert 'Para Dash' in [c[0] for c in cursor.fetchall()]
