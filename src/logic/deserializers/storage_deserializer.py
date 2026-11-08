from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import storage_model


class storage_deserializer(abstract_deserializer):
    """
    Десериализатор складов
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[storage_model]:
        if data is None or not isinstance(data, dict):
            return None

        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        name = data.get("name")
        instance = storage_model(name=name)
        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)

        return instance