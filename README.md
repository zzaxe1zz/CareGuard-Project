# CareGuard

**CareGuard** es una aplicación de escritorio desarrollada en Python con interfaz gráfica (GUI) diseñada para el entorno hospitalario. Su objetivo principal es monitorear la carga laboral y el estado emocional del personal médico para prevenir el síndrome de *burnout*, canalizar la atención psicológica de manera confidencial y medir la calidad del servicio percibida por los pacientes.

---

## Descripción General y Alcance

El sistema opera mediante una arquitectura orientada a escritorio para su ejecución local en estaciones de trabajo hospitalarias. A través de un esquema de Control de Acceso Basado en Roles (RBAC), garantiza la separación estricta entre los datos operativos, la evaluación de pacientes y la información confidencial de salud mental.

### Módulos del Sistema

- **Módulo Personal Médico & Enfermería:** Formulario de *check-in* rápido al finalizar la jornada laboral (registro de turnos, horas extra y test emocional de 3 preguntas) con visualización del historial personal de registros.
- **Módulo Psicología & Bienestar Laboral:** Panel confidencial que recibe alertas automáticas cuando el sistema detecta signos de sobrecarga en un profesional, junto con un sistema de seguimiento de casos y bitácora de notas internas.
- **Módulo Pacientes (Modo Kiosco):** Interfaz pública para la recolección anónima de retroalimentación sobre la calidad, trato y puntualidad de la atención recibida.
- **Módulo Administrador:** Dashboard con métricas agregadas e indicadores gráficos (horas extra por departamento y niveles globales de satisfacción) sin acceso a expedientes ni datos emocionales individuales.

---

## Estructura del Proyecto

```text
careguard/
│
├── main.py                    # Punto de entrada de la aplicación (Loop principal Tkinter)
│
├── views/                     # CAPA UI/UX (PRESENTACIÓN)
│   ├── components/            # Widgets reutilizables (botones, modales, gráficos Matplotlib)
│   ├── medical_view.py        # Registro de turnos y nivel de estrés
│   ├── psychology_view.py     # Bandeja de alertas, expedientes emocionales y citas
│   ├── admin_dashboard.py     # Métricas globales anonimizadas y gestión de usuarios
│   └── kiosk_view.py          # Evaluación pública anónima para pacientes
│
├── controllers/               # CAPA DE CONTROLADORES Y SEGURIDAD
│   ├── auth_controller.py     # Inicio de sesión, manejo de sesión y validación RBAC
│   ├── medical_controller.py  # Intermediario para acciones del personal médico
│   ├── psychology_controller.py # Intermediario para gestión de alertas y seguimiento
│   └── admin_controller.py    # Intermediario para consultas agregadas
│
├── services/                  # CAPA DE LÓGICA DE NEGOCIO (BACKEND)
│   ├── workday_manager.py     # Cálculo de horas trabajadas y descansos acumulados
│   ├── burnout_engine.py      # Motor determinista de alertas por sobrecarga
│   └── psychology_core.py     # Procesamiento de expedientes confidenciales
│   
├── models/                    # DTOs Y ENTIDADES DE DOMINIO
│   ├── dto.py                 # Contenedores de datos (ExpedienteDTO, AlertaDTO, SessionDTO)
│   └── entities.py            # Clases del modelo interno (Usuario, Cita, Alerta)
│
├── database/                  # CAPA DE PERSISTENCIA Y AUDITORÍA
│   ├── db_adapter.py          # Conexión, driver sqlite3 y ejecución de consultas SQL
│   ├── audit_logger.py        # Módulo de registro de eventos e inmutabilidad (auditoria.log)
│   └── schema.sql             # Definición DDL de tablas e índices
│
└── utils/                     # UTILIDADES
    ├── reset_timer.py         # Hilo/Timer para restablecimiento por inactividad en Kiosco
    └── security.py            # Funciones de hashing y sanitización
```

---

## Equipo de Desarrollo (Scrum Team)

- **Diana** — Scrum Master
- **Axel** — Scrum Master
- **Tony** — Product Owner
- **Fernanda** — Product Owner