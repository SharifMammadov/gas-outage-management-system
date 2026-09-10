"""
Əsas pəncərə
"""
import os
import threading
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QIcon

from views.tabs.records_tab import RecordsTab
from views.tabs.report_tab import ReportTab
from views.tabs.lists_tab import ListsTab
from views.tabs.offices_tab import OfficesTab
from utils.permissions import can_see_report, can_see_lists, can_backup, can_edit
from utils.session import clear_current_user
from utils.i18n import t
import config
import logging

logger = logging.getLogger('ui')


class MainWindow(QMainWindow):
    def __init__(self, role: str, username: str):
        super().__init__()
        self.role = role
        self.username = username

        self.setWindowTitle(f"{t('Qaz Bağlantıları')} ({t(role)}) - {username}")

        if os.path.exists(config.Config.APP_ICON):
            try:
                self.setWindowIcon(QIcon(str(config.Config.APP_ICON)))
            except Exception:
                pass

        screen = QGuiApplication.primaryScreen().geometry()
        w = max(int(screen.width() * 0.92), config.Config.DEFAULT_WINDOW_WIDTH)
        h = max(int(screen.height() * 0.90), config.Config.DEFAULT_WINDOW_HEIGHT)
        self.setGeometry(20, 20, w, h)
        self.setMinimumSize(
            config.Config.MIN_WINDOW_WIDTH,
            config.Config.MIN_WINDOW_HEIGHT
        )

        self._setup_ui()

        self._timer = None
        self._update_last_refresh_label()
        logger.info("Auto refresh tam söndürüldü, yalnız manual refresh aktivdir")

        logger.info(f"Əsas pəncərə açıldı: {role} / {username}")

    def _setup_ui(self):
        """İnterfeysi qur"""
        header = self._create_header()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs, stretch=1)

        self._create_tabs()
        self.setCentralWidget(central)

    def _create_header(self):
        """Header yarat"""
        header = QWidget()
        header.setProperty("class", "header")
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #2b5797;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Qaz Bağlantıları İdarəetmə Sistemi")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")

        self.theme_btn = QPushButton("🌓 Tema")
        self.theme_btn.setFixedSize(100, 36)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.theme_btn.clicked.connect(self._toggle_theme)

        self.refresh_btn = QPushButton("🔄 Yenilə")
        self.refresh_btn.setFixedSize(100, 36)
        self.refresh_btn.setStyleSheet(self.theme_btn.styleSheet())
        self.refresh_btn.clicked.connect(self._manual_refresh)

        self.last_refresh_label = QLabel("Son yenilənmə: -")
        self.last_refresh_label.setStyleSheet(
            "color: #d7e7f7; font-size: 9pt; background: transparent;"
        )
        self.last_refresh_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        user_info = QLabel(f"{self.username} ({t(self.role)})")
        user_info.setStyleSheet(
            "color: #a8c4e0; font-size: 10pt; background: transparent;"
        )
        user_info.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.theme_btn)
        layout.addSpacing(10)
        layout.addWidget(self.refresh_btn)
        layout.addSpacing(10)
        layout.addWidget(self.last_refresh_label)
        layout.addSpacing(10)

        if can_backup(self.role, self.username):
            self.backup_btn = QPushButton("💾 Backup")
            self.backup_btn.setFixedSize(100, 36)
            self.backup_btn.setStyleSheet(self.theme_btn.styleSheet())
            self.backup_btn.clicked.connect(self._manual_backup)
            layout.addWidget(self.backup_btn)
            layout.addSpacing(10)

        layout.addWidget(user_info)
        return header

    def _manual_backup(self):
        """Manual backup yarat"""
        if not can_backup(self.role, self.username):
            QMessageBox.warning(
                self,
                "İcazə yoxdur",
                "Backup yaratmaq icazəniz yoxdur."
            )
            return

        from utils.backup import backup_manager
        backup_file = backup_manager.create_backup(backup_type="manual")
        if backup_file:
            QMessageBox.information(self, "Backup", f"Backup yaradıldı:\n{backup_file}")
        else:
            QMessageBox.warning(self, "Xəta", "Backup yaradıla bilmədi!")

    def _toggle_theme(self):
        """Temanı dəyişdir"""
        try:
            from utils.theme import current_theme, set_theme, get_qss

            if current_theme == "light":
                set_theme("dark")
                self.theme_btn.setText(t("☀️ Açıq"))
            else:
                set_theme("light")
                self.theme_btn.setText(t("🌙 Tünd"))

            QApplication.instance().setStyleSheet(get_qss())
            self._update_header_color()

            logger.info(f"Tema dəyişdirildi: {current_theme}")
        except Exception as e:
            logger.error(f"Tema dəyişmə xətası: {e}")

    def _update_header_color(self):
        """Header rəngini yenilə"""
        for child in self.findChildren(QWidget):
            if child.property("class") == "header":
                child.setStyleSheet("background-color: #2b5797;")

    def _create_tabs(self):
        """Tab-ları yarat"""
        self.records_tab = RecordsTab(self)
        self.tabs.addTab(self.records_tab, "📋 Bağlantılar")

        if can_see_report(self.role):
            self.report_tab = ReportTab(self)
            self.tabs.addTab(self.report_tab, "📊 Hesabat")

        if can_see_lists(self.role):
            self.lists_tab = ListsTab(self)
            self.tabs.addTab(self.lists_tab, "📝 Rayon və səbəblər")

        self.offices_tab = OfficesTab(self)
        self.tabs.addTab(self.offices_tab, "🏢 İdarələr")

    def _setup_auto_refresh(self):
        """
        Role görə auto refresh-i qur.

        settings.ini:
        - AUTO_REFRESH_BASH_MS=30000  -> bash üçün 30 saniyə
        - AUTO_REFRESH_DISPETCER_MS=0 -> dispetçer üçün auto refresh OFF
        """
        interval = config.Config.get_auto_refresh_interval(self.role)

        if interval and interval > 0:
            self._timer.start(interval)
            logger.info(f"Auto refresh aktivdir: {interval} ms ({self.role})")
        else:
            self._timer.stop()
            logger.info(f"Auto refresh söndürülüb: {self.role}")

    def _manual_refresh(self):
        """Manual yeniləmə düyməsi."""
        self._refresh_all()

    def _update_last_refresh_label(self):
        """Son yenilənmə vaxtını header-də göstər."""
        if hasattr(self, 'last_refresh_label'):
            now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.last_refresh_label.setText(f"{t('Son yenilənmə:')} {now}")

    def _refresh_all(self):
        """Bütün tab-ları yenilə."""
        if hasattr(self, 'records_tab'):
            self.records_tab.refresh()

        if hasattr(self, 'report_tab'):
            self.report_tab.refresh()

        if hasattr(self, 'offices_tab'):
            self.offices_tab.refresh()

        self._update_last_refresh_label()

    def backup_database(self):
        """Verilənlər bazasının backup-ını yarat"""
        if not can_backup(self.role, self.username):
            return

        def do_backup():
            import shutil
            from datetime import datetime

            try:
                config.Config.BACKUP_DIR.mkdir(exist_ok=True, parents=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = config.Config.BACKUP_DIR / f"backup_{timestamp}.db"
                shutil.copy2(config.Config.DB_PATH, backup_file)
                logger.info(f"Backup yaradıldı: {backup_file}")
            except Exception as e:
                logger.error(f"Backup xətası: {e}")

        threading.Thread(target=do_backup, daemon=True).start()

    def closeEvent(self, event):
        """Pəncərə bağlananda"""
        clear_current_user()
        logger.info("Tətbiq bağlanır")
        event.accept()
