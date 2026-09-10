"""
Tətbiq konfiqurasiyası
"""
import sys
import configparser
from pathlib import Path


class Config:
    """Tətbiq parametrləri"""

    APP_NAME = "Gas Outage Management System"
    APP_VERSION = "1.0.0"

    DEFAULT_WINDOW_WIDTH = 1400
    DEFAULT_WINDOW_HEIGHT = 850
    MIN_WINDOW_WIDTH = 1100
    MIN_WINDOW_HEIGHT = 700
    DEBOUNCE_INTERVAL = 300
    STATUS_OPTIONS = [
        "Bağlı",
        "Açıq",
        "Stop"
    ]
    if getattr(sys, "frozen", False):
        BASE_DIR = Path(sys.executable).parent
    else:
        BASE_DIR = Path(__file__).resolve().parent

    SETTINGS_PATH = BASE_DIR / "settings.ini"

    DEFAULT_DB_PATH = BASE_DIR / "data" / "gas_connections.db"

    DEFAULT_AUTO_REFRESH_BASH_MS = 30000
    DEFAULT_AUTO_REFRESH_DISPETCER_MS = 0

    LOGS_DIR = BASE_DIR / "logs"
    BACKUPS_DIR = BASE_DIR / "backups"
    BACKUP_DIR = BACKUPS_DIR

    ASSETS_DIR = BASE_DIR / "assets"
    APP_ICON = ASSETS_DIR / "app.ico"
    APP_LOGO = ASSETS_DIR / "app_logo.png"

    WRITER_USERNAMES = {
        "bash",
    }

    DELETE_USERNAMES = {
        "bash",
    }

    STATUS_FILTERS = [
        "Hamısı",
        "Bağlı",
        "Açıq",
        "Stop"
    ]

    STATUS_COLORS = {
        "Bağlı": "#e74c3c",
        "Açıq": "#2ecc71",
        "Stop": "#f1c40f"
    }

    CATEGORIES = [
        "Təmir-telefonoqramma",
        "Daxili bağlantı"
    ]

    CATEGORY_OPTIONS = CATEGORIES

    DEFAULT_STATUS = "Bağlı"

    @staticmethod
    def _load_settings():
        parser = configparser.ConfigParser()

        if Config.SETTINGS_PATH.exists():
            parser.read(Config.SETTINGS_PATH, encoding="utf-8")

        return parser

    @staticmethod
    def get_db_path():
        parser = Config._load_settings()

        db_path = parser.get(
            "DATABASE",
            "db_path",
            fallback=Config.DEFAULT_DB_PATH
        )

        path = Path(db_path)
        return path if path.is_absolute() else Config.BASE_DIR / path

    @staticmethod
    def get_auto_refresh_interval(role=None):
        parser = Config._load_settings()

        bash_ms = parser.getint(
            "REFRESH",
            "AUTO_REFRESH_BASH_MS",
            fallback=Config.DEFAULT_AUTO_REFRESH_BASH_MS
        )

        dispetcer_ms = parser.getint(
            "REFRESH",
            "AUTO_REFRESH_DISPETCER_MS",
            fallback=Config.DEFAULT_AUTO_REFRESH_DISPETCER_MS
        )

        try:
            from utils.session import get_current_user, has_active_user

            if role is None and has_active_user():
                username, role = get_current_user()

        except Exception:
            pass

        if role == "bash":
            return bash_ms

        if role == "dispetcer":
            return dispetcer_ms

        return 0


    @staticmethod
    def ensure_dirs():
        Config.LOGS_DIR.mkdir(exist_ok=True, parents=True)
        Config.BACKUPS_DIR.mkdir(exist_ok=True, parents=True)
        Config.ASSETS_DIR.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def init_dirs():
        Config.ensure_dirs()


Config.DB_PATH = Config.get_db_path()
DB_PATH = Config.DB_PATH
REFRESH_INTERVAL = Config.get_auto_refresh_interval()

LOGS_DIR = Config.LOGS_DIR
BACKUPS_DIR = Config.BACKUPS_DIR
BACKUP_DIR = Config.BACKUP_DIR
ASSETS_DIR = Config.ASSETS_DIR

APP_ICON = Config.APP_ICON
APP_LOGO = Config.APP_LOGO

BASE_DIR = Config.BASE_DIR
APP_NAME = Config.APP_NAME
APP_VERSION = Config.APP_VERSION

DEFAULT_WINDOW_WIDTH = Config.DEFAULT_WINDOW_WIDTH
DEFAULT_WINDOW_HEIGHT = Config.DEFAULT_WINDOW_HEIGHT
MIN_WINDOW_WIDTH = Config.MIN_WINDOW_WIDTH
MIN_WINDOW_HEIGHT = Config.MIN_WINDOW_HEIGHT

STATUS_FILTERS = Config.STATUS_FILTERS
STATUS_COLORS = Config.STATUS_COLORS
CATEGORIES = Config.CATEGORIES
CATEGORY_OPTIONS = Config.CATEGORY_OPTIONS
DEFAULT_STATUS = Config.DEFAULT_STATUS
DEBOUNCE_INTERVAL = Config.DEBOUNCE_INTERVAL
STATUS_OPTIONS = Config.STATUS_OPTIONS
