from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    id_usuario: Optional[int]
    nombre: str
    usuario: str
    hash_password: str
    salt: str
    rol: str
    estado: str = "ACTIVO"


@dataclass
class Jornada:
    id_jornada: Optional[int]
    id_usuario: int
    fecha: str
    hora_entrada: str
    hora_salida: Optional[str] = None
    horas_trabajadas: float = 0.0
    horas_extra: float = 0.0


@dataclass
class Alerta:
    id_alerta: Optional[int]
    id_usuario: int
    fecha_generacion: str
    tipo: str  # 'ALGORITMO' o 'VOLUNTARIO'
    motivo: str
    estado: str = "PENDIENTE"  # 'PENDIENTE', 'EN_ATENCION', 'CERRADA'
