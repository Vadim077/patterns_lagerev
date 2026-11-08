from abc import ABC, abstractmethod
from typing import Any
from src.core.abstract_deserializer import abstract_deserializer


class abstract_deserialize_factory(ABC):
    """
    Абстрактный интерфейс фабрики десериализаторов
    """

    @abstractmethod
    def create(self, target_type_or_data: Any) -> abstract_deserializer:
        """
        Создать или вернуть десериализатор под целевой тип
        """
        pass