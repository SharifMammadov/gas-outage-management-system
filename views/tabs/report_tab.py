"""
Hesabat tab-ı
"""
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

from models.database import Database
from utils.theme import C_ACCENT, ROW_CLOSED
from utils.helpers import make_label
from utils.date_utils import (
    today_date_str, date_str, is_valid_date_ddmmyyyy,
    ddmmyyyy_to_iso, fmt_int
)
import logging

logger = logging.getLogger('ui')

class ReportTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()

        # İlk hesabatı yüklə
        self._update_report()

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Başlıq
        layout.addWidget(self._make_label("📊 Bağlantı Hesabatı", "title"))
        layout.addWidget(self._make_label(
            "Tarix aralığı üzrə cəmlər",
            "muted"
        ))

        # Tarix aralığı paneli
        layout.addWidget(self._create_date_range_frame())

        # KPI kartları
        layout.addLayout(self._create_kpi_cards())

        # Cədvəl başlığı
        layout.addWidget(self._make_label("Tarixlər üzrə cəm", "section"))

        # Cədvəl
        self.table = self._create_table()
        layout.addWidget(self.table, stretch=1)

        # Qeyd
        layout.addWidget(self._make_label(
            "Qeyd: Qalıq = həmin tarixdə bağlanıb, hələ Bağlı qalan abonentlər.",
            "muted"
        ))

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

    def _create_date_range_frame(self):
        """Tarix aralığı paneli yarat"""
        frame = QFrame()
        frame.setProperty("class", "card")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Başlanğıc tarix
        layout.addWidget(self._make_label("Başlanğıc:", bold=True))
        self.ent_date_from = QLineEdit(today_date_str())
        self.ent_date_from.setFixedWidth(110)
        self.ent_date_from.setFixedHeight(34)
        layout.addWidget(self.ent_date_from)

        # Bitiş tarix
        layout.addWidget(self._make_label("Bitiş:", bold=True))
        self.ent_date_to = QLineEdit(today_date_str())
        self.ent_date_to.setFixedWidth(110)
        self.ent_date_to.setFixedHeight(34)
        layout.addWidget(self.ent_date_to)

        # Bu gün düyməsi
        btn_today = QPushButton("📅 Bu gün")
        btn_today.setFixedHeight(34)
        btn_today.clicked.connect(self._set_today_range)
        layout.addWidget(btn_today)

        # Dünən düyməsi
        btn_yesterday = QPushButton("📅 Dünən")
        btn_yesterday.setFixedHeight(34)
        btn_yesterday.clicked.connect(self._set_yesterday_range)
        layout.addWidget(btn_yesterday)

        layout.addStretch()

        # Hesabla düyməsi
        btn_calc = QPushButton("🔍 Hesabla")
        btn_calc.setFixedHeight(34)
        btn_calc.clicked.connect(self._update_report)
        layout.addWidget(btn_calc)

        return frame

    def _create_kpi_cards(self):
        """KPI kartları yarat"""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Cəmi bağlantı
        self.kpi_total = self._create_kpi_card(
            "📊 Cəmi bağlantı",
            "0",
            layout
        )

        # Cəmi açılma
        self.kpi_opened = self._create_kpi_card(
            "🔓 Cəmi açılma",
            "0",
            layout
        )

        # Qalıq bağlantı
        self.kpi_remaining = self._create_kpi_card(
            "🔒 Qalıq bağlantı",
            "0",
            layout
        )

        return layout

    def _create_kpi_card(self, title, value, parent_layout):
        """KPI kartı yarat"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C_ACCENT};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        # Başlıq
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "color: #a8c4e0; font-size: 9pt; font-weight: bold; background: transparent;"
        )

        # Dəyər
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(
            "color: white; font-size: 22pt; font-weight: bold; background: transparent;"
        )
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)

        parent_layout.addWidget(frame)
        return lbl_value

    def _create_table(self):
        """Hesabat cədvəli yarat"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "📅 Tarix",
            "🔒 Bağlı",
            "🔓 Açıq",
            "⏸️ Stop",
            "📊 Cəmi"
        ])

        # Cədvəl xüsusiyyətləri
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)

        # Sütun genişlikləri
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        return table

    def _set_today_range(self):
        """Bu gün üçün tarix aralığı təyin et"""
        today = today_date_str()
        self.ent_date_from.setText(today)
        self.ent_date_to.setText(today)
        self._update_report()

    def _set_yesterday_range(self):
        """Dünən üçün tarix aralığı təyin et"""
        yesterday = date_str(datetime.now() - timedelta(days=1))
        self.ent_date_from.setText(yesterday)
        self.ent_date_to.setText(yesterday)
        self._update_report()

    def _update_report(self):
        """Hesabatı yenilə"""
        d1 = self.ent_date_from.text().strip()
        d2 = self.ent_date_to.text().strip()

        # Tarix formatını yoxla
        if not is_valid_date_ddmmyyyy(d1) or not is_valid_date_ddmmyyyy(d2):
            return

        iso1 = ddmmyyyy_to_iso(d1)
        iso2 = ddmmyyyy_to_iso(d2)

        # SQL date çevirmə
        closed_iso = (
            "(substr(closed_at,7,4)||'-'||substr(closed_at,4,2)"
            "||'-'||substr(closed_at,1,2))"
        )

        try:
            db = Database()

            # Ümumi cəmi hesabla
            row = db.execute(f"""
                SELECT COALESCE(SUM(abonent_count), 0) FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
            """, (iso1, iso2), fetchone=True)
            total = int(row[0] or 0)

            # Statuslara görə cəmi
            rows = db.execute(f"""
                SELECT status, COALESCE(SUM(abonent_count), 0) FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
                GROUP BY status
            """, (iso1, iso2), fetchall=True)

            by_status = {"Bağlı": 0, "Açıq": 0, "Stop": 0}
            for status, total_count in rows:
                if status in by_status:
                    by_status[status] = int(total_count or 0)

            # KPI-ları yenilə
            self.kpi_total.setText(fmt_int(total))
            self.kpi_opened.setText(fmt_int(by_status["Açıq"]))
            self.kpi_remaining.setText(fmt_int(by_status["Bağlı"]))

            # Günlük məlumatları topla
            rows = db.execute(f"""
                SELECT substr(closed_at, 1, 10) AS tarix,
                       TRIM(status),
                       COALESCE(SUM(abonent_count), 0)
                FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
                GROUP BY tarix, TRIM(status)
                ORDER BY {closed_iso}
            """, (iso1, iso2), fetchall=True)

            # Günlük məlumatları təşkil et
            daily = {}
            for tarix, status, count in rows:
                if tarix not in daily:
                    daily[tarix] = {"Bağlı": 0, "Açıq": 0, "Stop": 0}
                if status in ("Bağlı", "Açıq", "Stop"):
                    daily[tarix][status] += int(count or 0)

            # Cədvəli yenilə
            self._update_table(daily)

            logger.info(f"Hesabat yeniləndi: {d1} - {d2}")

        except Exception as e:
            logger.error(f"Hesabat xətası: {e}")

    def _update_table(self, daily_data):
        """Cədvəli məlumatlarla doldur"""
        self.table.setRowCount(len(daily_data))

        for i, tarix in enumerate(sorted(daily_data.keys(), reverse=True)):
            bagli = daily_data[tarix]["Bağlı"]
            aciq = daily_data[tarix]["Açıq"]
            stop = daily_data[tarix]["Stop"]
            total = bagli + aciq + stop

            # Sətir məlumatları
            row_data = [
                tarix,
                fmt_int(bagli),
                fmt_int(aciq),
                fmt_int(stop),
                fmt_int(total)
            ]

            for j, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Rəngləmə
                if bagli > 0:
                    item.setBackground(QBrush(QColor(ROW_CLOSED)))

                self.table.setItem(i, j, item)

            self.table.setRowHeight(i, 32)

    def refresh(self):
        """Hesabatı yenilə"""
        self._update_report()