from datetime import datetime, timedelta
import random
from database.db_adapter import DatabaseAdapter
from utils.security import generar_salt, hash_password


def sembrar_datos_completos(db_path: str = "careguard.db") -> None:
    db = DatabaseAdapter(db_path)

    # Limpiar base de datos para sembrado fresco
    db.ejecutar("DELETE FROM notificaciones")
    db.ejecutar("DELETE FROM citas")
    db.ejecutar("DELETE FROM evaluaciones_pacientes")
    db.ejecutar("DELETE FROM bitacora_psicologia")
    db.ejecutar("DELETE FROM alertas")
    db.ejecutar("DELETE FROM estados_emocionales")
    db.ejecutar("DELETE FROM descansos")
    db.ejecutar("DELETE FROM jornadas")
    db.ejecutar("DELETE FROM usuarios")

    # 1. Usuarios de prueba
    usuarios = [
        ("Admin General", "admin", "admin123", "ADMIN"),
        ("Dra. Sofia Lopez (Psicología)", "psico1", "psico123", "PSICOLOGO"),
        ("Dr. Carlos Gomez", "medico1", "medico123", "MEDICO"),
        ("Dra. Elena Rostova", "medico2", "medico123", "MEDICO"),
        ("Enf. Maria Torres", "enfermera1", "enf123", "ENFERMERO"),
    ]

    query_usr = "INSERT INTO usuarios (nombre, usuario, hash_password, salt, rol, estado) VALUES (?, ?, ?, ?, ?, 'ACTIVO')"
    ids_usr = {}
    for nombre, usr, pwd, rol in usuarios:
        salt = generar_salt()
        pwd_hash = hash_password(pwd, salt)
        id_u = db.ejecutar(query_usr, (nombre, usr, pwd_hash, salt, rol))
        ids_usr[usr] = id_u

    medicos = [ids_usr["medico1"], ids_usr["medico2"], ids_usr["enfermera1"]]
    psicologo_id = ids_usr["psico1"]

    # 2. Historial de 30 días para métricas
    hoy = datetime.now()
    for i in range(30, 0, -1):
        fecha_d = hoy - timedelta(days=i)
        fecha_str = fecha_d.strftime("%Y-%m-%d")

        for m_id in medicos:
            # Generar Jornadas
            h_entrada = f"{fecha_str} 07:00:00"
            h_trabajadas = round(random.uniform(8.0, 14.0), 1)
            h_extra = round(max(0.0, h_trabajadas - 8.0), 1)
            h_salida_d = fecha_d + timedelta(hours=h_trabajadas)
            h_salida = h_salida_d.strftime("%Y-%m-%d %H:%M:%S")

            id_j = db.ejecutar(
                "INSERT INTO jornadas (id_usuario, fecha, hora_entrada, hora_salida, horas_trabajadas, horas_extra) VALUES (?, ?, ?, ?, ?, ?)",
                (m_id, fecha_str, h_entrada, h_salida, h_trabajadas, h_extra)
            )

            # Descansos
            db.ejecutar(
                "INSERT INTO descansos (id_jornada, hora_inicio, hora_fin, duracion_minutos) VALUES (?, ?, ?, ?)",
                (id_j, f"{fecha_str} 12:00:00", f"{fecha_str} 12:30:00", 30)
            )

            # Estados Emocionales
            estres = random.randint(3, 10)
            animo = random.choice(
                ["Agotado", "Estable", "Muy Estresado", "Excelente"])
            db.ejecutar(
                "INSERT INTO estados_emocionales (id_usuario, id_jornada, fecha_registro, nivel_estres, estado_animo, notas) VALUES (?, ?, ?, ?, ?, ?)",
                (m_id, id_j, h_salida, estres, animo, "Cierre de turno habitual")
            )

            # Generar Alertas periódicas
            if estres >= 8:
                id_al = db.ejecutar(
                    "INSERT INTO alertas (id_usuario, fecha_generacion, tipo, estado, motivo) VALUES (?, ?, ?, ?, ?)",
                    (m_id, h_salida, "ALGORITMO", random.choice(
                        ["PENDIENTE", "EN_ATENCION", "CERRADA"]), f"Estrés elevado ({estres}/10) registrado al cierre.")
                )
                if random.choice([True, False]):
                    db.ejecutar(
                        "INSERT INTO citas (id_usuario, id_psicologo, fecha_hora, estado, notas) VALUES (?, ?, ?, 'PROGRAMADA', 'Seguimiento por sobrecarga')",
                        (m_id, psicologo_id, (fecha_d + timedelta(days=1)
                                              ).strftime("%Y-%m-%d 10:00:00"))
                    )

        # Evaluaciones de Pacientes
        for _ in range(random.randint(1, 4)):
            db.ejecutar(
                "INSERT INTO evaluaciones_pacientes (calificacion, comentario, fecha_registro) VALUES (?, ?, ?)",
                (random.randint(1, 5), random.choice(
                    ["Excelente atención", "Buena calidad", "Demora en urgencias", "Personal muy atento"]), fecha_str)
            )

    print("Sembrado completo de datos hospitalarios realizado con éxito.")


if __name__ == "__main__":
    sembrar_datos_completos()
