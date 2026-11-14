from abc import ABC
from typing import Optional
from uuid import uuid4
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.exception import arguments_exception


class name_id(ABC):
    """Базовый абстрактный класс с id, наименованием и типом."""

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
        """Получить наименование."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Установить наименование с валидацией (<= 50 символов)"""
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception(field="name", message="Имя объекта не может быть пустым")
        cleaned_value = value.strip()
        if len(cleaned_value) > 50:
            raise arguments_exception(field="name", message="Длина не должна превышать 50 символов")
        self._name = cleaned_value

    @property
    def type(self) -> str:
        """Тип модели (имя класса) для полиморфной сериализации и десериализации."""
        return self.__class__.__name__

    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None):
        """
        Базовый фабричный метод (GoF Factory Method) создания объекта из словаря.
        """
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")
        name = data.get("name")
        instance = cls(name=name) if name is not None else cls()
        item_id = data.get("id")
        if item_id:
            instance.id = item_id
        return instance

    @classmethod
    def from_dict(cls, data: dict, service: Optional[abstract_deserialization_context] = None):
        """Синоним фабричного метода create."""
        return cls.create(data, service)


abstract_model = name_id
