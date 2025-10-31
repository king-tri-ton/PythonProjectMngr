"""
Вспомогательные функции и утилиты приложения
"""
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl

def set_window_icon(window: QWidget, icon_name="python.ico"):
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent

    icon_path = base_path / icon_name
    window.setWindowIcon(QIcon(str(icon_path)))

def add_footer_label(window: QWidget, text=None):
    if text is None:
        text = (
            'Создал <a href="https://github.com/king-tri-ton" '
            'style="color: #2980b9; text-decoration: none;">King Triton</a> '
            'для Python сообщества | '
            '<a href="https://github.com/king-tri-ton/PythonProjectMngr" '
            'style="color: #2980b9; text-decoration: none;">PythonProjectMngr</a>'
        )
    
    layout = window.layout()
    if layout is None:
        return
    
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    label.setOpenExternalLinks(True)
    label.setStyleSheet("font-size: 10pt; color: gray; margin-top: 10px; margin-bottom: 5px;")
    
    layout.addWidget(label)


def center_window(window):
    """Центрирование окна на экране"""
    screen = window.screen().geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)