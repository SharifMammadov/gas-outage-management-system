"""
Tema və stillər - Açıq və tünd tema (status rəngləri ilə)
"""

# ========== AÇIQ TEMA RƏNGLƏRİ ==========
LIGHT_BG = "#f5f5f7"              # Açıq boz - fon
LIGHT_PANEL = "#ffffff"            # Ağ - panellər
LIGHT_ACCENT = "#2b5797"           # Tünd göy - vurğu rəngi
LIGHT_ACCENT2 = "#1e3f6e"          # Daha tünd göy - hover effekti
LIGHT_TEXT = "#2c3e50"             # Tünd boz - mətn rəngi
LIGHT_TEXT_LIGHT = "#5e6b7d"       # Açıq boz - ikinci dərəcəli mətn
LIGHT_MUTED = "#7f8c8d"            # Boz - solğun mətn
LIGHT_BORDER = "#d0d7de"           # Açıq boz - sərhəd rəngi
LIGHT_ROW_NORMAL = "#ffffff"        # Ağ - normal sətir
LIGHT_ROW_ALTERNATE = "#f8fafc"     # Çox açıq göy - alternativ sətir
LIGHT_ROW_SELECTED = "#e1ecf9"      # Açıq göy - seçilmiş sətir

# AÇIQ TEMA STATUS RƏNGLƏRİ
LIGHT_ROW_CLOSED = "#ffcdd2"        # Açıq qırmızı - Bağlı
LIGHT_ROW_OPEN = "#c8e6c9"          # Açıq yaşıl - Açıq
LIGHT_ROW_STOP = "#fff9c4"          # Açıq sarı - Stop

# ========== TÜND TEMA RƏNGLƏRİ ==========
DARK_BG = "#1a1a1a"                # Tünd boz - fon
DARK_PANEL = "#2d2d2d"             # Tünd boz - panellər
DARK_ACCENT = "#64b5f6"            # Açıq göy - vurğu rəngi
DARK_ACCENT2 = "#90caf9"           # Daha açıq göy - hover effekti
DARK_TEXT = "#e0e0e0"              # Açıq boz - mətn rəngi (ümumi)
DARK_TEXT_LIGHT = "#a0a0a0"        # Boz - ikinci dərəcəli mətn
DARK_MUTED = "#808080"             # Tünd boz - solğun mətn
DARK_BORDER = "#404040"            # Tünd boz - sərhəd rəngi
DARK_ROW_NORMAL = "#2d2d2d"        # Tünd boz - normal sətir
DARK_ROW_ALTERNATE = "#363636"     # Bir az açıq - alternativ sətir
DARK_ROW_SELECTED = "#1e3a5f"      # Tünd göy - seçilmiş sətir

# TÜND TEMA STATUS RƏNGLƏRİ
DARK_ROW_CLOSED = "#6b2e2e"         # Tünd qırmızı - Bağlı
DARK_ROW_OPEN = "#2e6b2e"           # Tünd yaşıl - Açıq
DARK_ROW_STOP = "#6b6b2e"           # Tünd sarı - Stop

# TÜND TEMA STATUS MƏTN RƏNGLƏRİ (qara - yaxşı görsənsin deyə)
DARK_ROW_CLOSED_TEXT = "#000000"     # Qara - Bağlı sətirlərdə mətn
DARK_ROW_OPEN_TEXT = "#000000"       # Qara - Açıq sətirlərdə mətn
DARK_ROW_STOP_TEXT = "#000000"       # Qara - Stop sətirlərdə mətn
DARK_ROW_NORMAL_TEXT = "#e0e0e0"     # Açıq boz - normal sətirlərdə mətn

# Cari tema (default: açıq)
current_theme = "light"  # "light" və ya "dark"

def get_colors(theme=None):
    """Tema rənglərini qaytar"""
    if theme is None:
        theme = current_theme

    if theme == "dark":
        return {
            'BG': DARK_BG,
            'PANEL': DARK_PANEL,
            'ACCENT': DARK_ACCENT,
            'ACCENT2': DARK_ACCENT2,
            'TEXT': DARK_TEXT,
            'TEXT_LIGHT': DARK_TEXT_LIGHT,
            'MUTED': DARK_MUTED,
            'BORDER': DARK_BORDER,
            'ROW_NORMAL': DARK_ROW_NORMAL,
            'ROW_ALTERNATE': DARK_ROW_ALTERNATE,
            'ROW_SELECTED': DARK_ROW_SELECTED,
            'ROW_CLOSED': DARK_ROW_CLOSED,
            'ROW_OPEN': DARK_ROW_OPEN,
            'ROW_STOP': DARK_ROW_STOP,
            'ROW_CLOSED_TEXT': DARK_ROW_CLOSED_TEXT,
            'ROW_OPEN_TEXT': DARK_ROW_OPEN_TEXT,
            'ROW_STOP_TEXT': DARK_ROW_STOP_TEXT,
            'ROW_NORMAL_TEXT': DARK_ROW_NORMAL_TEXT
        }
    else:
        return {
            'BG': LIGHT_BG,
            'PANEL': LIGHT_PANEL,
            'ACCENT': LIGHT_ACCENT,
            'ACCENT2': LIGHT_ACCENT2,
            'TEXT': LIGHT_TEXT,
            'TEXT_LIGHT': LIGHT_TEXT_LIGHT,
            'MUTED': LIGHT_MUTED,
            'BORDER': LIGHT_BORDER,
            'ROW_NORMAL': LIGHT_ROW_NORMAL,
            'ROW_ALTERNATE': LIGHT_ROW_ALTERNATE,
            'ROW_SELECTED': LIGHT_ROW_SELECTED,
            'ROW_CLOSED': LIGHT_ROW_CLOSED,
            'ROW_OPEN': LIGHT_ROW_OPEN,
            'ROW_STOP': LIGHT_ROW_STOP,
            'ROW_CLOSED_TEXT': LIGHT_TEXT,  # Açıq temada normal mətn rəngi
            'ROW_OPEN_TEXT': LIGHT_TEXT,
            'ROW_STOP_TEXT': LIGHT_TEXT,
            'ROW_NORMAL_TEXT': LIGHT_TEXT
        }

def set_theme(theme):
    """Temanı dəyiş"""
    global current_theme
    if theme in ["light", "dark"]:
        current_theme = theme
        return True
    return False

def get_qss(theme=None):
    """Tema üçün QSS qaytar"""
    c = get_colors(theme)

    return f"""
    QMainWindow, QDialog {{
        background-color: {c['BG']};
        color: {c['TEXT']};
    }}
    QTabWidget::pane {{
        background-color: {c['PANEL']};
        border: 1px solid {c['BORDER']};
    }}
    QTabBar::tab {{
        background-color: {c['PANEL']};
        color: {c['TEXT']};
        padding: 8px 16px;
    }}
    QTabBar::tab:selected {{
        background-color: {c['ACCENT']};
        color: white;
    }}
    .card, .filter-bar {{
        background-color: {c['PANEL']};
        border: 1px solid {c['BORDER']};
        border-radius: 8px;
    }}
    QTableWidget {{
        background-color: {c['PANEL']};
        alternate-background-color: {c['ROW_ALTERNATE']};
        gridline-color: {c['BORDER']};
        color: {c['TEXT']};
    }}
    QTableWidget::item:selected {{
        background-color: {c['ROW_SELECTED']};
    }}
    QHeaderView::section {{
        background-color: {c['PANEL']};
        color: {c['ACCENT']};
        padding: 8px;
        border-bottom: 2px solid {c['ACCENT']};
    }}
    QPushButton {{
        background-color: {c['ACCENT']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: {c['ACCENT2']};
    }}
    QPushButton[class="soft"] {{
        background-color: {c['PANEL']};
        color: {c['ACCENT']};
        border: 1px solid {c['ACCENT']};
    }}
    QLineEdit, QComboBox {{
        background-color: {c['PANEL']};
        border: 1px solid {c['BORDER']};
        border-radius: 6px;
        padding: 6px 10px;
        color: {c['TEXT']};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {c['ACCENT']};
    }}
    QLabel {{
        color: {c['TEXT']};
    }}
    QLabel[class="title"] {{
        font-size: 16pt;
        font-weight: bold;
        color: {c['ACCENT']};
    }}
    QLabel[class="muted"] {{
        color: {c['TEXT_LIGHT']};
    }}
    QListWidget {{
        background-color: {c['PANEL']};
        border: 1px solid {c['BORDER']};
        color: {c['TEXT']};
    }}
    QListWidget::item:selected {{
        background-color: {c['ROW_SELECTED']};
    }}
    QScrollBar:vertical {{
        background-color: {c['BG']};
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['BORDER']};
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {c['ACCENT']};
    }}
    """

# Geriye uyğunluq üçün sabitlər
C_BG = LIGHT_BG
C_PANEL = LIGHT_PANEL
C_ACCENT = LIGHT_ACCENT
C_ACCENT2 = LIGHT_ACCENT2
C_TEXT = LIGHT_TEXT
C_TEXT_LIGHT = LIGHT_TEXT_LIGHT
C_MUTED = LIGHT_MUTED
C_BORDER = LIGHT_BORDER
ROW_CLOSED = LIGHT_ROW_CLOSED
ROW_OPEN = LIGHT_ROW_OPEN
ROW_STOP = LIGHT_ROW_STOP

# Default QSS
QSS = get_qss("light")

__all__ = [
    'QSS', 'get_qss', 'set_theme', 'get_colors', 'current_theme',
    'C_BG', 'C_PANEL', 'C_ACCENT', 'C_ACCENT2', 'C_TEXT', 'C_TEXT_LIGHT',
    'C_MUTED', 'C_BORDER', 'ROW_CLOSED', 'ROW_OPEN', 'ROW_STOP'
]