from abc import ABC, abstractmethod
from typing import Any, Optional
from src.core.abstract_deserialization_context import abstract_deserialization_context
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

    @property
    @abstractmethod
    def service(self) -> Optional[abstract_deserialization_context]:
        pass

    @service.setter
    @abstractmethod
    def service(self, value: Optional[abstract_deserialization_context]) -> None:
        pass

    @abstractmethod
    def get_model_class(self, type_name: str) -> Optional[type]:
        pass

    @abstractmethod
    def register_class(self, cls: type) -> None:
        pass
