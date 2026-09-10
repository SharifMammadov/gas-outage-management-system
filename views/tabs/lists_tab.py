"""
Rayon və səbəblər tab-ı
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QMessageBox, QDialog
)

from models.database import Database
from models.cache import Cache
from views.dialogs.ask_text import AskTextDialog
from utils.permissions import can_edit, can_delete_lists
from utils.helpers import make_label, make_btn
import logging

logger = logging.getLogger('ui')


class ListsTab(QWidget):
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

    def _setup_ui(self):
        """İnterfeysi qur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Rayonlar paneli
        layout.addWidget(self._create_rayon_panel())

        # Səbəblər paneli
        layout.addWidget(self._create_reason_panel())

    def _create_rayon_panel(self):
        """Rayonlar paneli yarat"""
        frame = QFrame()
        frame.setProperty("class", "card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Başlıq
        layout.addWidget(make_label("🏙️ Rayonlar", cls="section"))

        # Siyahı
        self.rayon_list = QListWidget()
        self.rayon_list.setAlternatingRowColors(True)
        layout.addWidget(self.rayon_list, stretch=1)

        # Düymələr
        btn_layout = QHBoxLayout()

        btn_add = QPushButton("➕ Əlavə et")
        btn_rename = make_btn("✏️ Dəyiş", "soft")
        btn_delete = make_btn("🗑️ Sil", "soft")

        for btn in (btn_add, btn_rename, btn_delete):
            btn.setFixedHeight(34)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # Düymə vəziyyətləri
        btn_add.setEnabled(can_edit(self.role, self.username))
        btn_rename.setEnabled(can_edit(self.role, self.username))
        btn_delete.setEnabled(can_delete_lists(self.role, self.username))

        # Bağlantılar
        btn_add.clicked.connect(self._add_rayon)
        btn_rename.clicked.connect(self._rename_rayon)
        btn_delete.clicked.connect(self._delete_rayon)

        return frame

    def _create_reason_panel(self):
        """Səbəblər paneli yarat"""
        frame = QFrame()
        frame.setProperty("class", "card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Başlıq
        layout.addWidget(make_label("📝 Bağlanma səbəbləri", cls="section"))

        # Siyahı
        self.reason_list = QListWidget()
        self.reason_list.setAlternatingRowColors(True)
        layout.addWidget(self.reason_list, stretch=1)

        # Düymələr
        btn_layout = QHBoxLayout()

        btn_add = QPushButton("➕ Əlavə et")
        btn_rename = make_btn("✏️ Dəyiş", "soft")
        btn_delete = make_btn("🗑️ Sil", "soft")

        for btn in (btn_add, btn_rename, btn_delete):
            btn.setFixedHeight(34)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # Düymə vəziyyətləri
        btn_add.setEnabled(can_edit(self.role, self.username))
        btn_rename.setEnabled(can_edit(self.role, self.username))
        btn_delete.setEnabled(can_delete_lists(self.role, self.username))

        # Bağlantılar
        btn_add.clicked.connect(self._add_reason)
        btn_rename.clicked.connect(self._rename_reason)
        btn_delete.clicked.connect(self._delete_reason)

        return frame

    def _load_lists(self):
        """Siyahıları yüklə"""
        cache_key = 'lists_data'
        cached = self.cache.get(cache_key)

        if cached:
            self.rayon_values, self.reason_values = cached
            self._update_lists_ui()
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
            self._update_lists_ui()

        except Exception as e:
            logger.error(f"Siyahı yükləmə xətası: {e}")

    def _update_lists_ui(self):
        """UI-də siyahıları yenilə"""
        # Rayon siyahısı
        self.rayon_list.clear()
        for rayon in self.rayon_values:
            item = QListWidgetItem(rayon)
            self.rayon_list.addItem(item)

        # Səbəb siyahısı
        self.reason_list.clear()
        for reason in self.reason_values:
            item = QListWidgetItem(reason)
            self.reason_list.addItem(item)

    def _add_rayon(self):
        """Yeni rayon əlavə et"""
        if not can_edit(self.role, self.username):
            return

        name = AskTextDialog.get_text(
            self,
            "Rayon əlavə et",
            "Rayon adı:"
        )

        if not name:
            return

        try:
            db = Database()
            db.execute(
                "INSERT INTO rayons(name) VALUES(?)",
                (name,)
            )

            # Keşi təmizlə
            self.cache.clear('lists_data')

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()

            logger.info(f"Yeni rayon əlavə edildi: {name}")

        except Exception as e:
            logger.error(f"Rayon əlavə etmə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                "Bu rayon artıq mövcuddur."
            )

    def _rename_rayon(self):
        """Rayon adını dəyiş"""
        if not can_edit(self.role, self.username):
            return

        item = self.rayon_list.currentItem()
        if not item:
            return

        old_name = item.text()
        new_name = AskTextDialog.get_text(
            self,
            "Rayon dəyiş",
            "Yeni rayon adı:",
            old_name
        )

        if not new_name or new_name == old_name:
            return

        try:
            db = Database()

            # Rayonlar cədvəlində yenilə
            db.execute(
                "UPDATE rayons SET name=? WHERE name=?",
                (new_name, old_name)
            )

            # Records cədvəlində yenilə
            db.execute(
                "UPDATE records SET rayon=? WHERE rayon=?",
                (new_name, old_name)
            )

            # Keşi təmizlə
            self.cache.clear('lists_data')
            self.cache.clear_record_cache()

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()
                self.main_window.records_tab.refresh()

            logger.info(f"Rayon adı dəyişdirildi: {old_name} -> {new_name}")

        except Exception as e:
            logger.error(f"Rayon dəyişmə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                "Bu adla rayon artıq mövcuddur."
            )

    def _delete_rayon(self):
        """Rayon sil"""
        if not can_delete_lists(self.role, self.username):
            return

        item = self.rayon_list.currentItem()
        if not item:
            return

        name = item.text()

        reply = QMessageBox.question(
            self,
            "Təsdiq",
            f"'{name}' rayonunu silmək istəyirsiniz?\n"
            "Bu rayonla bağlı bütün bağlantılar təsirlənəcək!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            db = Database()
            db.execute("DELETE FROM rayons WHERE name=?", (name,))

            # Keşi təmizlə
            self.cache.clear('lists_data')

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()

            logger.info(f"Rayon silindi: {name}")

        except Exception as e:
            logger.error(f"Rayon silmə xətası: {e}")
            QMessageBox.warning(self, "Xəta", str(e))

    def _add_reason(self):
        if not can_edit(self.role, self.username):
            return

        """Yeni səbəb əlavə et"""
        name = AskTextDialog.get_text(
            self,
            "Səbəb əlavə et",
            "Bağlanma səbəbi:"
        )

        if not name:
            return

        try:
            db = Database()
            db.execute(
                "INSERT INTO reasons(name) VALUES(?)",
                (name,)
            )

            # Keşi təmizlə
            self.cache.clear('lists_data')

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()

            logger.info(f"Yeni səbəb əlavə edildi: {name}")

        except Exception as e:
            logger.error(f"Səbəb əlavə etmə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                "Bu səbəb artıq mövcuddur."
            )

    def _rename_reason(self):
        if not can_edit(self.role, self.username):
            return

        """Səbəb adını dəyiş"""
        item = self.reason_list.currentItem()
        if not item:
            return

        old_name = item.text()
        new_name = AskTextDialog.get_text(
            self,
            "Səbəb dəyiş",
            "Yeni səbəb adı:",
            old_name
        )

        if not new_name or new_name == old_name:
            return

        try:
            db = Database()

            # Səbəblər cədvəlində yenilə
            db.execute(
                "UPDATE reasons SET name=? WHERE name=?",
                (new_name, old_name)
            )

            # Records cədvəlində yenilə
            db.execute(
                "UPDATE records SET reason=? WHERE reason=?",
                (new_name, old_name)
            )

            # Keşi təmizlə
            self.cache.clear('lists_data')
            self.cache.clear_record_cache()

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()
                self.main_window.records_tab.refresh()

            logger.info(f"Səbəb adı dəyişdirildi: {old_name} -> {new_name}")

        except Exception as e:
            logger.error(f"Səbəb dəyişmə xətası: {e}")
            QMessageBox.warning(
                self,
                "Xəta",
                "Bu adla səbəb artıq mövcuddur."
            )

    def _delete_reason(self):
        """Səbəb sil"""
        if not can_delete_lists(self.role, self.username):
            return

        item = self.reason_list.currentItem()
        if not item:
            return

        name = item.text()

        reply = QMessageBox.question(
            self,
            "Təsdiq",
            f"'{name}' səbəbini silmək istəyirsiniz?\n"
            "Bu səbəblə bağlı bütün bağlantılar təsirlənəcək!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            db = Database()
            db.execute("DELETE FROM reasons WHERE name=?", (name,))

            # Keşi təmizlə
            self.cache.clear('lists_data')

            # Siyahıları yenilə
            self._load_lists()

            # Records tab-ı yenilə
            if hasattr(self.main_window, 'records_tab'):
                self.main_window.records_tab._load_lists()

            logger.info(f"Səbəb silindi: {name}")

        except Exception as e:
            logger.error(f"Səbəb silmə xətası: {e}")
            QMessageBox.warning(self, "Xəta", str(e))