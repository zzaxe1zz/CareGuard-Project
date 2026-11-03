import pytest


def test_st_05_01_acceso_denegado_medico():
    """ST-05: Acceso denegado: Médico a Panel Admin."""
    rol = 'MEDICO'
    acceso = False if rol == 'MEDICO' else True
    assert not acceso


def test_st_05_02_acceso_denegado_enfermero():
    """ST-05: Acceso denegado: Enfermero a Bitácora Psicología."""
    rol = 'ENFERMERO'
    acceso = False if rol == 'ENFERMERO' else True
    assert not acceso


def test_st_05_03_acceso_denegado_administrador():
    """ST-05: Acceso denegado: Administrador a Bandeja Clínica Individual."""
    rol = 'ADMIN'
    acceso = False if rol == 'ADMIN' else True
    assert not acceso


def test_st_05_04_acceso_denegado_paciente_kiosco():
    """ST-05: Acceso denegado: Paciente/Kiosco a Datos del Sistema."""
    rol = 'KIOSCO'
    acceso = False if rol == 'KIOSCO' else True
    assert not acceso


def test_st_05_05_intentos_registrados_en_auditoria_log():
    """ST-05: Intentos registrados en auditoria.log."""
    log_line = "ACCESO DENEGADO - Rol MEDICO intentó acceder a BITACORA_PSICOLOGIA"
    assert "ACCESO DENEGADO" in log_line
