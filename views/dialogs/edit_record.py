"""
Bağlantı redaktə dialogu
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt

from utils.helpers import make_label
from utils.validators import validate_abonent_count, validate_pipe_mm
from utils.theme import C_MUTED


class EditRecordDialog(QDialog):
    """Bağlantı redaktə dialogu"""

    def __init__(self, parent, values: list):
        super().__init__(parent)
        self.setWindowTitle(f"Bağlantı redaktə (ID {values[0]})")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._data = None
        self.values = values

        self._setup_ui()
        center_on_parent(self, 500, 400, parent)

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Başlıq
        layout.addWidget(make_label(f"✏️ Redaktə — ID {self.values[0]}", cls="title"))
        layout.addWidget(make_label(
            "Məlumatları dəyişdirin",
            cls="muted"
        ))

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Rayon
        self.ent_rayon = QLineEdit(self.values[1])
        self.ent_rayon.setFixedHeight(36)
        form.addRow(make_label("Rayon:", bold=True), self.ent_rayon)

        # Küçə
        self.ent_street = QLineEdit(self.values[2])
        self.ent_street.setFixedHeight(36)
        form.addRow(make_label("Küçə:", bold=True), self.ent_street)

        # Səbəb
        self.ent_reason = QLineEdit(self.values[3])
        self.ent_reason.setFixedHeight(36)
        form.addRow(make_label("Bağlanma səbəbi:", bold=True), self.ent_reason)

        # Abonent sayı
        self.ent_count = QLineEdit(self.values[4])
        self.ent_count.setFixedHeight(36)
        form.addRow(make_label("Abonent sayı:", bold=True), self.ent_count)

        # Kateqoriya
        self.ent_category = QLineEdit(self.values[5])
        self.ent_category.setFixedHeight(36)
        form.addRow(make_label("Kateqoriya:", bold=True), self.ent_category)

        # Qaz xətti
        pipe_value = "" if self.values[6] in ("None", "") else self.values[6]
        self.ent_pipe = QLineEdit(pipe_value)
        self.ent_pipe.setPlaceholderText("Boş buraxıla bilər")
        self.ent_pipe.setFixedHeight(36)
        form.addRow(make_label("Qaz xətti (mm):", bold=True), self.ent_pipe)

        layout.addLayout(form)
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

    def _save(self):
        """Dəyişiklikləri yadda saxla"""
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

        # Məlumatları topla
        self._data = {
            "rayon": self.ent_rayon.text().strip(),
            "küçə": self.ent_street.text().strip(),
            "reason": self.ent_reason.text().strip(),
            "abonent_count": count,
            "category": self.ent_category.text().strip(),
            "pipe_mm": pipe
        }

        self.accept()

    def _show_error(self, message):
        """Xəta mesajı göstər"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Xəta", message)

    def get_data(self) -> dict | None:
        """Daxil edilmiş məlumatları qaytar"""
        return self._data


# Helper function
def center_on_parent(dialog, w, h, parent):
    """Dialogu parent-in mərkəzində yerləşdir"""
    if parent:
        px = parent.x() + (parent.width() - w) // 2
        py = parent.y() + (parent.height() - h) // 2
        dialog.move(px, py)