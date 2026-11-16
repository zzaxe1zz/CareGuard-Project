from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SessionDTO:
    id_usuario: int
    nombre: str
    usuario: str
    rol: str


@dataclass(frozen=True)
class AlertaDTO:
    id_alerta: int
    id_usuario: int
    nombre_profesional: str
    fecha_generacion: str
    tipo: str
    estado: str
    motivo: str


@dataclass(frozen=True)
class ExpedienteDTO:
    id_usuario: int
    nombre_profesional: str
    promedio_estres_reciente: float
    total_horas_extra_semana: float
    alertas_activas: int
