"""
Verilənlər bazası əməliyyatları
"""
import sqlite3
import threading
from contextlib import closing
import logging
from pathlib import Path
from urllib.parse import quote

from config import Config
from utils.session import get_current_user, has_active_user
from utils.permissions import can_edit, can_delete, is_readonly
from utils.security import hash_password

logger = logging.getLogger('database')


WRITE_COMMANDS = {
    "insert", "update", "delete", "replace",
    "create", "drop", "alter", "pragma", "vacuum", "reindex"
}


class Database:
    """Verilənlər bazası sinfi - Singleton pattern"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = self._get_db_path()
            self.initialized = True
            self._init_db()

    def _get_db_path(self):
        """
        Verilənlər bazası yolunu settings.ini faylından götür.

        Məntiq:
        - EXE lokal kompüterdə qalır
        - DB yolu settings.ini-də yazılır
        - IP/qovluq dəyişəndə EXE yenidən yığılmır, sadəcə settings.ini dəyişir
        """
        db_path = Config.get_db_path()

        try:
            db_path.parent.mkdir(exist_ok=True, parents=True)
            logger.info(f"📁 DB qovluğu: {db_path.parent}")
        except Exception as e:
            logger.error(f"DB qovluğu yaradıla bilmədi: {e}")
            raise

        logger.info(f"📁 Verilənlər bazası: {db_path}")
        return db_path

    def _sqlite_readonly_uri(self):
        """SQLite üçün read-only URI hazırla."""
        path = str(self.db_path.resolve()).replace("\\", "/")
        return "file:" + quote(path, safe="/:") + "?mode=ro"

    def _query_command(self, query: str) -> str:
        """Sorğunun ilk SQL əmrini qaytar."""
        if not query:
            return ""
        cleaned = query.strip().lower()
        while cleaned.startswith("--"):
            parts = cleaned.split("\n", 1)
            cleaned = parts[1].strip() if len(parts) > 1 else ""
        return cleaned.split(None, 1)[0] if cleaned else ""

    def _is_write_query(self, query: str) -> bool:
        """Sorğu yazma/sxem dəyişmə əməliyyatıdırmı?"""
        return self._query_command(query) in WRITE_COMMANDS

    def _check_write_permission(self, query: str):
        """
        Login olmuş istifadəçidə yazma icazəsini yoxla.
        Tətbiq hələ login mərhələsində deyilsə, init_db üçün icazə verilir.
        """
        if not self._is_write_query(query):
            return

        if not has_active_user():
            # Sistem start/init/login mərhələsi üçün icazə verilir.
            return

        username, role = get_current_user()
        command = self._query_command(query)

        if command == "delete" and not can_delete(role, username):
            raise PermissionError("Bu istifadəçinin silmə icazəsi yoxdur.")

        if command != "delete" and not can_edit(role, username):
            raise PermissionError("Bu istifadəçinin yazma/redaktə icazəsi yoxdur.")

    def get_connection(self, read_only: bool | None = None):
        """
        Yeni verilənlər bazası bağlantısı yarat.

        read_only=None olduqda login sessiyasına baxılır:
        - dispetçer və yazma hüququ olmayan istifadəçi: read-only connection
        - admin / icazəli baş istifadəçi: write connection

        Şəbəkə qovluğu üçün WAL əvəzinə DELETE journal rejimi saxlanılır.
        """
        try:
            if read_only is None:
                username, role = get_current_user()
                read_only = has_active_user() and is_readonly(role, username)

            if read_only:
                # UNC path (\\server\share) SQLite URI ilə problem yarada bilər.
                # Ona görə read-only rejimdə də birbaşa Windows path ilə qoşuluruq,
                # yazmanı isə PRAGMA query_only=ON bloklayır.
                conn = sqlite3.connect(
                    str(self.db_path),
                    timeout=60,
                    check_same_thread=False
                )
                conn.execute("PRAGMA busy_timeout=60000")
                conn.execute("PRAGMA query_only=ON")
                return conn

            self.db_path.parent.mkdir(exist_ok=True, parents=True)
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=60,
                check_same_thread=False
            )

            # Network/share istifadəsi üçün WAL yox, DELETE daha təhlükəsizdir.
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA busy_timeout=60000")
            conn.execute("PRAGMA query_only=OFF")
            return conn

        except Exception as e:
            logger.error(f"Verilənlər bazası bağlantı xətası: {e}")
            raise

    def _init_db(self):
        """Verilənlər bazasını yarat"""
        try:
            with closing(self.get_connection(read_only=False)) as conn:
                c = conn.cursor()

                c.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                """)

                c.execute("""
                    CREATE TABLE IF NOT EXISTS rayons (
                        name TEXT PRIMARY KEY
                    )
                """)

                c.execute("""
                    CREATE TABLE IF NOT EXISTS reasons (
                        name TEXT PRIMARY KEY
                    )
                """)

                c.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rayon TEXT NOT NULL,
                        küçə TEXT NOT NULL,
                        reason TEXT,
                        abonent_count INTEGER DEFAULT 0,
                        category TEXT,
                        pipe_mm INTEGER,
                        closed_at TEXT,
                        opened_at TEXT,
                        status TEXT DEFAULT 'Bağlı'
                    )
                """)

                c.execute("""
                    CREATE TABLE IF NOT EXISTS offices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        address TEXT NOT NULL,
                        region_name TEXT,
                        region_kod INTEGER,
                        rayon_kod INTEGER,
                        phone TEXT,
                        notes TEXT
                    )
                """)

                default_users = [
                    ("admin", hash_password("demo123"), "admin"),
                    ("manager", hash_password("demo123"), "bash"),
                    ("viewer", hash_password("demo123"), "dispetcer")
                ]

                for user in default_users:
                    try:
                        c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)", user)
                    except Exception:
                        pass

                default_rayons = [
                    ("Nərimanov",), ("Nizami",), ("Xətai",),
                    ("Yasamal",), ("Səbail",), ("Binəqədi",),
                    ("Sabunçu",), ("Qaradağ",), ("Suraxanı",),
                    ("Xəzər",), ("Abşeron",), ("Sumqayıt",),
                    ("Gəncə",), ("Bərdə",), ("Şəmkir",)
                ]

                for rayon in default_rayons:
                    try:
                        c.execute("INSERT OR IGNORE INTO rayons VALUES (?)", rayon)
                    except Exception:
                        pass

                default_reasons = [
                    ("Təmir işləri",), ("Borc",), ("Qəza",),
                    ("Yenidənqurma",), ("Müvəqqəti dayandırma",)
                ]

                for reason in default_reasons:
                    try:
                        c.execute("INSERT OR IGNORE INTO reasons VALUES (?)", reason)
                    except Exception:
                        pass

                conn.commit()

                tables = c.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

                logger.info(f"✅ Verilənlər bazası hazırlandı: {self.db_path}")
                logger.info(f"📊 Cədvəllər: {len(tables)}")

        except Exception as e:
            logger.error(f"❌ Verilənlər bazası yaratma xətası: {e}")
            raise

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        """SQL sorğusunu icra et"""
        conn = None
        try:
            self._check_write_permission(query)
            write_query = self._is_write_query(query)
            conn = self.get_connection(read_only=not write_query if has_active_user() else False)
            c = conn.cursor()
            c.execute(query, params)

            if write_query:
                conn.commit()

            if fetchone:
                return c.fetchone()
            elif fetchall:
                return c.fetchall()
            return None

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"Database execute xətası: {e}")
            raise

        finally:
            if conn:
                conn.close()


_db = None


def get_conn(read_only: bool | None = None):
    """Verilənlər bazası bağlantısı qaytar"""
    global _db
    if _db is None:
        _db = Database()
    return _db.get_connection(read_only=read_only)


def init_db():
    """Verilənlər bazasını init et"""
    global _db
    _db = Database()
    return _db
