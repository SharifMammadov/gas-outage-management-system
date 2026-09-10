"""
Autentifikasiya kontrolleri
"""
from models.database import Database
from models.cache import Cache
from utils.session import set_current_user, clear_current_user
from utils.permissions import can_edit, can_see_report, can_see_lists
from utils.security import hash_password, verify_password
import logging

logger = logging.getLogger('auth')


class AuthController:
    """İstifadəçi autentifikasiyası kontrolleri"""

    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.current_user = None
        self.current_role = None

    def login(self, username: str, password: str) -> tuple[bool, str | None]:
        """
        İstifadəçi girişi.
        Returns: (uğurlu?, rol və ya xəta mesajı)
        """
        if not username or not password:
            return False, "İstifadəçi adı və şifrə daxil edin"

        try:
            row = self.db.execute(
                "SELECT password, role FROM users WHERE username=?",
                (username,),
                fetchone=True
            )

            if not row or not verify_password(password, row[0]):
                logger.warning(f"Uğursuz giriş cəhdi: {username}")
                return False, "İstifadəçi adı və ya şifrə yanlışdır"

            role = row[1]
            self.current_user = username
            self.current_role = role
            set_current_user(username, role)

            logger.info(f"Uğurlu giriş: {username} ({role})")
            return True, role

        except Exception as e:
            logger.error(f"Giriş xətası: {e}")
            return False, f"Sistem xətası: {str(e)}"

    def logout(self):
        """Çıxış et"""
        if self.current_user:
            logger.info(f"Çıxış: {self.current_user}")
        self.current_user = None
        self.current_role = None
        clear_current_user()

    def get_current_user(self) -> tuple[str | None, str | None]:
        """Cari istifadəçini qaytar"""
        return self.current_user, self.current_role

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Şifrə dəyiş"""
        if not old_password or not new_password:
            return False, "Köhnə və yeni şifrə daxil edin"

        try:
            row = self.db.execute(
                "SELECT password FROM users WHERE username=?",
                (username,),
                fetchone=True
            )

            if not row or not verify_password(old_password, row[0]):
                return False, "Köhnə şifrə yanlışdır"

            self.db.execute(
                "UPDATE users SET password=? WHERE username=?",
                (hash_password(new_password), username)
            )

            logger.info(f"Şifrə dəyişdirildi: {username}")
            return True, "Şifrə uğurla dəyişdirildi"

        except Exception as e:
            logger.error(f"Şifrə dəyişmə xətası: {e}")
            return False, f"Xəta: {str(e)}"

    def has_permission(self, permission: str) -> bool:
        """İcazəni yoxla"""
        if not self.current_role:
            return False

        if permission in ("edit", "add", "change_status"):
            return can_edit(self.current_role, self.current_user)

        if permission == "see_report":
            return can_see_report(self.current_role)

        if permission == "see_lists":
            return can_see_lists(self.current_role)

        if permission == "view_only":
            return True

        return False
