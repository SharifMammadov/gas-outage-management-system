"""
Cari istifadəçi sessiyası.

Bu modul tətbiq daxilində login olmuş istifadəçinin adını və rolunu saxlayır.
Məqsəd: icazə yoxlamalarını yalnız UI səviyyəsində yox, həm də database səviyyəsində aparmaqdır.
"""

_current_username = None
_current_role = None


def set_current_user(username: str, role: str):
    """Cari istifadəçini yadda saxla."""
    global _current_username, _current_role
    _current_username = username
    _current_role = role


def get_current_user() -> tuple[str | None, str | None]:
    """Cari istifadəçini qaytar: (username, role)."""
    return _current_username, _current_role


def clear_current_user():
    """Sessiyanı təmizlə."""
    global _current_username, _current_role
    _current_username = None
    _current_role = None


def has_active_user() -> bool:
    """Login olmuş istifadəçi varmı?"""
    return bool(_current_username and _current_role)
