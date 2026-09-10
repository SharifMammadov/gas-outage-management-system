"""
Qaz Bağlantıları İdarəetmə Sistemi
Ana giriş nöqtəsi
"""

import sys
import os

# Əsas qovluğu sys.path-ə əlavə et
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from views.login import Login
from utils.theme import get_qss, set_theme
from models.database import init_db
from logger import setup_logging
from utils.i18n import install_translation_filter

import config


def set_app_icon(app):
    """Tətbiq ikonunu mövcuddursa qur."""

    if os.path.exists(config.Config.APP_ICON):
        try:
            app.setWindowIcon(QIcon(str(config.Config.APP_ICON)))
            print(f"✅ Tətbiq ikonu yükləndi: {config.Config.APP_ICON}")
            return True
        except Exception as e:
            print(f"❌ İkon yüklənə bilmədi: {e}")
    else:
        print(f"❌ İkon faylı tapılmadı: {config.Config.APP_ICON}")

        if config.Config.ASSETS_DIR.exists():
            print("\n📁 Assets qovluğundakı fayllar:")
            for file in config.Config.ASSETS_DIR.glob("*"):
                print(f"   - {file.name}")
        else:
            print(f"📁 Assets qovluğu mövcud deyil: {config.Config.ASSETS_DIR}")

    return False


def main():
    # Loglama sistemini qur
    logger = setup_logging()
    logger.info("Tətbiq başladılır...")

    # Lazımi qovluqları yarat
    config.Config.init_dirs()

    # Assets qovluğundakı faylları göstər
    assets_dir = config.Config.ASSETS_DIR
    if assets_dir.exists():
        files = list(assets_dir.glob("*"))
        logger.info(f"Assets qovluğunda {len(files)} fayl var")
        for f in files:
            logger.info(f"  - {f.name}")
    else:
        logger.warning("Assets qovluğu mövcud deyil")

    # Verilənlər bazasını init et
    init_db()
    logger.info("Verilənlər bazası hazırdır")

    # PyQt tətbiqini başlat
    app = QApplication(sys.argv)
    app._translation_filter = install_translation_filter(app)

    # Tətbiq ikonlarını qur
    set_app_icon(app)

    # Default tema
    set_theme("light")
    app.setStyleSheet(get_qss())

    # Login pəncərəsini göstər
    win = Login()
    win.show()

    logger.info("Tətbiq işə düşdü")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
