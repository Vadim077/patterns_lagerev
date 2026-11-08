from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.models import (
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
)


class recipe_row_deserializer(abstract_deserializer):
    """
    Десериализатор строки технологической карты
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[recipe_row_model]:
        if data is None or not isinstance(data, dict):
            return None

        item_id = data.get("id")
        if self.__service and item_id and self.__service.has_cache(item_id):
            return self.__service.get_cache(item_id)

        nom = None
        nom_data = data.get("nomenclature")
        if isinstance(nom_data, dict) and self.__service:
            nom = self.__service.deserialize(nom_data, nomenclature_model)

        brutto = float(data.get("brutto", 0.0))
        netto = float(data.get("netto", brutto))

        range_unit = None
        range_data = data.get("range")
        if isinstance(range_data, dict) and self.__service:
            range_unit = self.__service.deserialize(range_data, range_model)

        # Рекурсивное восстановление полуфабриката
        sub_recipe = None
        sub_recipe_data = data.get("sub_recipe")
        if isinstance(sub_recipe_data, dict) and self.__service:
            sub_recipe = self.__service.deserialize(sub_recipe_data, recipe_model)

        instance = recipe_row_model(
            nomenclature=nom,
            brutto=brutto,
            netto=netto,
            range_unit=range_unit,
            sub_recipe=sub_recipe,
        )

        if item_id:
            instance.id = item_id
            if self.__service:
                self.__service.set_cache(item_id, instance)
        return instance