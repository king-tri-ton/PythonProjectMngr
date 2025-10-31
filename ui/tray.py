"""
Системный трей с меню над панелью задач
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QAction, QCursor
from PyQt6.QtCore import Qt, QPoint
from ui.windows import CreateProjectWindow, DeleteProjectWindow, SettingsWindow
import sys
from pathlib import Path

class TrayIcon(QSystemTrayIcon):
    def __init__(self, manager):
        self.manager = manager
        
        # Правильная загрузка иконки для PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent
        
        icon_path = base_path / "python.png"
        
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            # Запасной вариант - создание иконки программно
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(Qt.GlobalColor.blue)
            painter.drawEllipse(8, 8, 48, 48)
            painter.end()
            icon = QIcon(pixmap)
        
        super().__init__(icon)
        self.setToolTip("Python Project Manager")
        
        # Создаём меню вручную
        self.menu = QMenu()
        
        create_action = QAction("Создать проект", self.menu)
        create_action.triggered.connect(self.show_create_window)
        self.menu.addAction(create_action)
        
        open_action = QAction("Открыть проекты", self.menu)
        open_action.triggered.connect(self.manager.open_projects_folder)
        self.menu.addAction(open_action)
        
        delete_action = QAction("Удалить проект", self.menu)
        delete_action.triggered.connect(self.show_delete_window)
        self.menu.addAction(delete_action)
        
        self.menu.addSeparator()
        
        settings_action = QAction("Настройки", self.menu)
        settings_action.triggered.connect(self.show_settings_window)
        self.menu.addAction(settings_action)
        
        self.menu.addSeparator()
        
        quit_action = QAction("Выход", self.menu)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
        
        self.activated.connect(self.on_tray_activated)
        self.show()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            cursor_pos = QCursor.pos()  # текущая позиция курсора
            screen = QApplication.primaryScreen().availableGeometry()
            menu_height = self.menu.sizeHint().height()
            
            x = cursor_pos.x()
            y = min(cursor_pos.y(), screen.bottom() - menu_height - 5)
            
            self.menu.popup(QPoint(x, y))
    
    def show_create_window(self):
        self.create_window = CreateProjectWindow(self.manager)
        self.create_window.show()
    
    def show_delete_window(self):
        self.delete_window = DeleteProjectWindow(self.manager)
        self.delete_window.show()
    
    def show_settings_window(self):
        self.settings_window = SettingsWindow(self.manager)
        self.settings_window.show()
    
    def quit_app(self):
        QApplication.quit()