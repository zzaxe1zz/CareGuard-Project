"""ST-03: Tiempo de Respuesta de la GUI (consultas que alimentan las vistas) <= 2.0 s.

Volumen del diseño: 1,000 jornadas y 100 alertas. Cada carga se mide MEDICIONES veces
y se imprime cada tiempo (ejecutar con `pytest -s` para verlos en consola).
"""
import random
import statistics
import time
from datetime import datetime, timedelta

import pytest

from controllers.medical_controller import MedicalController
from controllers.psychology_controller import PsychologyController

pytestmark = pytest.mark.system
LIMITE_S, MEDICIONES = 2.0, 5
JORNADAS, ALERTAS, PROFESIONALES = 1000, 100, 4


@pytest.fixture
def volumen(db_adapter, mock_logger, crear_usuario, sesion):
    random.seed(7)
    psi = crear_usuario("psi_perf", "PSICOLOGO")
    meds = [crear_usuario(f"med_perf{i}", "MEDICO") for i in range(PROFESIONALES)]
    conn = db_adapter.obtener_conexion()
    for n in range(JORNADAS):
        m = meds[n % PROFESIONALES]
        f = (datetime.now() - timedelta(days=n // PROFESIONALES + 1)).strftime("%Y-%m-%d")
        cur = conn.execute(
            "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, horas_trabajadas, horas_extra) VALUES (?,?,?,?,?)",
            (m, f, f"{f} 07:00:00", 10.0, 2.0))
        conn.execute(
            "INSERT INTO estados_emocionales (id_usuario,id_jornada,fecha_registro,nivel_estres,estado_animo) VALUES (?,?,?,?,?)",
            (m, cur.lastrowid, f"{f} 18:00:00", random.randint(3, 10), "Estable"))
        conn.execute(
            "INSERT INTO descansos (id_jornada,hora_inicio,hora_fin,duracion_minutos) VALUES (?,?,?,30)",
            (cur.lastrowid, f"{f} 12:00:00", f"{f} 12:30:00"))
    for n in range(ALERTAS):
        conn.execute(
            "INSERT INTO alertas (id_usuario,fecha_generacion,tipo,estado,motivo) VALUES (?,?,'ALGORITMO','PENDIENTE','x')",
            (meds[n % PROFESIONALES], f"2026-10-{1 + n % 28:02d} 18:00:00"))
    conn.commit()
    conn.close()
    assert db_adapter.obtener_uno("SELECT COUNT(*) c FROM jornadas")["c"] == JORNADAS
    assert db_adapter.obtener_uno("SELECT COUNT(*) c FROM alertas")["c"] == ALERTAS
    return (PsychologyController(sesion(psi, "PSICOLOGO"), db_adapter, mock_logger),
            MedicalController(sesion(meds[0], "MEDICO"), db_adapter, mock_logger), meds[0])


def medir(nombre, fn, record_property):
    """Ejecuta `fn` MEDICIONES veces, imprime cada tiempo y devuelve la lista."""
    tiempos = []
    for i in range(MEDICIONES):
        t0 = time.perf_counter()
        fn()
        tiempos.append(time.perf_counter() - t0)
        print(f"[ST-03] {nombre} medición {i + 1}: {tiempos[-1] * 1000:.1f} ms")
    prom = statistics.mean(tiempos)
    print(f"[ST-03] {nombre} PROMEDIO: {prom * 1000:.1f} ms (límite {LIMITE_S * 1000:.0f} ms)")
    record_property(f"promedio_ms_{nombre}", round(prom * 1000, 1))
    return tiempos


def test_st_03_01_carga_de_la_bandeja_de_alertas(volumen, record_property):
    psi, _, _ = volumen
    assert statistics.mean(medir("bandeja", psi.consultar_bandeja_alertas, record_property)) <= LIMITE_S


def test_st_03_02_carga_de_historiales(volumen, record_property):
    psi, medico, id_med = volumen
    cargas = {"resumen_semanal": medico.consultar_resumen_semanal,
              "historial_propio": medico.consultar_historial_propio,
              "expediente": lambda: psi.consultar_expediente_confidencial(id_med)}
    for nombre, fn in cargas.items():
        assert statistics.mean(medir(nombre, fn, record_property)) <= LIMITE_S


def test_st_03_03_promedio_de_al_menos_5_mediciones(volumen, record_property):
    psi, medico, _ = volumen
    for nombre, fn in {"bandeja": psi.consultar_bandeja_alertas,
                       "resumen_semanal": medico.consultar_resumen_semanal}.items():
        tiempos = medir(nombre, fn, record_property)
        assert len(tiempos) >= 5
        assert statistics.mean(tiempos) == pytest.approx(sum(tiempos) / len(tiempos))
        assert statistics.mean(tiempos) <= LIMITE_S
