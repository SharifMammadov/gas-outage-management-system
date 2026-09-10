"""
Bağlantılar tab-ı
"""
"""
Bağlantılar tab-ı
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QDialog  # <-- QDialog burada əlavə edildi
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QColor

from models.database import Database
from models.record import Record
from models.cache import Cache
from views.dialogs.add_record import AddRecordDialog
from views.dialogs.edit_record import EditRecordDialog
from views.dialogs.status_dialog import StatusDialog
from utils.permissions import can_edit, can_delete
from utils.theme import ROW_CLOSED, ROW_OPEN, ROW_STOP
from utils.helpers import make_label, make_btn
from utils.i18n import t
from utils.date_utils import (  # <-- date_utils əlavə edildi
    today_date_str, default_time_str, date_str,
    make_dt_str, is_valid_date_ddmmyyyy,
    ddmmyyyy_to_iso, fmt_int, time_choices
)
import config
import logging

logger = logging.getLogger('ui')
class RecordsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.role = main_window.role
        self.username = main_window.username
        self.cache = Cache()

        self.rayon_values = []
        self.reason_values = []

        self._setup_ui()
        self._load_lists()

        # Debounce timer
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(config.Config.DEBOUNCE_INTERVAL)
        self._debounce.timeout.connect(self._load_records)

        # İlk yükləmə
        QTimer.singleShot(150, self._load_records)

    def _setup_ui(self):
        """İnterfeysi qur - dispetçer üçün read-only"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Filter paneli (hər kəs görür)
        layout.addWidget(self._create_filter_bar())

        # Cədvəl (hər kəs görür)
        self.table = self._create_table()
        layout.addWidget(self.table, stretch=1)

        # Əməliyyat paneli - YALNIZ ADMIN/BASH ÜÇÜN
        if can_edit(self.role, self.username) or can_delete(self.role, self.username):
            layout.addLayout(self._create_action_bar())
        else:
            # Dispetçer üçün sadəcə məlumat
            info_label = QLabel("👁 Siz yalnız baxış rejimindəsiniz")
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
            layout.addWidget(info_label)

    def _create_filter_bar(self):
        """Filter paneli yarat"""
        frame = QFrame()
        frame.setProperty("class", "filter-bar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # Rayon filter
        layout.addWidget(make_label("Rayon:", bold=True))
        self.txt_rayon_filter = QLineEdit()
        self.txt_rayon_filter.setPlaceholderText("Axtar...")
        self.txt_rayon_filter.setFixedWidth(200)
        self.txt_rayon_filter.setFixedHeight(34)
        self.txt_rayon_filter.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.txt_rayon_filter)

        # Status filter
        layout.addWidget(make_label("Status:", bold=True))
        self.cb_status_filter = QComboBox()
        for status in config.Config.STATUS_FILTERS:
            self.cb_status_filter.addItem(t(status), status)
        self.cb_status_filter.setFixedWidth(130)
        self.cb_status_filter.setFixedHeight(34)
        self.cb_status_filter.currentIndexChanged.connect(self._load_records)
        layout.addWidget(self.cb_status_filter)

        layout.addStretch()

        # Yeni bağlantı düyməsi
        if can_edit(self.role, self.username):
            btn_new = QPushButton("➕ Yeni bağlantı")
            btn_new.setFixedHeight(34)
            btn_new.clicked.connect(self._add_record)
            layout.addWidget(btn_new)

        # Yenilə düyməsi
        btn_refresh = make_btn("🔄 Yenilə", "soft")
        btn_refresh.setFixedHeight(34)
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        return frame

    def _create_table(self):
        """Cədvəl yarat"""
        table = QTableWidget()
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "ID", "Rayon", "Küçə", "Bağlanma səbəbi",
            "Abonent sayı", "Kateqoriya", "Diametr",
            "Bağlandı", "Açıldı", "Status"
        ])

        # Cədvəl xüsusiyyətləri
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setSortingEnabled(True)

        # Sütun genişlikləri
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Rayon
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Küçə
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Səbəb

        for col in range(4, 10):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        # Dispetçer üçün ID sütununu gizlət
        if self.role == "dispetcer":
            table.setColumnHidden(0, True)

        return table

    def _create_action_bar(self):
        """Əməliyyat paneli yarat"""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Düymələr
        self.btn_toggle = QPushButton("🔀 Status dəyiş")
        self.btn_edit = make_btn("✏️ Redaktə", "soft")
        self.btn_delete = make_btn("🗑️ Sil", "soft")

        for btn in (self.btn_toggle, self.btn_edit, self.btn_delete):
            btn.setFixedHeight(36)
            layout.addWidget(btn)

        layout.addStretch()
        layout.addWidget(
            make_label("👉 Sətiri seçin → əməliyyat edin.", cls="muted")
        )

        # Düymə vəziyyətləri
        if self.role == "dispetcer":
            self.btn_toggle.setEnabled(False)
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
        else:
            self.btn_toggle.setEnabled(can_edit(self.role, self.username))
            self.btn_edit.setEnabled(can_edit(self.role, self.username))
            self.btn_delete.setEnabled(can_delete(self.role, self.username))

        # Bağlantılar
        self.btn_toggle.clicked.connect(self._toggle_status)
        self.btn_edit.clicked.connect(self._edit_selected)
        self.btn_delete.clicked.connect(self._delete_selected)

        return layout

    def _on_filter_changed(self):
        """Filter dəyişəndə debounce işə sal"""
        self._debounce.start()

    def _load_lists(self):
        """Rayon və səbəb siyahılarını yüklə"""
        cache_key = 'lists_data'
        cached = self.cache.get(cache_key)

        if cached:
            self.rayon_values, self.reason_values = cached
            return

        try:
            db = Database()
            rows = db.execute(
                "SELECT name FROM rayons ORDER BY name",
                fetchall=True
            )
            self.rayon_values = [r[0] for r in rows]

            rows = db.execute(
                "SELECT name FROM reasons ORDER BY name",
                fetchall=True
            )
            self.reason_values = [r[0] for r in rows]

            self.cache.set(cache_key, (self.rayon_values, self.reason_values))

        except Exception as e:
            logger.error(f"Siyahı yükləmə xətası: {e}")

    def _load_records(self):
        """Bağlantıları yüklə"""
        rayon_filter = self.txt_rayon_filter.text().strip()
        status_filter = self.cb_status_filter.currentData()

        try:
            records = Record.get_all(rayon_filter, status_filter)

            # Cari tema rənglərini al
            from utils.theme import get_colors
            colors = get_colors()

            # Cədvəli yenilə
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(records))

            for i, record in enumerate(records):
                status = record.status

                # Sətir fon rəngi
                if status == "Açıq":
                    bg_color = QColor(colors['ROW_OPEN'])
                    text_color = QColor(colors['ROW_OPEN_TEXT'])
                elif status == "Stop":
                    bg_color = QColor(colors['ROW_STOP'])
                    text_color = QColor(colors['ROW_STOP_TEXT'])
                else:  # Bağlı
                    bg_color = QColor(colors['ROW_CLOSED'])
                    text_color = QColor(colors['ROW_CLOSED_TEXT'])

                row_data = [
                    str(record.id),
                    record.rayon or "",
                    record.küçə or "",
                    record.reason or "",
                    str(record.abonent_count or 0),
                    record.category or "",
                    str(record.pipe_mm or ""),
                    record.closed_at or "",
                    record.opened_at or "",
                    t(record.status or "")
                ]

                for j, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    if j == 9:
                        item.setData(Qt.ItemDataRole.UserRole, record.status)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(QBrush(bg_color))
                    item.setForeground(QBrush(text_color))  # Mətn rəngi
                    self.table.setItem(i, j, item)

                self.table.setRowHeight(i, 32)

            self.table.setSortingEnabled(True)
            logger.debug(f"{len(records)} bağlantı yükləndi")

        except Exception as e:
            logger.error(f"Bağlantı yükləmə xətası: {e}")

    def refresh(self):
        """Məlumatları yenilə"""
        self._load_lists()
        self._load_records()

    def _add_record(self):
        """Yeni bağlantı əlavə et"""
        if not can_edit(self.role, self.username):
            return

        self._load_lists()
        dlg = AddRecordDialog(self, self.rayon_values, self.reason_values)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        if not data:
            return

        try:
            # Yeni record yarat
            record = Record(
                rayon=data["rayon"],
                küçə=data["küçə"],
                reason=data["reason"],
                abonent_count=data["abonent_count"],
                category=data["category"],
                pipe_mm=data["pipe_mm"],
                closed_at=data["closed_at"],
                status="Bağlı"
            )
            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._load_records()

            logger.info(f"Yeni bağlantı əlavə edildi: {record.rayon}")

        except Exception as e:
            logger.error(f"Bağlantı əlavə etmə xətası: {e}")
            QMessageBox.critical(self, "Xəta", str(e))

    def _toggle_status(self):
        """Status dəyiş"""
        if not can_edit(self.role, self.username):
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "Məlumat",
                "Zəhmət olmasa bir sətir seçin."
            )
            return

        # ID-ni əldə et
        id_item = self.table.item(row, 0)
        if not id_item or not id_item.text():
            return

        record_id = int(id_item.text())
        status_item = self.table.item(row, 9)
        current_status = status_item.data(Qt.ItemDataRole.UserRole) or status_item.text()

        # Status dialogu
        dlg = StatusDialog(self, current_status)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        result = dlg.get_data()
        if not result:
            return

        new_status, dt_val = result

        try:
            record = Record.get_by_id(record_id)
            if not record:
                return

            # Status-u yenilə
            if new_status == "Açıq":
                record.status = "Açıq"
                record.opened_at = dt_val
            elif new_status == "Bağlı":
                record.status = "Bağlı"
                record.closed_at = dt_val
                record.opened_at = ""  # Açılış tarixini təmizlə
            else:  # Stop
                record.status = "Stop"

            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._load_records()

            logger.info(f"Status dəyişdirildi: {record_id} -> {new_status}")

        except Exception as e:
            logger.error(f"Status dəyişmə xətası: {e}")
            QMessageBox.critical(self, "Xəta", str(e))

    def _edit_selected(self):
        """Seçilmiş bağlantını redaktə et"""
        if not can_edit(self.role, self.username):
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "Məlumat",
                "Zəhmət olmasa bir sətir seçin."
            )
            return

        # Mövcud dəyərləri topla
        values = []
        for j in range(10):
            item = self.table.item(row, j)
            values.append(item.text() if item else "")

        # Redaktə dialogu
        dlg = EditRecordDialog(self, values)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        if not data:
            return

        try:
            record = Record.get_by_id(int(values[0]))
            if not record:
                return

            # Məlumatları yenilə
            record.rayon = data["rayon"]
            record.küçə = data["küçə"]
            record.reason = data["reason"]
            record.abonent_count = data["abonent_count"]
            record.category = data["category"]
            record.pipe_mm = data["pipe_mm"]

            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._load_records()

            logger.info(f"Bağlantı redaktə edildi: {values[0]}")

        except Exception as e:
            logger.error(f"Redaktə xətası: {e}")
            QMessageBox.critical(self, "Xəta", str(e))

    def _delete_selected(self):
        """Seçilmiş bağlantını sil"""
        if not can_delete(self.role, self.username):
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "Məlumat",
                "Zəhmət olmasa bir sətir seçin."
            )
            return

        # ID-ni əldə et
        id_item = self.table.item(row, 0)
        if not id_item or not id_item.text():
            return

        record_id = int(id_item.text())

        # Təsdiq sorğusu
        reply = QMessageBox.question(
            self, "Təsdiq",
            f"ID {record_id} sətrini silmək istəyirsiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            record = Record.get_by_id(record_id)
            if record:
                record.delete()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            # Backup yarat
            self.main_window.backup_database()

            # Cədvəli yenilə
            self._load_records()

            logger.info(f"Bağlantı silindi: {record_id}")

        except Exception as e:
            logger.error(f"Silme xətası: {e}")
            QMessageBox.critical(self, "Xəta", str(e))
