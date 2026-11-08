from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import (
    nomenclature_model,
    recipe_model,
    recipe_row_model,
)


class recipe_deserializer(abstract_deserializer):
    """
    Десериализатор технологической карты
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[recipe_model]:
        if data is None or not isinstance(data, dict):
            return None

        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        name = data.get("name")
        dish = None
        dish_data = data.get("dish")
        if isinstance(dish_data, dict) and self.__service:
            dish = self.__service.deserialize(dish_data, nomenclature_model)

        cooking_time = int(data.get("cooking_time", 0))
        instructions = data.get("instructions", [])
        portions = int(data.get("portions", 1))

        instance = recipe_model(
            name=name,
            dish=dish,
            cooking_time=cooking_time,
            instructions=instructions,
            portions=portions,
        )

        # Восстанавливаем строки рецепта
        for row_data in data.get("rows", []):
            if self.__service:
                row_model = self.__service.deserialize(row_data, recipe_row_model)
            else:
                row_model = None
            if row_model is not None:
                instance.add_row(row_model)

        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)

        return instance