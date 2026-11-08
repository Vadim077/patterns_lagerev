from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
)


class nomenclature_deserializer(abstract_deserializer):
    """
    Десериализатор номенклатуры
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[nomenclature_model]:
        if data is None or not isinstance(data, dict):
            return None

        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        name = data.get("name")
        full_name = data.get("full_name", name)

        # Рекурсивно восстанавливаем связанные группу и единицу измерения
        group = None
        group_data = data.get("group")
        if isinstance(group_data, dict) and self.__service:
            group = self.__service.deserialize(group_data, nomenclature_group_model)

        range_unit = None
        range_data = data.get("range")
        if isinstance(range_data, dict) and self.__service:
            range_unit = self.__service.deserialize(range_data, range_model)

        instance = nomenclature_model(name=name, full_name=full_name, group=group, range_unit=range_unit)
        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)

        return instance