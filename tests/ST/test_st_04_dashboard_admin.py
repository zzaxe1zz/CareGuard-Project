"""ST-04: Despliegue Completo del Dashboard del Administrador (datos que alimentan las gráficas)."""
import json

import pytest

from controllers.admin_controller import AdminController

pytestmark = pytest.mark.system
CLAVES_PROHIBIDAS = {"id_usuario", "nombre", "usuario", "nombre_profesional", "notas",
                     "estado_animo", "motivo", "hash_password", "salt"}


def claves(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k; yield from claves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from claves(v)


@pytest.fixture
def metricas(db_adapter, mock_logger, crear_usuario, crear_jornada, crear_estado, sesion):
    m1 = crear_usuario("m1", "MEDICO", nombre="Dr. Nombre Secreto")
    e1 = crear_usuario("e1", "ENFERMERO", nombre="Enf. Nombre Secreto")
    for dias in (1, 2):
        crear_estado(m1, crear_jornada(m1, dias, horas_extra=3.0), 8, dias, animo="Agotado", notas="SECRETO")
    crear_jornada(e1, 1, horas_extra=2.0)
    db_adapter.ejecutar("INSERT INTO alertas (id_usuario,tipo,estado,motivo) VALUES (?,'ALGORITMO','PENDIENTE','MOTIVO_SECRETO')", (m1,))
    for cal, com in [(5, "Excelente"), (4, "Bueno"), (3, "Regular")]:
        db_adapter.ejecutar("INSERT INTO evaluaciones_pacientes (calificacion, comentario) VALUES (?, ?)", (cal, com))
    return AdminController(sesion(99, "ADMIN"), db_adapter, mock_logger).obtener_metricas_dashboard()


def test_st_04_01_grafica_de_horas_extra_acumuladas(metricas):
    por_rol = {f["rol"]: f["total_horas_extra"] for f in metricas["horas_extra_agregadas"]}
    assert por_rol == {"MEDICO": 6.0, "ENFERMERO": 2.0}
    assert metricas["total_horas_extra"] == 8.0 and metricas["total_jornadas"] == 3


def test_st_04_02_grafica_de_tendencia(metricas):
    # lista de (día, promedio institucional de estrés); sin identificar a ningún profesional
    assert len(metricas["tendencia_estres"]) == 2
    assert all(len(t) == 2 and t[1] == 8 for t in metricas["tendencia_estres"])


def test_st_04_03_promedio_de_estrellas(metricas):
    assert metricas["promedio_satisfaccion"] == 4.0 and metricas["total_evaluaciones"] == 3


def test_st_04_04_comentarios_recientes(metricas):
    assert {c["comentario"] for c in metricas["comentarios_recientes"]} == {"Excelente", "Bueno", "Regular"}


def test_st_04_05_sin_nombres_ni_datos_individuales_de_salud(metricas):
    assert not CLAVES_PROHIBIDAS & set(claves(metricas))
    volcado = json.dumps(metricas, default=str)
    for secreto in ("Nombre Secreto", "SECRETO", "MOTIVO_SECRETO", "Agotado"):
        assert secreto not in volcado
    assert metricas["alertas_por_estado"] == {"PENDIENTE": 1}      # solo conteos agregados
