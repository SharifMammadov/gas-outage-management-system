"""
Status dəyişmə dialogu
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta

from utils.helpers import make_label, center_on_parent
from utils.date_utils import (
    today_date_str, is_valid_date_ddmmyyyy,
    make_dt_str, time_choices
)
from utils.theme import C_MUTED
from utils.i18n import t
import config

class StatusDialog(QDialog):
    """Status dəyişmə dialogu"""

    def __init__(self, parent, current_status: str):
        super().__init__(parent)
        self.setWindowTitle("Status dəyiş")
        self.setModal(True)
        self.setFixedSize(400, 280)
        self._result = None
        self.current_status = current_status

        self._setup_ui()
        center_on_parent(self, 400, 280, parent)

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Cari status
        layout.addWidget(self._make_label(
            f"{t('Cari status:')} {t(self.current_status)}", "muted"
        ))

        # Form
        form = QFormLayout()
        form.setSpacing(12)

        # Status seçimi
        self.cb_status = QComboBox()
        for status in config.Config.STATUS_OPTIONS:
            self.cb_status.addItem(t(status), status)
        self.cb_status.setCurrentIndex(self.cb_status.findData(self.current_status))
        self.cb_status.setFixedHeight(36)
        self.cb_status.currentIndexChanged.connect(self._update_hint)
        form.addRow(self._make_label("Yeni status:", bold=True), self.cb_status)

        # Tarix/Saat
        dt_widget = self._create_datetime_widget()
        form.addRow(self._make_label("Tarix / Saat:", bold=True), dt_widget)

        layout.addLayout(form)

        # Köməkçi mətn
        self.hint_label = QLabel()
        self.hint_label.setStyleSheet(f"color: {C_MUTED}; font-size: 9pt;")
        layout.addWidget(self.hint_label)

        self._update_hint()

        layout.addStretch()

        # Düymələr
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Ləğv et")
        btn_cancel.setFixedSize(100, 36)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Yadda saxla")
        btn_save.setFixedSize(120, 36)
        btn_save.clicked.connect(self._save)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _make_label(self, text, cls="", bold=False):
        """Köməkçi label yaratma funksiyası"""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QFont
        lbl = QLabel(text)
        if cls:
            lbl.setProperty("class", cls)
        if bold:
            f = lbl.font()
            f.setBold(True)
            lbl.setFont(f)
        return lbl

    def _round_time_to_nearest_5(self) -> str:
        """Cari vaxtı ən yaxın 5 dəqiqəyə yuvarlaqlaşdır.

        Nümunə:
        - 14:33 -> 14:35
        - 14:37 -> 14:35
        - 14:38 -> 14:40
        """
        now = datetime.now()
        remainder = now.minute % 5

        if remainder <= 2:
            rounded = now - timedelta(minutes=remainder)
        else:
            rounded = now + timedelta(minutes=(5 - remainder))

        rounded = rounded.replace(second=0, microsecond=0)
        return rounded.strftime("%H:%M")

    def _create_datetime_widget(self):
        """Tarix/saat seçici yarat"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Default olaraq bugünkü tarix gəlir. İstifadəçi manual dəyişə bilər.
        self.ent_date = QLineEdit(today_date_str())
        self.ent_date.setFixedWidth(110)
        self.ent_date.setFixedHeight(36)

        # Saat 5 dəqiqəlik siyahıdan seçilir.
        # Default olaraq cari vaxt ən yaxın 5 dəqiqəyə yuvarlaqlaşdırılır.
        self.cb_time = QComboBox()
        self.cb_time.addItems(time_choices(5))
        self.cb_time.setCurrentText(self._round_time_to_nearest_5())
        self.cb_time.setFixedWidth(100)
        self.cb_time.setFixedHeight(36)
        self.cb_time.setEditable(False)

        layout.addWidget(self.ent_date)
        layout.addWidget(self.cb_time)
        layout.addStretch()

        return widget

    def _update_hint(self):
        """Köməkçi mətni yenilə"""
        status = self.cb_status.currentData()

        if status == "Açıq":
            self.hint_label.setText(
                t("ℹ️ Qeyd: Bu tarix/saat 'Açıldı' sütununa yazılacaq.")
            )
        elif status == "Bağlı":
            self.hint_label.setText(
                t("ℹ️ Qeyd: Bu tarix/saat 'Bağlandı' sütununa yazılacaq.")
            )
        else:  # Stop
            self.hint_label.setText(
                t("ℹ️ Qeyd: Stop statusu üçün tarix/saat saxlanmayacaq.")
            )

    def _save(self):
        """Dəyişiklikləri yadda saxla"""
        new_status = self.cb_status.currentData()
        dt_value = ""

        # Açıq və Bağlı üçün tarix yoxla
        if new_status in ("Açıq", "Bağlı"):
            date_str = self.ent_date.text().strip()

            if not is_valid_date_ddmmyyyy(date_str):
                self._show_error("Tarix formatı düzgün deyil: gg.aa.iiii")
                return

            dt_value = make_dt_str(date_str, self.cb_time.currentText().strip())

        self._result = (new_status, dt_value)
        self.accept()

    def _show_error(self, message):
        """Xəta mesajı göstər"""
        QMessageBox.warning(self, "Xəta", message)

    def get_data(self) -> tuple | None:
        """Seçilmiş status və tarixi qaytar"""
        return self._result
