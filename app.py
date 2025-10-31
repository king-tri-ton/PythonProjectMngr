"""
PythonProjectMngr - Главный файл приложения
"""
import sys
from PyQt6.QtWidgets import QApplication
from core.manager import ProjectManager
from ui.tray import TrayIcon


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    manager = ProjectManager()
    tray = TrayIcon(manager)
    tray.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()