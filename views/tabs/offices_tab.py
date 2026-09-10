"""
İdarələr tab-ı - Excel formatında cədvəl, telefon və qeydlərlə
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models.database import Database
from views.dialogs.ask_text import AskTextDialog
from views.dialogs.add_office import AddOfficeDialog
from views.dialogs.edit_office import EditOfficeDialog
from utils.permissions import can_edit, can_delete_lists, is_readonly
from utils.helpers import make_label, make_btn
import logging

logger = logging.getLogger('ui')

class OfficesTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.role = main_window.role
        self.username = main_window.username
        self.office_rows = []

        self._setup_ui()
        self._load_offices()

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Başlıq
        layout.addWidget(self._create_label("🏢 İdarələrin ünvanları", "title"))

        # Üst panel (düymələr və axtarış)
        top_panel = self._create_top_panel()
        layout.addLayout(top_panel)

        # Cədvəl
        self.table = self._create_table()
        layout.addWidget(self.table, stretch=1)

        # Alt əməliyyat düymələri (yalnız admin/bash üçün)
        if can_edit(self.role, self.username) or can_delete_lists(self.role, self.username):
            layout.addLayout(self._create_action_buttons())
        else:
            # Dispetçer üçün məlumat
            info_label = QLabel("👁 Siz yalnız baxış rejimindəsiniz")
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
            layout.addWidget(info_label)

    def _create_label(self, text, cls="", bold=False):
        """Label yarat (köməkçi metod)"""
        label = QLabel(text)
        if cls:
            label.setProperty("class", cls)
        if bold:
            font = label.font()
            font.setBold(True)
            label.setFont(font)
        return label

    def _create_top_panel(self):
        """Üst panel - düymələr və axtarış"""
        layout = QHBoxLayout()

        # "Yeni idarə" düyməsi - YALNIZ ADMIN/BASH
        if can_edit(self.role, self.username) or can_delete_lists(self.role, self.username):
            self.btn_add_office = QPushButton("➕ Yeni idarə")
            self.btn_add_office.setFixedHeight(34)
            self.btn_add_office.clicked.connect(self._add_office)
            layout.addWidget(self.btn_add_office)

        # Axtarış (hər kəs üçün)
        layout.addWidget(self._create_label("🔍 Axtarış:", bold=True))
        self.ent_office_search = QLineEdit()
        self.ent_office_search.setPlaceholderText("Ad, region, ünvan, telefon və ya qeydlərə görə axtar...")
        self.ent_office_search.setFixedHeight(34)
        self.ent_office_search.textChanged.connect(self._reload_offices_ui)
        layout.addWidget(self.ent_office_search, stretch=1)

        # Təmizlə düyməsi (hər kəs üçün)
        btn_clear = QPushButton("🗑️ Təmizlə")
        btn_clear.setFixedSize(100, 34)
        btn_clear.clicked.connect(self._clear_search)
        layout.addWidget(btn_clear)

        # Yenilə düyməsi (hər kəs üçün)
        btn_refresh = QPushButton("🔄 Yenilə")
        btn_refresh.setFixedSize(100, 34)
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        return layout

    def _create_action_buttons(self):
        """Əməliyyat düymələrini yarat"""
        layout = QHBoxLayout()

        self.btn_edit_office = make_btn("✏️ Dəyiş", "soft")
        self.btn_delete_office = make_btn("🗑️ Sil", "soft")

        for btn in (self.btn_edit_office, self.btn_delete_office):
            btn.setFixedHeight(34)
            layout.addWidget(btn)

        layout.addStretch()

        # Düymə vəziyyətləri
        self.btn_edit_office.setEnabled(can_edit(self.role, self.username))
        self.btn_delete_office.setEnabled(can_delete_lists(self.role, self.username))

        # Bağlantılar
        self.btn_edit_office.clicked.connect(self._edit_office)
        self.btn_delete_office.clicked.connect(self._delete_office)

        return layout

    def _create_table(self):
        """Excel formatında cədvəl yarat"""
        table = QTableWidget()

        # Sütunları təyin et
        columns = ["ID", "İdarə adı", "Region", "Region kod", "Rayon kod", "Ünvan", "Telefon", "Qeydlər"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Cədvəl xüsusiyyətləri
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        # Sütun genişlikləri
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # İdarə adı
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Region
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Region kod
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Rayon kod
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Ünvan
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Telefon
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Qeydlər

        # Dispetçer üçün ID sütununu gizlət
        if self.role == "dispetcer":
            table.setColumnHidden(0, True)

        # Cədvəl seçim hadisəsini bağla (yalnız admin/bash üçün)
        if can_edit(self.role, self.username) or can_delete_lists(self.role, self.username):
            table.itemSelectionChanged.connect(self._on_table_select)

        return table

    def _clear_search(self):
        """Axtarış sahəsini təmizlə"""
        self.ent_office_search.clear()

    def _load_offices(self):
        """İdarələri yüklə"""
        try:
            db = Database()
            rows = db.execute(
                """SELECT id, name, address, region_name, region_kod, rayon_kod, phone, notes 
                   FROM offices ORDER BY name""",
                fetchall=True
            )
            self.office_rows = rows
        except Exception as e:
            logger.error(f"İdarə yükləmə xətası: {e}")
            self.office_rows = []

    def _get_filtered_offices(self):
        """Axtarışa uyğun idarələri qaytar"""
        search_text = self.ent_office_search.text().strip().lower() if hasattr(self, 'ent_office_search') else ""

        filtered = []
        for row in self.office_rows:
            # row: (id, name, address, region_name, region_kod, rayon_kod, phone, notes)
            if len(row) >= 8:
                oid, name, address, region_name, region_kod, rayon_kod, phone, notes = row[:8]
            else:
                continue

            # Axtarış üçün bütün sahələri birləşdir
            region_name_str = region_name if region_name else ""
            region_kod_str = str(region_kod) if region_kod else ""
            rayon_kod_str = str(rayon_kod) if rayon_kod else ""
            phone_str = phone if phone else ""
            notes_str = notes if notes else ""

            searchable = f"{name} {address} {region_name_str} {region_kod_str} {rayon_kod_str} {phone_str} {notes_str}".lower()

            if not search_text or search_text in searchable:
                filtered.append((oid, name, address, region_name, region_kod, rayon_kod, phone, notes))

        return filtered

    def _reload_offices_ui(self):
        """Cədvəli məlumatlarla doldur"""
        if not hasattr(self, 'table'):
            return

        self._load_offices()
        filtered = self._get_filtered_offices()

        # Cədvəli təmizlə və yenidən qur
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered))

        for i, row_data in enumerate(filtered):
            oid, name, address, region_name, region_kod, rayon_kod, phone, notes = row_data

            # Sətir məlumatları
            row_values = [
                str(oid),
                name,
                region_name if region_name else "",
                str(region_kod) if region_kod else "",
                str(rayon_kod) if rayon_kod else "",
                address,
                phone if phone else "",
                notes if notes else ""
            ]

            for j, value in enumerate(row_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)

            self.table.setRowHeight(i, 30)

        self.table.setSortingEnabled(True)
        logger.debug(f"{len(filtered)} idarə göstərildi")

    def _get_selected_row_data(self):
        """Seçilmiş sətirin məlumatlarını qaytar"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None

        # Filterlənmiş siyahıdan sətiri tap
        filtered = self._get_filtered_offices()
        if current_row < len(filtered):
            return filtered[current_row]
        return None

    def _on_table_select(self):
        """Cədvəldə sətir seçildikdə - redaktə üçün"""
        # Bu metod boş ola bilər və ya seçilmiş sətiri qeyd edə bilər
        pass

    def _add_office(self):
        """Yeni idarə əlavə et (dialog ilə)"""
        if not can_edit(self.role, self.username):
            return

        dlg = AddOfficeDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        if not data:
            return

        try:
            db = Database()
            db.execute(
                """INSERT INTO offices 
                   (name, address, region_name, region_kod, rayon_kod, phone, notes) 
                   VALUES (?,?,?,?,?,?,?)""",
                (data["name"], data["address"],
                 data["region_name"] if data["region_name"] else None,
                 data["region_kod"], data["rayon_kod"],
                 data["phone"] if data["phone"] else None,
                 data["notes"] if data["notes"] else None)
            )

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._reload_offices_ui()

            logger.info(f"Yeni idarə əlavə edildi: {data['name']}")

        except Exception as e:
            logger.error(f"İdarə əlavə etmə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                f"Bu adla idarə artıq mövcuddur: {str(e)}"
            )

    def _edit_office(self):
        """İdarə redaktə et (dialog ilə)"""
        if not can_edit(self.role, self.username):
            return

        row_data = self._get_selected_row_data()
        if not row_data:
            QMessageBox.information(
                self,
                "Məlumat",
                "Zəhmət olmasa bir sətir seçin."
            )
            return

        dlg = EditOfficeDialog(self, row_data)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        if not data:
            return

        try:
            db = Database()
            db.execute(
                """UPDATE offices SET 
                   name=?, address=?, region_name=?, region_kod=?, rayon_kod=?, phone=?, notes=? 
                   WHERE id=?""",
                (data["name"], data["address"],
                 data["region_name"] if data["region_name"] else None,
                 data["region_kod"], data["rayon_kod"],
                 data["phone"] if data["phone"] else None,
                 data["notes"] if data["notes"] else None,
                 data["id"])
            )

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._reload_offices_ui()

            logger.info(f"İdarə redaktə edildi: {data['name']}")

        except Exception as e:
            logger.error(f"İdarə redaktə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                f"Dəyişiklik edilə bilmədi: {str(e)}"
            )

    def _delete_office(self):
        """İdarəni sil"""
        if not can_delete_lists(self.role, self.username):
            return

        row_data = self._get_selected_row_data()
        if not row_data:
            QMessageBox.information(
                self,
                "Məlumat",
                "Zəhmət olmasa bir sətir seçin."
            )
            return

        oid, name, _, _, _, _, _, _ = row_data

        reply = QMessageBox.question(
            self,
            "Təsdiq",
            f"'{name}' idarəsini silmək istəyirsiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            db = Database()
            db.execute("DELETE FROM offices WHERE id=?", (oid,))

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._reload_offices_ui()

            logger.info(f"İdarə silindi: {name}")

        except Exception as e:
            logger.error(f"İdarə silmə xətası: {e}")
            QMessageBox.warning(self, "Xəta", str(e))

    def refresh(self):
        """Cədvəli yenilə"""
        self._reload_offices_ui()