from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import range_model


class range_deserializer(abstract_deserializer):
    """
    Десериализатор единиц измерения
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[range_model]:
        if data is None or not isinstance(data, dict):
            return None

        # Проверка кэша сервиса
        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        name = data.get("name")
        conversion_factor = float(data.get("conversion_factor", 1.0))

        # Рекурсивная десериализация базовой единицы
        base_range = None
        base_range_data = data.get("base_range")
        if isinstance(base_range_data, dict):
            if self.__service:
                base_range = self.__service.deserialize(base_range_data, range_model)
            else:
                base_range = self.deserialize(base_range_data, range_model)

        instance = range_model(name=name, conversion_factor=conversion_factor, base_range=base_range)
        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)

        return instance