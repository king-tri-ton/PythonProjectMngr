"""
Менеджер проектов - основная бизнес-логика
"""
import os
import json
import shutil
from pathlib import Path


class ProjectManager:
    def __init__(self):
        user = os.getlogin()
        self.app_folder = Path(f"C:/Users/{user}/PythonProjectMngr")
        self.app_folder.mkdir(parents=True, exist_ok=True)

        self.config_file = self.app_folder / "settings.mngr"
        self.load_config()

    def get_default_root(self):
        default = self.app_folder / "Projects"
        default.mkdir(parents=True, exist_ok=True)
        return str(default)

    def load_config(self):
        default_root = self.get_default_root()
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.root_path = config.get("root_path", default_root)
                    self.open_after_create = config.get("open_after_create", True)
            except:
                self.root_path = default_root
                self.open_after_create = True
                self.save_config()
        else:
            self.root_path = default_root
            self.open_after_create = True
            self.save_config()

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump({
                "root_path": self.root_path,
                "open_after_create": self.open_after_create
            }, f, ensure_ascii=False, indent=4)

    def ensure_root_exists(self):
        """Убедиться, что корневая папка существует"""
        os.makedirs(self.root_path, exist_ok=True)

    def create_project(self, project_name):
        """
        Создание нового проекта
        Returns: (success: bool, message: str, project_path: str)
        """
        if not project_name or not project_name.strip():
            return False, "Введите название проекта!", None

        name = project_name.strip()

        # Проверка на недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        if any(char in name for char in invalid_chars):
            return False, "Название содержит недопустимые символы!", None

        self.ensure_root_exists()
        project_path = os.path.join(self.root_path, name)

        if os.path.exists(project_path):
            return False, f"Проект '{name}' уже существует!", None

        try:
            os.makedirs(project_path)
            app_file = os.path.join(project_path, "app.py")
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write("")  # Создаём пустой файл

            return True, f"Проект '{name}' создан!", project_path
        except Exception as e:
            return False, f"Не удалось создать проект:\n{str(e)}", None

    def get_projects(self):
        """Получение списка проектов"""
        self.ensure_root_exists()
        try:
            return sorted([
                d for d in os.listdir(self.root_path)
                if os.path.isdir(os.path.join(self.root_path, d))
            ])
        except Exception:
            return []

    def delete_project(self, project_name):
        """Удаление проекта"""
        if not project_name:
            return False, "Проект не выбран!"

        project_path = os.path.join(self.root_path, project_name)

        if not os.path.exists(project_path):
            return False, f"Проект '{project_name}' не найден!"

        try:
            shutil.rmtree(project_path)
            return True, f"Проект '{project_name}' удалён!"
        except Exception as e:
            return False, f"Не удалось удалить проект:\n{str(e)}"

    def open_projects_folder(self):
        """Открытие папки с проектами"""
        self.ensure_root_exists()
        os.startfile(self.root_path)

    def open_project_folder(self, project_path):
        """Открытие конкретной папки проекта"""
        if os.path.exists(project_path):
            os.startfile(project_path)

    def change_root_path(self, new_path, move_projects=True):
        """Изменение корневой папки"""
        if not new_path:
            return False, "Путь не указан!"

        old_path = self.root_path

        if old_path == new_path:
            return True, "Путь не изменился"

        try:
            # Создаём новую папку если не существует
            os.makedirs(new_path, exist_ok=True)

            # Переносим проекты если нужно
            if move_projects and os.path.exists(old_path):
                projects = self.get_projects()

                for project in projects:
                    old_project_path = os.path.join(old_path, project)
                    new_project_path = os.path.join(new_path, project)

                    if not os.path.exists(new_project_path):
                        shutil.move(old_project_path, new_project_path)

            self.root_path = new_path
            self.save_config()

            return True, "Настройки сохранены и проекты перенесены!"
        except PermissionError:
            return False, "Отказано в доступе. Выбери другую папку или запусти программу от имени администратора."
        except Exception as e:
            return False, f"Ошибка при изменении пути:\n{str(e)}"
