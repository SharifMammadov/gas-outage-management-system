"""Lightweight Azerbaijani/English internationalization for the PyQt UI."""

import configparser
import re

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTabWidget,
    QTableWidget,
    QWidget,
)

from config import Config


TRANSLATIONS = {
    "Qaz Bağlantıları - Giriş": "Gas Outage Management - Sign In",
    "Qaz Bağlantıları": "Gas Outage Management",
    "Qaz Bağlantıları İdarəetmə Sistemi": "Gas Outage Management System",
    "Sistemə daxil olun": "Sign in to the system",
    "Dil:": "Language:",
    "İstifadəçi adı": "Username",
    "İstifadəçi adı:": "Username:",
    "istifadəçi adı": "username",
    "Şifrə": "Password",
    "Daxil ol": "Sign in",
    "Xəta": "Error",
    "Məlumat": "Information",
    "Təsdiq": "Confirmation",
    "İcazə yoxdur": "Permission denied",
    "İstifadəçi adı və şifrəni daxil edin.": "Enter your username and password.",
    "Login və ya şifrə yanlışdır.": "The username or password is incorrect.",
    "Backup yaratmaq icazəniz yoxdur.": "You do not have permission to create a backup.",
    "Backup yaradıla bilmədi!": "The backup could not be created.",
    "🌓 Tema": "🌓 Theme",
    "☀️ Açıq": "☀️ Light",
    "🌙 Tünd": "🌙 Dark",
    "🔄 Yenilə": "🔄 Refresh",
    "Son yenilənmə: -": "Last refresh: -",
    "Son yenilənmə:": "Last refresh:",
    "📋 Bağlantılar": "📋 Outages",
    "📊 Hesabat": "📊 Reports",
    "📝 Rayon və səbəblər": "📝 Districts and reasons",
    "🏢 İdarələr": "🏢 Offices",
    "👁 Siz yalnız baxış rejimindəsiniz": "👁 You are in read-only mode",
    "Rayon:": "District:",
    "Rayon": "District",
    "Axtar...": "Search...",
    "Status:": "Status:",
    "➕ Yeni bağlantı": "➕ New outage",
    "🔀 Status dəyiş": "🔀 Change status",
    "✏️ Redaktə": "✏️ Edit",
    "✏️ Dəyiş": "✏️ Rename",
    "🗑️ Sil": "🗑️ Delete",
    "👉 Sətiri seçin → əməliyyat edin.": "👉 Select a row, then choose an action.",
    "ID": "ID",
    "Küçə": "Street",
    "Bağlanma səbəbi": "Outage reason",
    "Abonent sayı": "Affected customers",
    "Kateqoriya": "Category",
    "Diametr": "Diameter",
    "Bağlandı": "Interrupted at",
    "Açıldı": "Restored at",
    "Bağlı": "Closed",
    "Açıq": "Restored",
    "Stop": "Stopped",
    "Hamısı": "All",
    "admin": "Administrator",
    "bash": "Manager",
    "dispetcer": "Viewer",
    "Təmir-telefonoqramma": "Maintenance notice",
    "Daxili bağlantı": "Internal interruption",
    "Yeni bağlantı": "New outage",
    "Bütün sahələri doldurun": "Complete all required fields",
    "Bağlanma səbəbi:": "Outage reason:",
    "Küçə:": "Street:",
    "Küçə adı, ev nömrəsi": "Street name and building number",
    "Abonent sayı:": "Affected customers:",
    "Kateqoriya:": "Category:",
    "Qaz xətti (mm):": "Gas pipe (mm):",
    "Boş buraxıla bilər": "Optional",
    "Bağlanma tarixi:": "Interruption date:",
    "Ləğv et": "Cancel",
    "Əlavə et": "Add",
    "Yadda saxla": "Save",
    "Məlumatları dəyişdirin": "Update the information",
    "Rayon adı daxil edin": "Enter a district name",
    "Küçə adı daxil edin": "Enter a street name",
    "Kateqoriya seçin": "Select a category",
    "Tarix formatı düzgün deyil: gg.aa.iiii": "Invalid date format: dd.mm.yyyy",
    "Status dəyiş": "Change status",
    "Cari status:": "Current status:",
    "Yeni status:": "New status:",
    "Tarix / Saat:": "Date / Time:",
    "ℹ️ Qeyd: Bu tarix/saat 'Açıldı' sütununa yazılacaq.": "ℹ️ Note: This date/time will be saved as the restoration time.",
    "ℹ️ Qeyd: Bu tarix/saat 'Bağlandı' sütununa yazılacaq.": "ℹ️ Note: This date/time will be saved as the interruption time.",
    "ℹ️ Qeyd: Stop statusu üçün tarix/saat saxlanmayacaq.": "ℹ️ Note: No date/time is stored for the stopped status.",
    "📊 Bağlantı Hesabatı": "📊 Outage Report",
    "Tarix aralığı üzrə cəmlər": "Totals by date range",
    "Tarixlər üzrə cəm": "Daily totals",
    "Qeyd: Qalıq = həmin tarixdə bağlanıb, hələ Bağlı qalan abonentlər.": "Note: Remaining means customers interrupted on that date and not yet restored.",
    "Başlanğıc:": "From:",
    "Bitiş:": "To:",
    "📅 Bu gün": "📅 Today",
    "📅 Dünən": "📅 Yesterday",
    "🔍 Hesabla": "🔍 Calculate",
    "📊 Cəmi bağlantı": "📊 Total affected",
    "🔓 Cəmi açılma": "🔓 Total restored",
    "🔒 Qalıq bağlantı": "🔒 Remaining affected",
    "📅 Tarix": "📅 Date",
    "🔒 Bağlı": "🔒 Closed",
    "🔓 Açıq": "🔓 Restored",
    "⏸️ Stop": "⏸️ Stopped",
    "📊 Cəmi": "📊 Total",
    "🏙️ Rayonlar": "🏙️ Districts",
    "📝 Bağlanma səbəbləri": "📝 Outage reasons",
    "➕ Əlavə et": "➕ Add",
    "Rayon əlavə et": "Add district",
    "Rayon adı:": "District name:",
    "Rayon dəyiş": "Rename district",
    "Yeni rayon adı:": "New district name:",
    "Səbəb əlavə et": "Add reason",
    "Səbəb dəyiş": "Rename reason",
    "Yeni səbəb adı:": "New reason:",
    "Bu rayon artıq mövcuddur.": "This district already exists.",
    "Bu adla rayon artıq mövcuddur.": "A district with this name already exists.",
    "Bu səbəb artıq mövcuddur.": "This reason already exists.",
    "Bu adla səbəb artıq mövcuddur.": "A reason with this name already exists.",
    "🏢 İdarələrin ünvanları": "🏢 Office Directory",
    "➕ Yeni idarə": "➕ New office",
    "🔍 Axtarış:": "🔍 Search:",
    "Ad, region, ünvan, telefon və ya qeydlərə görə axtar...": "Search by name, region, address, phone, or notes...",
    "🗑️ Təmizlə": "🗑️ Clear",
    "İdarə adı": "Office name",
    "Region kod": "Region code",
    "Rayon kod": "District code",
    "Ünvan": "Address",
    "Telefon": "Phone",
    "Qeydlər": "Notes",
    "Yeni idarə": "New office",
    "İdarə məlumatlarını doldurun": "Enter office information",
    "İdarə adı:": "Office name:",
    "Region adı:": "Region name:",
    "Region kodu:": "Region code:",
    "Rayon kodu:": "District code:",
    "Ünvan:": "Address:",
    "Telefon:": "Phone:",
    "Qeydlər:": "Notes:",
    "Tam ünvan": "Full address",
    "Əlavə məlumat": "Additional information",
    "Məs: Binəqədi 1, 2 XS": "Example: Central Office 1",
    "Məs: Mərkəzi region": "Example: Central region",
    "Məs: 1": "Example: 1",
    "Məs: 68": "Example: 68",
    "Məs: +994 50 123 45 67": "Example: +994 50 123 45 67",
    "İdarə redaktə": "Edit office",
    "İdarə adı daxil edin": "Enter an office name",
    "Ünvan daxil edin": "Enter an address",
    "Region kodu rəqəm olmalıdır": "The region code must be numeric",
    "Rayon kodu rəqəm olmalıdır": "The district code must be numeric",
    "Zəhmət olmasa bir sətir seçin.": "Please select a row.",
    "Təsdiq et": "Confirm",
    "Abonent sayı boş ola bilməz": "Affected customers cannot be empty",
    "Abonent sayı mənfi ola bilməz": "Affected customers cannot be negative",
    "Abonent sayı çox böyükdür (max 100000)": "Affected customers is too large (max 100000)",
    "Abonent sayı rəqəm olmalıdır": "Affected customers must be numeric",
    "Diametr mənfi ola bilməz": "Diameter cannot be negative",
    "Diametr çox böyükdür (max 1000 mm)": "Diameter is too large (max 1000 mm)",
    "Diametr rəqəm olmalıdır": "Diameter must be numeric",
}


def get_language() -> str:
    parser = configparser.ConfigParser()
    if Config.SETTINGS_PATH.exists():
        parser.read(Config.SETTINGS_PATH, encoding="utf-8")
    value = parser.get("APP", "language", fallback="az").lower()
    return value if value in {"az", "en"} else "az"


def set_language(language: str) -> None:
    language = language if language in {"az", "en"} else "az"
    parser = configparser.ConfigParser()
    if Config.SETTINGS_PATH.exists():
        parser.read(Config.SETTINGS_PATH, encoding="utf-8")
    if not parser.has_section("APP"):
        parser.add_section("APP")
    parser.set("APP", "language", language)
    with Config.SETTINGS_PATH.open("w", encoding="utf-8") as settings_file:
        parser.write(settings_file)


def t(text: str) -> str:
    if get_language() != "en" or not text:
        return text
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]

    patterns = (
        (r"^Qaz Bağlantıları \((.+)\) - (.+)$", r"Gas Outage Management (\1) - \2"),
        (r"^Son yenilənmə: (.+)$", r"Last refresh: \1"),
        (r"^Bağlantı redaktə \(ID (.+)\)$", r"Edit outage (ID \1)"),
        (r"^✏️ Redaktə — ID (.+)$", r"✏️ Edit — ID \1"),
        (r"^✏️ İdarə redaktə - ID (.+)$", r"✏️ Edit office - ID \1"),
        (r"^Cari status: (.+)$", lambda m: f"Current status: {t(m.group(1))}"),
        (r"^ID (.+) sətrini silmək istəyirsiniz\?$", r"Do you want to delete row ID \1?"),
        (r"^'(.+)' idarəsini silmək istəyirsiniz\?$", r"Do you want to delete the office '\1'?"),
        (r"^'(.+)' rayonunu silmək istəyirsiniz\?\nBu rayonla bağlı bütün bağlantılar təsirlənəcək!$", r"Delete district '\1'?\nAll related outage records will be affected!"),
        (r"^'(.+)' səbəbini silmək istəyirsiniz\?\nBu səbəblə bağlı bütün bağlantılar təsirlənəcək!$", r"Delete reason '\1'?\nAll related outage records will be affected!"),
        (r"^Backup yaradıldı:\n(.+)$", r"Backup created:\n\1"),
        (r"^Bu adla idarə artıq mövcuddur: (.+)$", r"An office with this name already exists: \1"),
        (r"^Dəyişiklik edilə bilmədi: (.+)$", r"The change could not be saved: \1"),
    )
    for pattern, replacement in patterns:
        if re.match(pattern, text, flags=re.DOTALL):
            return re.sub(pattern, replacement, text, flags=re.DOTALL)
    return text


def _translate_property(widget: QWidget, property_name: str, getter, setter) -> None:
    source_key = f"i18n_source_{property_name}"
    source = widget.property(source_key)
    current = getter()
    if source is None:
        source = current
        widget.setProperty(source_key, source)
    setter(t(source))


def retranslate_widget_tree(root: QWidget) -> None:
    widgets = [root, *root.findChildren(QWidget)]
    for widget in widgets:
        if widget.isWindow():
            _translate_property(widget, "window_title", widget.windowTitle, widget.setWindowTitle)
        if isinstance(widget, (QLabel, QAbstractButton)):
            _translate_property(widget, "text", widget.text, widget.setText)
        if isinstance(widget, QGroupBox):
            _translate_property(widget, "title", widget.title, widget.setTitle)
        if isinstance(widget, QLineEdit):
            _translate_property(
                widget,
                "placeholder",
                widget.placeholderText,
                widget.setPlaceholderText,
            )
        if isinstance(widget, QTabWidget):
            for index in range(widget.count()):
                key = f"i18n_tab_{index}"
                source = widget.property(key)
                if source is None:
                    source = widget.tabText(index)
                    widget.setProperty(key, source)
                widget.setTabText(index, t(source))
        if isinstance(widget, QTableWidget):
            for column in range(widget.columnCount()):
                item = widget.horizontalHeaderItem(column)
                if item is None:
                    continue
                source_role = int(Qt.ItemDataRole.UserRole) + 1
                source = item.data(source_role)
                if source is None:
                    source = item.text()
                    item.setData(source_role, source)
                item.setText(t(source))


class TranslationEventFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Show and isinstance(watched, QWidget):
            retranslate_widget_tree(watched)
        return super().eventFilter(watched, event)


def install_translation_filter(app: QApplication) -> TranslationEventFilter:
    event_filter = TranslationEventFilter(app)
    app.installEventFilter(event_filter)
    return event_filter
