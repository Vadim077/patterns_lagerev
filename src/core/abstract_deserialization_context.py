from abc import ABC, abstractmethod
from typing import Any, Optional


class abstract_deserialization_context(ABC):

    @abstractmethod
    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        pass

    @abstractmethod
    def has_cache(self, model_type: type, item_id: str) -> bool:
        pass

    @abstractmethod
    def get_cache(self, model_type: type, item_id: str) -> Optional[object]:
        pass

    @abstractmethod
    def set_cache(self, model_type: type, item_id: str, instance: object) -> None:
        pass
