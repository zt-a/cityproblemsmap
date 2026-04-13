# app/services/totp.py
import pyotp
import secrets
from typing import List


def generate_totp_secret() -> str:
    """Генерирует случайный секрет для TOTP"""
    return pyotp.random_base32()


def generate_totp_uri(secret: str, username: str, issuer: str = "CityProblemMap") -> str:
    """
    Генерирует URI для QR кода.
    Используется в приложениях типа Google Authenticator.
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Проверяет TOTP код.
    Допускает небольшое отклонение времени (±1 интервал = 30 сек).
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Генерирует резервные коды для восстановления доступа.
    Каждый код можно использовать только один раз.
    """
    codes = []
    for _ in range(count):
        # Генерируем 8-значный код
        code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
        # Форматируем как XXXX-XXXX для удобства
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    return codes


def hash_backup_code(code: str) -> str:
    """Хеширует резервный код для безопасного хранения"""
    from app.services.auth import hash_password
    # Убираем дефис перед хешированием
    clean_code = code.replace("-", "")
    return hash_password(clean_code)


def verify_backup_code(code: str, hashed_code: str) -> bool:
    """Проверяет резервный код"""
    from app.services.auth import verify_password
    clean_code = code.replace("-", "")
    return verify_password(clean_code, hashed_code)
