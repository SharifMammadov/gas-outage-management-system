"""
İdarə redaktə dialogu
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.helpers import make_label, center_on_parent


class EditOfficeDialog(QDialog):
    """İdarə redaktə dialogu"""

    def __init__(self, parent, office_data):
        super().__init__(parent)
        self.setWindowTitle("İdarə redaktə")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._data = None
        self.office_data = office_data  # (id, name, address, region_name, region_kod, rayon_kod, phone, notes)

        self._setup_ui()
        center_on_parent(self, 500, 400, parent)

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Başlıq
        layout.addWidget(self._make_label(f"✏️ İdarə redaktə - ID {self.office_data[0]}", "title"))
        layout.addWidget(self._make_label("Məlumatları dəyişdirin", "muted"))

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # İdarə adı
        self.ent_name = QLineEdit(self.office_data[1])
        self.ent_name.setFixedHeight(36)
        form.addRow(self._make_label("İdarə adı:", bold=True), self.ent_name)

        # Region adı
        self.ent_region_name = QLineEdit(self.office_data[3] if self.office_data[3] else "")
        self.ent_region_name.setFixedHeight(36)
        form.addRow(self._make_label("Region adı:", bold=True), self.ent_region_name)

        # Region kodu
        region_kod_str = str(self.office_data[4]) if self.office_data[4] else ""
        self.ent_region_kod = QLineEdit(region_kod_str)
        self.ent_region_kod.setFixedHeight(36)
        form.addRow(self._make_label("Region kodu:", bold=True), self.ent_region_kod)

        # Rayon kodu
        rayon_kod_str = str(self.office_data[5]) if self.office_data[5] else ""
        self.ent_rayon_kod = QLineEdit(rayon_kod_str)
        self.ent_rayon_kod.setFixedHeight(36)
        form.addRow(self._make_label("Rayon kodu:", bold=True), self.ent_rayon_kod)

        # Ünvan
        self.ent_address = QLineEdit(self.office_data[2])
        self.ent_address.setFixedHeight(36)
        form.addRow(self._make_label("Ünvan:", bold=True), self.ent_address)

        # Telefon
        self.ent_phone = QLineEdit(self.office_data[6] if self.office_data[6] else "")
        self.ent_phone.setFixedHeight(36)
        form.addRow(self._make_label("Telefon:", bold=True), self.ent_phone)

        # Qeydlər
        self.ent_notes = QLineEdit(self.office_data[7] if self.office_data[7] else "")
        self.ent_notes.setFixedHeight(36)
        form.addRow(self._make_label("Qeydlər:", bold=True), self.ent_notes)

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

    def _save(self):
        """Dəyişiklikləri yadda saxla"""
        # Dəyərləri topla
        name = self.ent_name.text().strip()
        region_name = self.ent_region_name.text().strip()
        region_kod_text = self.ent_region_kod.text().strip()
        rayon_kod_text = self.ent_rayon_kod.text().strip()
        address = self.ent_address.text().strip()
        phone = self.ent_phone.text().strip()
        notes = self.ent_notes.text().strip()

        # Məcburi sahələri yoxla
        if not name:
            QMessageBox.warning(self, "Xəta", "İdarə adı daxil edin")
            return

        if not address:
            QMessageBox.warning(self, "Xəta", "Ünvan daxil edin")
            return

        # Kodları integer-ə çevir
        region_kod = None
        if region_kod_text:
            try:
                region_kod = int(region_kod_text)
            except ValueError:
                QMessageBox.warning(self, "Xəta", "Region kodu rəqəm olmalıdır")
                return

        rayon_kod = None
        if rayon_kod_text:
            try:
                rayon_kod = int(rayon_kod_text)
            except ValueError:
                QMessageBox.warning(self, "Xəta", "Rayon kodu rəqəm olmalıdır")
                return

        # Məlumatları topla
        self._data = {
            "id": self.office_data[0],
            "name": name,
            "region_name": region_name,
            "region_kod": region_kod,
            "rayon_kod": rayon_kod,
            "address": address,
            "phone": phone,
            "notes": notes
        }

        self.accept()

    def get_data(self) -> dict | None:
        """Daxil edilmiş məlumatları qaytar"""
        return self._data