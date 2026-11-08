from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import nomenclature_group_model


class nomenclature_group_deserializer(abstract_deserializer):
    """
    Десериализатор групп номенклатуры
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[nomenclature_group_model]:
        if data is None or not isinstance(data, dict):
            return None

        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        name = data.get("name")
        instance = nomenclature_group_model(name=name)
        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)

        return instance