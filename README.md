# CareGuard

**CareGuard** es una aplicación de escritorio desarrollada en Python con interfaz gráfica (CustomTkinter) diseñada para el entorno hospitalario. Su objetivo principal es monitorear la carga laboral y el estado emocional del personal médico y de enfermería para prevenir el síndrome de *burnout*, canalizar la atención psicológica de manera confidencial y medir la calidad del servicio percibida por los pacientes.

---

## Descripción General y Alcance

El sistema opera mediante una arquitectura local en capas para su ejecución en estaciones de trabajo hospitalarias con persistencia en SQLite 3. A través de un esquema de Control de Acceso Basado en Roles (RBAC) y registros de auditoría, garantiza la separación estricta entre los datos operativos, la evaluación anónima de pacientes y la información confidencial de salud mental.

### Módulos del Sistema

- **Módulo Personal Médico & Enfermería:** Gestión de jornadas laborales (registro de entrada, pausas/descansos, cierre de turno y cálculo automático de horas extra), autoevaluación de nivel de estrés y estado de ánimo, consulta de historial personal restringido y solicitud voluntaria de apoyo psicológico.
- **Módulo Psicología & Bienestar Laboral:** Bandeja confidencial que recibe alertas preventivas automáticas por sobrecarga y solicitudes voluntarias, consulta de expedientes emocionales, agendamiento de citas y seguimiento de casos con bitácora de notas internas.
- **Módulo Pacientes (Modo Kiosco):** Interfaz pública con restablecimiento automático tras 30 segundos de inactividad para la recolección anónima de calificaciones (1 a 5 estrellas) y comentarios sobre la atención recibida.
- **Módulo Administrador:** Dashboard con métricas agregadas e indicadores gráficos (horas extra acumuladas, tendencias y promedio de satisfacción) junto con gestión de alta de usuarios y roles, sin acceso a expedientes ni datos emocionales individuales.

---

## Estructura del Proyecto

```text
CareGuard/
│
├── main.py                        # Punto de entrada de la aplicación (Interfaz principal CustomTkinter)
├── pytest.ini                     # Configuración de ejecución de pruebas
├── requirements.txt               # Dependencias del proyecto
│
├── views/                         # CAPA UI/UX (PRESENTACIÓN)
│   ├── ui_kit.py                  # Componentes visuales base, paleta y estilos reutilizables
│   └── components/                # Vistas principales por rol
│       ├── medical_view.py        # Registro de turnos, descansos, estrés e historial personal
│       ├── psychology_view.py     # Bandeja de alertas, expedientes emocionales y citas
│       ├── admin_dashboard.py     # Métricas globales anonimizadas y gestión de usuarios
│       └── kiosk_view.py          # Evaluación pública anónima para pacientes
│
├── controllers/                   # CAPA DE CONTROLADORES Y SEGURIDAD
│   ├── auth_controller.py         # Inicio de sesión, manejo de sesión y validación RBAC
│   ├── medical_controller.py      # Intermediario para acciones del personal médico y enfermería
│   ├── psychology_controller.py   # Intermediario para gestión de alertas, citas y seguimiento
│   ├── admin_controller.py        # Intermediario para alta de usuarios y consultas agregadas
│   └── kiosk_controller.py        # Intermediario para registro anónimo de evaluaciones de pacientes
│
├── services/                      # CAPA DE LÓGICA DE NEGOCIO (BACKEND)
│   ├── workday_manager.py         # Cálculo de horas trabajadas, horas extra y descansos
│   ├── burnout_engine.py          # Motor determinista de alertas por sobrecarga (ventana de 7 días)
│   └── psychology_core.py         # Procesamiento de expedientes confidenciales
│
├── models/                        # DTOs Y ENTIDADES DE DOMINIO
│   ├── dto.py                     # Contenedores de datos (ExpedienteDTO, AlertaDTO, SessionDTO)
│   └── entities.py                # Clases del modelo interno (Usuario, Jornada, Cita, Alerta)
│
├── database/                      # CAPA DE PERSISTENCIA Y AUDITORÍA
│   ├── db_adapter.py              # Conexión, driver sqlite3 y ejecución de consultas SQL
│   ├── audit_logger.py            # Registro de eventos de seguridad y trazabilidad (auditoria.log)
│   ├── schema.sql                 # Definición DDL de tablas, restricciones e índices
│   └── seed.py                    # Carga inicial de datos y usuarios de prueba
│
├── utils/                         # UTILIDADES
│   ├── paths.py                   # Resolución de rutas locales de base de datos y logs
│   ├── reset_timer.py             # Temporizador en segundo plano para reinicio por inactividad en Kiosco
│   └── security.py                # Hashing de contraseñas (PBKDF2) y sanitización
│
└── tests/                         # SUITE DE PRUEBAS AUTOMATIZADAS (pytest)
    ├── conftest.py                # Fixtures compartidos y configuración de BD en memoria
    ├── MT/                        # Pruebas de Módulo / Unitarias (MT-01 a MT-05)
    ├── IT/                        # Pruebas de Integración (IT-01 a IT-05)
    └── ST/                        # Pruebas de Sistema, Rendimiento y Seguridad RBAC (ST-01 a ST-05)
```

---

## Instalación y Ejecución

1. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

2. **Ejecutar la aplicación:**

```bash
python main.py
```

3. **Ejecutar la suite de pruebas y cobertura:**

```bash
pytest -v --cov=. --cov-report=term-missing
```

---

## Equipo de Desarrollo (Scrum Team)

- **Diana** — Scrum Master
- **Axel** — Scrum Master
- **Tony** — Product Owner
- **Fernanda** — Product Owner

---

## Principales correcciones aplicadas respecto al borrador anterior

1. **Rutas de vistas corregidas:** Las vistas (`medical_view.py`, `psychology_view.py`, `admin_dashboard.py`, `kiosk_view.py`) están dentro de `views/components/`, y se agregó `views/ui_kit.py`.
2. **Archivos reales añadidos:** Se incorporaron `controllers/kiosk_controller.py`, `database/seed.py`, `utils/paths.py`, `pytest.ini`, `requirements.txt` y la carpeta completa de pruebas `tests/` (`MT/`, `IT/`, `ST/`).
3. **Stack tecnológico:** Se precisó el uso de **CustomTkinter** y **SQLite 3** junto con los comandos de ejecución y `pytest`.