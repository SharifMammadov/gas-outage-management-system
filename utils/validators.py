"""
Validasiya funksiyaları
"""
import re
from datetime import datetime


def validate_abonent_count(value: str) -> tuple[bool, str | None]:
    """Abonent sayını yoxla"""
    if not value or not value.strip():
        return False, "Abonent sayı boş ola bilməz"

    try:
        count = int(value.strip())
        if count < 0:
            return False, "Abonent sayı mənfi ola bilməz"
        if count > 100000:
            return False, "Abonent sayı çox böyükdür (max 100000)"
        return True, None
    except ValueError:
        return False, "Abonent sayı rəqəm olmalıdır"


def validate_pipe_mm(value: str) -> tuple[bool, str | None]:
    """Qaz xətti diametrini yoxla"""
    if not value or not value.strip():
        return True, None  # Boş ola bilər

    try:
        mm = int(value.strip())
        if mm < 0:
            return False, "Diametr mənfi ola bilməz"
        if mm > 1000:
            return False, "Diametr çox böyükdür (max 1000 mm)"
        return True, None
    except ValueError:
        return False, "Diametr rəqəm olmalıdır"


def validate_required(value: str, field_name: str) -> tuple[bool, str | None]:
    """Məcburi sahəni yoxla"""
    if not value or not value.strip():
        return False, f"{field_name} boş ola bilməz"
    return True, None


def validate_date(date_str: str) -> tuple[bool, str | None]:
    """Tarix formatını yoxla"""
    if not date_str or not date_str.strip():
        return False, "Tarix daxil edin"

    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
        return False, "Tarix formatı: gg.aa.iiii"

    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True, None
    except ValueError:
        return False, "Yanlış tarix"


def validate_phone(phone: str) -> tuple[bool, str | None]:
    """Telefon nömrəsini yoxla"""
    if not phone:
        return True, None  # Boş ola bilər

    # +994 XX XXX XX XX formatı
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    if re.match(r'^\+?994\d{9}$', cleaned) or re.match(r'^0\d{9}$', cleaned):
        return True, None
    else:
        return False, "Telefon formatı: +994 XX XXX XX XX"


def validate_email(email: str) -> tuple[bool, str | None]:
    """Email ünvanını yoxla"""
    if not email:
        return True, None  # Boş ola bilər

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, None
    else:
        return False, "Email formatı düzgün deyil"