"""
UI köməkçi funksiyaları
"""
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtCore import Qt

def make_label(text: str, cls: str = "", bold: bool = False) -> QLabel:
    """Label yarat"""
    label = QLabel(text)
    if cls:
        label.setProperty("class", cls)
    if bold:
        font = label.font()
        font.setBold(True)
        label.setFont(font)
    return label

def make_btn(text: str, cls: str = "") -> QPushButton:
    """Düymə yarat"""
    btn = QPushButton(text)
    if cls:
        btn.setProperty("class", cls)
    return btn

def center_on_parent(widget, width: int, height: int, parent=None):
    """Widget-i parent-in mərkəzində yerləşdir"""
    if parent and parent.isVisible():
        x = parent.x() + (parent.width() - width) // 2
        y = parent.y() + (parent.height() - height) // 2
    else:
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2

    widget.move(x, y)

def truncate_text(text: str, max_length: int = 50) -> str:
    """Uzun mətni qısalt"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_address(street: str, building: str = "", apartment: str = "") -> str:
    """Ünvanı formatla"""
    parts = []
    if street:
        parts.append(street)
    if building:
        parts.append(f"bina {building}")
    if apartment:
        parts.append(f"mənzil {apartment}")
    return ", ".join(parts)