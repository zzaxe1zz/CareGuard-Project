import pytest
import time


def test_st_03_tiempo_respuesta_bandeja_con_alto_volumen(db_conn):
    """ST-03: Carga de la bandeja de alertas con 1,000 jornadas y 100 alertas en un tiempo promedio <= 2.0 s en 5 mediciones."""
    cursor = db_conn.cursor()

    # 1. Poblado masivo de prueba (10 usuarios, 1000 jornadas, 100 alertas)
    for i in range(1, 11):
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES (?, ?, 'h', 's', 'MEDICO')",
            (f"Usuario {i}", f"user_st_{i}")
        )

    cursor.execute("SELECT id_usuario FROM usuarios")
    usuarios_ids = [row[0] for row in cursor.fetchall()]

    for j in range(1000):
        uid = usuarios_ids[j % len(usuarios_ids)]
        cursor.execute(
            "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_extra) VALUES (?, '2026-11-01', '2026-11-01 08:00:00', 1.0)",
            (uid,)
        )

    for a in range(100):
        uid = usuarios_ids[a % len(usuarios_ids)]
        cursor.execute(
            "INSERT INTO alertas (id_usuario, tipo, estado, motivo) VALUES (?, 'ALGORITMO', 'PENDIENTE', 'Estrés acumulado')",
            (uid,)
        )
    db_conn.commit()

    # 2. Promedio de al menos 5 mediciones de tiempo de respuesta
    mediciones = []
    for _ in range(5):
        t_inicio = time.perf_counter()
        cursor.execute(
            """
            SELECT a.id_alerta, u.nombre, a.tipo, a.estado, a.motivo 
            FROM alertas a 
            JOIN usuarios u ON a.id_usuario = u.id_usuario 
            WHERE a.estado = 'PENDIENTE'
            """
        )
        _ = cursor.fetchall()
        t_fin = time.perf_counter()
        mediciones.append(t_fin - t_inicio)

    promedio_segundos = sum(mediciones) / len(mediciones)

    # Assert: Carga promedio <= 2.0 segundos
    assert promedio_segundos <= 2.0, f"La carga tardó {promedio_segundos:.4f}s, superando el límite de 2.0s"
