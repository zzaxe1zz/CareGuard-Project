-- Habilitar claves foráneas
PRAGMA foreign_keys = ON;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    hash_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('MEDICO', 'ENFERMERO', 'PSICOLOGO', 'ADMIN')),
    estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO')),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Jornadas Laborales
CREATE TABLE IF NOT EXISTS jornadas (
    id_jornada INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada DATETIME NOT NULL,
    hora_salida DATETIME,
    horas_trabajadas REAL DEFAULT 0.0,
    horas_extra REAL DEFAULT 0.0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

-- Tabla de Registro de Descansos (RF-01)
CREATE TABLE IF NOT EXISTS descansos (
    id_descanso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_jornada INTEGER NOT NULL,
    hora_inicio DATETIME NOT NULL,
    hora_fin DATETIME NOT NULL,
    duracion_minutos INTEGER NOT NULL,
    FOREIGN KEY (id_jornada) REFERENCES jornadas (id_jornada) ON DELETE CASCADE
);

-- Tabla de Evaluaciones Emocionales (RF-02)
CREATE TABLE IF NOT EXISTS estados_emocionales (
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_jornada INTEGER NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    nivel_estres INTEGER NOT NULL CHECK (nivel_estres BETWEEN 1 AND 10),
    estado_animo TEXT NOT NULL,
    notas TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_jornada) REFERENCES jornadas (id_jornada) ON DELETE CASCADE
);

-- Tabla de Alertas por Sobrecarga / Voluntarias (RF-05, RF-14)
CREATE TABLE IF NOT EXISTS alertas (
    id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL CHECK (tipo IN ('ALGORITMO', 'VOLUNTARIO')),
    estado TEXT NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EN_ATENCION', 'CERRADA')),
    motivo TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

-- Tabla de Bitácora y Notas del Psicólogo (RF-06)
CREATE TABLE IF NOT EXISTS bitacora_psicologia (
    id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alerta INTEGER NOT NULL,
    id_psicologo INTEGER NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacion TEXT NOT NULL,
    FOREIGN KEY (id_alerta) REFERENCES alertas (id_alerta) ON DELETE CASCADE,
    FOREIGN KEY (id_psicologo) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

-- Tabla de Evaluaciones Anónimas de Pacientes en Kiosco (RF-09)
CREATE TABLE IF NOT EXISTS evaluaciones_pacientes (
    id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
    calificacion INTEGER NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Citas Psicológicas
CREATE TABLE IF NOT EXISTS citas (
    id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_psicologo INTEGER NOT NULL,
    fecha_hora DATETIME NOT NULL,
    estado TEXT NOT NULL DEFAULT 'PROGRAMADA' CHECK (estado IN ('PROGRAMADA', 'COMPLETADA', 'CANCELADA')),
    notas TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_psicologo) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

-- Tabla de Notificaciones Internas
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    leido INTEGER DEFAULT 0,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);