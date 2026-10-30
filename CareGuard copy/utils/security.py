import hashlib
import os
import re


def generar_salt() -> str:
    """Genera un salt aleatorio en formato hexadecimal."""
    return os.urandom(16).hex()


def hash_password(password: str, salt: str) -> str:
    """Genera un hash seguro utilizando PBKDF2 con HMAC-SHA256."""
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        iterations=100_000
    )
    return hash_obj.hex()


def verificar_password(password: str, hash_almacenado: str, salt: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    hash_calculado = hash_password(password, salt)
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100_000).hex() == hash_almacenado


def sanitizar_texto(texto: str) -> str:
    """Elimina caracteres potencialmente dañinos o espacios innecesarios."""
    if not texto:
        return ""
    texto_limpio = re.sub(r'[<>]', '', texto)
    return texto_limpio.strip()
