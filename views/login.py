"""
Giriş pəncərəsi
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QComboBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

from models.database import Database
from views.main_window import MainWindow
from utils.theme import C_ACCENT, C_MUTED
from utils.helpers import center_on_parent
from utils.session import set_current_user
from utils.security import verify_password
from utils.i18n import get_language, retranslate_widget_tree, set_language
import config
import logging

logger = logging.getLogger('auth')


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qaz Bağlantıları - Giriş")
        self.setFixedSize(420, 430)

        # Pəncərə ikonunu mövcuddursa qur
        if os.path.exists(config.Config.APP_ICON):
            try:
                self.setWindowIcon(QIcon(str(config.Config.APP_ICON)))
            except Exception:
                pass

        self._setup_ui()
        center_on_parent(self, 420, 430)
        logger.info("Giriş pəncərəsi açıldı")

    def _setup_ui(self):
        """İnterfeysi qur"""
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        # Kart
        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(6)

        # Başlıq
        title = QLabel("Qaz Bağlantıları")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_ACCENT};")
        card_layout.addWidget(title)

        # Alt başlıq
        sub = QLabel("Sistemə daxil olun")
        sub.setStyleSheet(f"color: {C_MUTED}; font-size: 11pt;")
        card_layout.addWidget(sub)
        card_layout.addSpacing(10)

        # İnterfeys dili
        card_layout.addWidget(self._make_label("Dil:", bold=True))
        self.cb_language = QComboBox()
        self.cb_language.addItem("Azərbaycan dili", "az")
        self.cb_language.addItem("English", "en")
        self.cb_language.setCurrentIndex(
            max(0, self.cb_language.findData(get_language()))
        )
        self.cb_language.setFixedHeight(36)
        self.cb_language.currentIndexChanged.connect(self._change_language)
        card_layout.addWidget(self.cb_language)
        card_layout.addSpacing(6)

        # İstifadəçi adı
        card_layout.addWidget(self._make_label("İstifadəçi adı", bold=True))
        self.ent_user = QLineEdit()
        self.ent_user.setPlaceholderText("istifadəçi adı")
        self.ent_user.setFixedHeight(40)
        card_layout.addWidget(self.ent_user)
        card_layout.addSpacing(6)

        # Şifrə
        card_layout.addWidget(self._make_label("Şifrə", bold=True))
        self.ent_pass = QLineEdit()
        self.ent_pass.setPlaceholderText("*****")
        self.ent_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.ent_pass.setFixedHeight(40)
        card_layout.addWidget(self.ent_pass)
        card_layout.addSpacing(16)

        # Giriş düyməsi
        btn = QPushButton("Daxil ol")
        btn.setFixedHeight(44)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn.clicked.connect(self._login)
        card_layout.addWidget(btn)
        card_layout.addSpacing(8)

        # Köməkçi məlumat
        hint = QLabel("Demo: admin/demo123 · manager/demo123 · viewer/demo123")
        hint.setStyleSheet(f"color: {C_MUTED}; font-size: 9pt;")
        card_layout.addWidget(hint)

        root.addWidget(card)

        # Klaviatura hadisələri
        self.ent_user.returnPressed.connect(lambda: self.ent_pass.setFocus())
        self.ent_pass.returnPressed.connect(self._login)
        self.ent_user.setFocus()

    def _change_language(self):
        """Seçilmiş dili yadda saxla və giriş ekranını yenilə."""
        set_language(self.cb_language.currentData())
        retranslate_widget_tree(self)

    def _make_label(self, text, bold=False):
        """Label yarat"""
        lbl = QLabel(text)
        if bold:
            f = lbl.font()
            f.setBold(True)
            lbl.setFont(f)
        return lbl

    def _login(self):
        """Giriş et"""
        username = self.ent_user.text().strip()
        password = self.ent_pass.text().strip()

        # Boş yoxlama
        if not username or not password:
            QMessageBox.warning(
                self, "Xəta",
                "İstifadəçi adı və şifrəni daxil edin."
            )
            return

        try:
            db = Database()
            row = db.execute(
                "SELECT password, role FROM users WHERE username=?",
                (username,),
                fetchone=True
            )

            if not row or not verify_password(password, row[0]):
                logger.warning(f"Uğursuz giriş cəhdi: {username}")
                QMessageBox.critical(
                    self, "Xəta",
                    "Login və ya şifrə yanlışdır."
                )
                return

            role = row[1]
            set_current_user(username, role)
            logger.info(f"Uğurlu giriş: {username} ({role})")

            # Əsas pəncərəni aç
            self.hide()
            self._main_window = MainWindow(role, username)
            self._main_window.show()

        except Exception as e:
            logger.error(f"Giriş xətası: {e}")
            QMessageBox.critical(self, "Xəta", str(e))
