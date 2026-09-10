"""
Yeni bağlantı əlavə etmə dialogu
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.helpers import make_label, center_on_parent
from utils.date_utils import (
    today_date_str, default_time_str,
    is_valid_date_ddmmyyyy, make_dt_str, time_choices
)
from utils.validators import validate_abonent_count, validate_pipe_mm
from utils.i18n import t
import config

class AddRecordDialog(QDialog):
    """Yeni bağlantı əlavə etmə dialogu"""

    def __init__(self, parent, rayon_values: list, reason_values: list):
        super().__init__(parent)
        self.setWindowTitle("Yeni bağlantı")
        self.setModal(True)
        self.setFixedSize(540, 520)
        self._data = None

        self.rayon_values = rayon_values
        self.reason_values = reason_values

        self._setup_ui()
        center_on_parent(self, 540, 520, parent)

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Başlıq
        layout.addWidget(self._make_label("➕ Yeni bağlantı", "title"))
        layout.addWidget(self._make_label(
            "Bütün sahələri doldurun", "muted"
        ))

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Rayon
        self.cb_rayon = QComboBox()
        self.cb_rayon.setEditable(True)
        self.cb_rayon.addItems(self.rayon_values)
        self.cb_rayon.setFixedHeight(36)
        form.addRow(self._make_label("Rayon:", bold=True), self.cb_rayon)

        # Səbəb
        self.cb_reason = QComboBox()
        self.cb_reason.setEditable(True)
        for reason in self.reason_values:
            self.cb_reason.addItem(t(reason), reason)
        self.cb_reason.setFixedHeight(36)
        form.addRow(self._make_label("Bağlanma səbəbi:", bold=True), self.cb_reason)

        # Küçə
        self.ent_street = QLineEdit()
        self.ent_street.setPlaceholderText("Küçə adı, ev nömrəsi")
        self.ent_street.setFixedHeight(36)
        form.addRow(self._make_label("Küçə:", bold=True), self.ent_street)

        # Abonent sayı
        self.ent_count = QLineEdit("0")
        self.ent_count.setFixedHeight(36)
        form.addRow(self._make_label("Abonent sayı:", bold=True), self.ent_count)

        # Kateqoriya
        self.cb_category = QComboBox()
        for category in config.Config.CATEGORIES:
            self.cb_category.addItem(t(category), category)
        self.cb_category.setFixedHeight(36)
        form.addRow(self._make_label("Kateqoriya:", bold=True), self.cb_category)

        # Qaz xətti
        self.ent_pipe = QLineEdit()
        self.ent_pipe.setPlaceholderText("Boş buraxıla bilər")
        self.ent_pipe.setFixedHeight(36)
        form.addRow(self._make_label("Qaz xətti (mm):", bold=True), self.ent_pipe)

        # Tarix/Saat
        dt_widget = self._create_datetime_widget()
        form.addRow(self._make_label("Bağlanma tarixi:", bold=True), dt_widget)

        layout.addLayout(form)
        layout.addStretch()

        # Düymələr
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Ləğv et")
        btn_cancel.setFixedSize(100, 36)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Əlavə et")
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

    def _create_datetime_widget(self):
        """Tarix/saat seçici yarat"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.ent_date = QLineEdit(today_date_str())
        self.ent_date.setFixedWidth(110)
        self.ent_date.setFixedHeight(36)

        self.cb_time = QComboBox()
        self.cb_time.addItems(time_choices(5))
        self.cb_time.setCurrentText(default_time_str())
        self.cb_time.setFixedWidth(100)
        self.cb_time.setFixedHeight(36)

        layout.addWidget(self.ent_date)
        layout.addWidget(self.cb_time)
        layout.addStretch()

        return widget

    def _save(self):
        """Məlumatları yadda saxla"""
        # Dəyərləri topla
        rayon = self.cb_rayon.currentText().strip()
        reason = self.cb_reason.currentData() or self.cb_reason.currentText().strip()
        street = self.ent_street.text().strip()
        category = self.cb_category.currentData()

        # Boş sahələri yoxla
        if not rayon:
            self._show_error("Rayon adı daxil edin")
            return

        if not street:
            self._show_error("Küçə adı daxil edin")
            return

        if not category:
            self._show_error("Kateqoriya seçin")
            return

        # Abonent sayını yoxla
        is_valid, error = validate_abonent_count(self.ent_count.text())
        if not is_valid:
            self._show_error(error)
            return
        count = int(self.ent_count.text() or "0")

        # Qaz xəttini yoxla
        pipe_raw = self.ent_pipe.text().strip()
        pipe = None
        if pipe_raw:
            is_valid, error = validate_pipe_mm(pipe_raw)
            if not is_valid:
                self._show_error(error)
                return
            pipe = int(pipe_raw)

        # Tarixi yoxla
        date_str = self.ent_date.text().strip()
        if not is_valid_date_ddmmyyyy(date_str):
            self._show_error("Tarix formatı düzgün deyil: gg.aa.iiii")
            return

        # Məlumatları topla
        self._data = {
            "rayon": rayon,
            "küçə": street,
            "reason": reason,
            "abonent_count": count,
            "category": category,
            "pipe_mm": pipe,
            "closed_at": make_dt_str(date_str, self.cb_time.currentText().strip())
        }

        self.accept()

    def _show_error(self, message):
        """Xəta mesajı göstər"""
        QMessageBox.warning(self, "Xəta", message)

    def get_data(self) -> dict | None:
        """Daxil edilmiş məlumatları qaytar"""
        return self._data
