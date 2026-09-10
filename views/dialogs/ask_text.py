"""
Mətn sorğu dialogu
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt

from utils.helpers import make_label, make_btn, center_on_parent


class AskTextDialog(QDialog):
    """Mətn daxil etmə dialogu"""

    def __init__(self, parent, title: str, prompt: str, initial: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(440, 170)
        self.result_value = None

        self._setup_ui(prompt, initial)
        center_on_parent(self, 440, 170, parent)

    def _setup_ui(self, prompt: str, initial: str):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Sorğu mətni
        layout.addWidget(make_label(prompt, bold=True))

        # Mətn sahəsi
        self.entry = QLineEdit(initial)
        self.entry.setFixedHeight(38)
        self.entry.selectAll()
        layout.addWidget(self.entry)

        # Düymələr
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = make_btn("Ləğv et", "soft")
        btn_cancel.setFixedWidth(90)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Təsdiq et")
        btn_ok.setFixedWidth(90)
        btn_ok.clicked.connect(self._accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

        # Enter düyməsi ilə təsdiq
        self.entry.returnPressed.connect(self._accept)

    def _accept(self):
        """Mətni təsdiq et"""
        value = self.entry.text().strip()
        if not value:
            return
        self.result_value = value
        self.accept()

    @staticmethod
    def get_text(parent, title: str, prompt: str, initial: str = "") -> str | None:
        """Mətn sorğusu göstər"""
        dialog = AskTextDialog(parent, title, prompt, initial)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.result_value
        return None