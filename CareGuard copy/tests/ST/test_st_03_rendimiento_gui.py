import pytest
import time


def test_st_03_01_carga_bandeja_alertas_menor_igual_2s(db_conn):
    """ST-03: Carga de la bandeja de alertas <= 2.0 s."""
    cursor = db_conn.cursor()
    t0 = time.perf_counter()
    cursor.execute("SELECT * FROM alertas WHERE estado = 'PENDIENTE'")
    _ = cursor.fetchall()
    t1 = time.perf_counter()
    assert (t1 - t0) <= 2.0


def test_st_03_02_carga_historiales_menor_igual_2s(db_conn):
    """ST-03: Carga de historiales <= 2.0 s."""
    cursor = db_conn.cursor()
    t0 = time.perf_counter()
    cursor.execute("SELECT * FROM jornadas")
    _ = cursor.fetchall()
    t1 = time.perf_counter()
    assert (t1 - t0) <= 2.0


def test_st_03_03_promedio_al_menos_5_mediciones(db_conn):
    """ST-03: Promedio de al menos 5 mediciones."""
    cursor = db_conn.cursor()
    mediciones = []
    for _ in range(5):
        t0 = time.perf_counter()
        cursor.execute("SELECT * FROM alertas")
        _ = cursor.fetchall()
        t1 = time.perf_counter()
        mediciones.append(t1 - t0)
    promedio = sum(mediciones) / len(mediciones)
    assert len(mediciones) >= 5 and promedio <= 2.0
