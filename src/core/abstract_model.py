from abc import ABC
from uuid import uuid4
from src.core.exception import arguments_exception


class name_id(ABC):
    """Базовый абстрактный класс с id и именем."""

    def __init__(self, name: str = None) -> None:
        """Конструктор."""
        self._id: str = str(uuid4())
        self._name: str = ""
        # Если передали аргумент при инициализации — валидируем через сеттер
        if name is not None:
            self.name = name

    def __eq__(self, other: object) -> bool:
        """Сравнение сущностей по типу и значению id."""
        if not isinstance(other, name_id):
            return False
        return self.id == other.id

    @property
    def id(self) -> str:
        """Получить id."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """Установить id вручную с валидацией."""
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception(field="id", message="ID не может быть пустым")
        self._id = value.strip()

    @property
    def name(self) -> str:
        """Получить имя."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Установить имя с валидацией (<= 50 символов)"""
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception(field="name", message="Имя объекта не может быть пустым")
        cleaned_value = value.strip()
        if len(cleaned_value) > 50:
            raise arguments_exception(field="name", message="Длина не должна превышать 50 символов")
        self._name = cleaned_value