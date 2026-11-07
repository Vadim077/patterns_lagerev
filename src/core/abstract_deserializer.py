from abc import ABC, abstractmethod
from typing import Any, Optional


class abstract_deserializer(ABC):
    """
    Абстрактный базовый класс десериализатора данных
    """

    @abstractmethod
    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Преобразовать исходные данные в объект целевого типа
        """
        pass