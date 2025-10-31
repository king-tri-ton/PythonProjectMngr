"""
Окна приложения
"""
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                              QMessageBox, QFileDialog, QCheckBox)
from PyQt6.QtCore import Qt
from core.utils import set_window_icon, add_footer_label, center_window
import os


class SilentMessageBox(QDialog):
    """Полностью бесшумное окно уведомления"""
    def __init__(self, parent=None, title="", text="", icon=None, buttons=("OK",)):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(200, 100)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)

        # Устанавливаем иконку **после** установки флагов
        set_window_icon(self)

        layout = QVBoxLayout()
        layout.addStretch()

        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.buttons = {}
        for b in buttons:
            btn = QPushButton(b)
            btn.clicked.connect(lambda _, x=b: self.on_click(x))
            self.buttons[b] = btn
            btn_layout.addWidget(btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.clicked_button = None

    def on_click(self, button_text):
        """Обработчик кнопки"""
        self.clicked_button = button_text
        self.accept()

    def exec_with_result(self):
        """Аналог QMessageBox.exec(), возвращает текст кнопки"""
        super().exec()
        return self.clicked_button

class CreateProjectWindow(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        set_window_icon(self)
        add_footer_label(self)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Создать проект | PythonProjectMngr")
        self.setFixedSize(410, 150)
        center_window(self)
        
        layout = QVBoxLayout()
        
        # Метка
        label = QLabel("Название проекта:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Поле ввода
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название проекта")
        
        # Исправленные стили с одинаковыми отступами со всех сторон
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
            }
        """)
        
        self.name_input.setFixedHeight(30)
        # Убираем AlignVCenter - он влияет только на текст, не на placeholder
        
        self.name_input.returnPressed.connect(self.create_project)
        layout.addWidget(self.name_input)
        
        # Кнопка
        btn = QPushButton("Создать")
        btn.clicked.connect(self.create_project)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        self.name_input.setFocus()
    
    def create_project(self):
        """Создание проекта"""
        project_name = self.name_input.text()
        success, message, project_path = self.manager.create_project(project_name)

        if success:
            msg = SilentMessageBox(self, "Успех", message)
            msg.exec_with_result()

            # Открываем папку проекта если включена опция
            if self.manager.open_after_create and project_path:
                self.manager.open_project_folder(project_path)

            self.close()
        else:
            msg = SilentMessageBox(self, "Ошибка", message)
            msg.exec_with_result()

class DeleteProjectWindow(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        set_window_icon(self)
        add_footer_label(self)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Удалить проект | PythonProjectMngr")
        self.setGeometry(100, 100, 500, 400)
        center_window(self)
        
        layout = QVBoxLayout()
        
        # Метка
        label = QLabel("Список проектов:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Название проекта"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Отключаем редактирование ячеек
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Подключаем двойной клик к удалению
        self.table.cellDoubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_project)
        btn_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_projects)
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_projects()

    def on_double_click(self, row, column):
        """Обработка двойного клика по строке"""
        self.delete_project()
    
    def load_projects(self):
        """Загрузка списка проектов"""
        projects = self.manager.get_projects()
        self.table.setRowCount(len(projects))
        
        for i, project in enumerate(projects):
            item = QTableWidgetItem(project)
            self.table.setItem(i, 0, item)
    
    def delete_project(self):
        """Удаление выбранного проекта"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            msg = SilentMessageBox(self, "Предупреждение", "Выберите проект для удаления!")
            msg.exec_with_result()
            return
        
        project_name = self.table.item(selected_row, 0).text()
        msg = SilentMessageBox(
            self,
            "Подтверждение",
            f"Вы действительно хотите удалить проект '{project_name}'?",
            buttons=("Да", "Нет")
        )
        reply = msg.exec_with_result()
        
        if reply == "Да":
            success, message = self.manager.delete_project(project_name)
            if success:
                self.load_projects()
                result_msg = SilentMessageBox(self, "Успех", message)
            else:
                result_msg = SilentMessageBox(self, "Ошибка", message)
            result_msg.exec_with_result()

class SettingsWindow(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        set_window_icon(self)
        add_footer_label(self)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Настройки | PythonProjectMngr")
        self.setFixedSize(600, 220)
        center_window(self)
        
        layout = QVBoxLayout()
        
        # Метка корневой папки
        label = QLabel("Корневая папка проектов:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Поле пути и кнопка обзора
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit(self.manager.root_path)
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Чекбокс для переноса проектов
        self.move_checkbox = QCheckBox("Перенести существующие проекты в новую папку")
        self.move_checkbox.setChecked(True)
        layout.addWidget(self.move_checkbox)
        
        # Разделитель
        layout.addSpacing(10)
        
        # Метка поведения
        behavior_label = QLabel("Поведение после создания проекта:")
        behavior_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(behavior_label)
        
        # Чекбокс для открытия папки после создания
        self.open_after_create_checkbox = QCheckBox("Автоматически открывать папку после создания проекта")
        self.open_after_create_checkbox.setChecked(self.manager.open_after_create)
        layout.addWidget(self.open_after_create_checkbox)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def browse_folder(self):
        """Выбор папки"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку",
            self.manager.root_path
        )
        
        if folder:
            self.path_input.setText(folder)
    
    def save_settings(self):
        """Сохранение настроек"""
        new_path = self.path_input.text()
        move_projects = self.move_checkbox.isChecked()

        # Проверяем, изменился ли путь
        path_changed = (new_path != self.manager.root_path)

        # Проверяем, изменилась ли настройка открытия проекта
        open_changed = (self.manager.open_after_create != self.open_after_create_checkbox.isChecked())

        # Сохраняем новую настройку открытия проекта
        self.manager.open_after_create = self.open_after_create_checkbox.isChecked()

        if path_changed:
            # Меняем корневую папку, если она действительно изменилась
            success, message = self.manager.change_root_path(new_path, move_projects)
        else:
            # Если путь тот же, просто сообщаем о сохранении настроек
            success, message = True, "Настройки сохранены"

        msg = SilentMessageBox(self, "Успех" if success else "Ошибка", message)
        msg.exec_with_result()

        if success:
            self.close()