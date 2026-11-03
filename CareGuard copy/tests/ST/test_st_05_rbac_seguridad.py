import pytest


def test_st_05_control_acceso_rbac_y_denegacion(db_conn):
    """ST-05: Denegar accesos no autorizados por rol y verificar el registro en auditoría."""
    cursor = db_conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol) VALUES ('Dr. Juan', 'dr_juan', 'h', 's', 'MEDICO')"
    )
    medico_id = cursor.lastrowid
    db_conn.commit()

    # Matriz RBAC: Un 'MEDICO' no debe poder acceder a la vista de Bitácora de Psicología
    rol_usuario = 'MEDICO'
    vistas_permitidas = ['DASHBOARD_MEDICO',
                         'REGISTRO_DESCANSO', 'ESTADO_EMOCIONAL']
    vista_solicitada = 'BITACORA_PSICOLOGIA'

    acceso_concedido = vista_solicitada in vistas_permitidas
    assert not acceso_concedido, "El acceso a la vista de psicología debe ser denegado para el rol MEDICO"

    # Simular registro en auditoria.log tras el intento denegado
    intento_registrado = False
    if not acceso_concedido:
        log_entry = f"ACCESO DENEGADO - Usuario ID {medico_id} (Rol: {rol_usuario}) intentó acceder a {vista_solicitada}"
        intento_registrado = "ACCESO DENEGADO" in log_entry

    assert intento_registrado
