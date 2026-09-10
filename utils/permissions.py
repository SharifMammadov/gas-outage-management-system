"""
İcazə funksiyaları

Qayda:
- admin: tam hüquq
- WRITER_USERNAMES siyahısında olan konkret istifadəçi: yazma/redaktə/status dəyişmə hüququ
- dispetcer və digər istifadəçilər: yalnız oxuma/filter
"""

try:
    from config import Config
except Exception:  # test zamanı config import olunmasa
    Config = None

from utils.session import get_current_user


DEFAULT_WRITER_USERNAMES = {"admin", "bash"}


def normalize(value) -> str:
    """Dəyəri standart formaya sal."""
    if value is None:
        return ""
    return str(value).strip().lower()


def _writer_usernames() -> set[str]:
    """Yazma hüququ olan username-ləri qaytar."""
    if Config is not None and hasattr(Config, "WRITER_USERNAMES"):
        return {normalize(u) for u in Config.WRITER_USERNAMES}
    return {normalize(u) for u in DEFAULT_WRITER_USERNAMES}


def _resolve_user(role: str = None, username: str = None) -> tuple[str, str]:
    """
    Əgər username ötürülməyibsə, login sessiyasından götür.
    Mövcud köhnə çağırışlar üçün geriyə uyğunluq saxlayır: can_edit(role).
    """
    session_username, session_role = get_current_user()
    resolved_username = username if username is not None else session_username
    resolved_role = role if role is not None else session_role
    return normalize(resolved_role), normalize(resolved_username)


def is_admin(role: str, username: str = None) -> bool:
    """Admin yoxlaması."""
    role, _ = _resolve_user(role, username)
    return role == "admin"


def can_edit(role: str, username: str = None) -> bool:
    """
    Redaktə/yazma icazəsi.

    Admin həmişə yaza bilər.
    Bash rolunda olsa belə, yalnız WRITER_USERNAMES siyahısında olan konkret username yaza bilər.
    """
    role, username = _resolve_user(role, username)

    if role == "admin":
        return True

    return username in _writer_usernames()


def can_add(role: str, username: str = None) -> bool:
    """Əlavə etmə icazəsi."""
    return can_edit(role, username)


def can_change_status(role: str, username: str = None) -> bool:
    """Status dəyişmə icazəsi."""
    return can_edit(role, username)


def can_delete(role: str, username: str = None) -> bool:
    """Silmə icazəsi yalnız adminə verilir."""
    return is_admin(role, username)


def can_delete_lists(role: str, username: str = None) -> bool:
    """Siyahı silmə icazəsi yalnız adminə verilir."""
    return is_admin(role, username)


def can_see_report(role: str) -> bool:
    """Hesabat görmə icazəsi."""
    return True


def can_see_lists(role: str) -> bool:
    """Siyahıları görmə icazəsi."""
    return True


def can_backup(role: str, username: str = None) -> bool:
    """Backup icazəsi yalnız adminə verilir."""
    return is_admin(role, username)


def is_readonly(role: str = None, username: str = None) -> bool:
    """Yazma icazəsi yoxdursa, istifadəçi read-only sayılır."""
    return not can_edit(role, username)


def require_edit(role: str = None, username: str = None):
    """Yazma əməliyyatından əvvəl məcburi yoxlama."""
    if not can_edit(role, username):
        raise PermissionError("Bu istifadəçinin yazma/redaktə icazəsi yoxdur.")


def require_delete(role: str = None, username: str = None):
    """Silmə əməliyyatından əvvəl məcburi yoxlama."""
    if not can_delete(role, username):
        raise PermissionError("Bu istifadəçinin silmə icazəsi yoxdur.")
