from abc import ABC
import uuid

class name_id(ABC):
    """Базовый абстрактный класс с id и именем."""

    def __init__(self):
        """Конструктор."""
        self.__name = ""
        self.__id = uuid.uuid4()

    @property
    def id(self):
        """Получить id."""
        return self.__id

    @property
    def name(self) -> str:
        """Получить имя."""
        return self.__name

    @name.setter
    def name(self, new_name: str):
        """Установить имя."""
        if new_name is not None and len(new_name) > 0:
            self.__name = new_name
        else:
            raise ValueError("Имя не должно быть пустым")