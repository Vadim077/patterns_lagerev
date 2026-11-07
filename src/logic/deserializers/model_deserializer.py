from typing import Any, Callable, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.core.exception import arguments_exception
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    storage_model,
)


class model_deserializer(abstract_deserializer):
    """
    Десериализатор доменных сущностей и моделей данных
    """

    def __init__(self, factory: Optional[Any] = None) -> None:
        self.__factory = factory
        self.__cache: dict[str, Any] = {}

        # Маппинг методов
        self.__builders: dict[type, Callable[[dict], Any]] = {
            range_model: self._build_range,
            nomenclature_group_model: self._build_group,
            storage_model: self._build_storage,
            nomenclature_model: self._build_nomenclature,
            recipe_row_model: self._build_recipe_row,
            recipe_model: self._build_recipe,
        }

    @property
    def factory(self) -> Optional[Any]:
        return self.__factory

    @factory.setter
    def factory(self, value: Optional[Any]) -> None:
        self.__factory = value

    def clear_cache(self) -> None:
        """
        Очистить кэш восстановленных объектов
        """
        self.__cache.clear()

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Восстановление доменной модели из словаря данных
        """
        if data is None:
            return None

        if not isinstance(data, dict):
            return data

        if target_type is None:
            raise arguments_exception(
                field="target_type",
                message="Целевой класс модели (target_type) обязателен для десериализации объекта",
            )

        # Проверка кэша по id
        item_id = data.get("id")
        if item_id and item_id in self.__cache:
            return self.__cache[item_id]

        builder = self._get_builder(target_type)
        if builder is None:
            raise arguments_exception(
                field="target_type",
                message=f"Не найден строитель для типа: {target_type}",
            )

        # Создаем модель через соответствующий строитель
        model = builder(data)

        # Восстанавливаем оригинальный id
        if item_id and hasattr(model, "id"):
            model.id = item_id
            self.__cache[item_id] = model

        return model

    def _get_builder(self, target_type: type) -> Optional[Callable[[dict], Any]]:
        """Поиск строителя с учетом наследования"""
        if target_type in self.__builders:
            return self.__builders[target_type]
        for reg_type, builder in self.__builders.items():
            if issubclass(target_type, reg_type):
                return builder
        return None

    def _deserialize_field(self, field_data: Any, field_type: Optional[type] = None) -> Any:
        """Рекурсивный вызов десериализации поля через фабрику"""
        if self.__factory is not None:
            return self.__factory.deserialize(field_data, field_type)
        return self.deserialize(field_data, field_type)

    def _build_range(self, data: dict) -> range_model:
        """Построение единицы измерения"""
        name = data.get("name")
        conversion_factor = float(data.get("conversion_factor", 1.0))
        base_range_data = data.get("base_range")
        base_range = None
        if isinstance(base_range_data, dict):
            base_range = self._deserialize_field(base_range_data, range_model)
        return range_model(name=name, conversion_factor=conversion_factor, base_range=base_range)

    def _build_group(self, data: dict) -> nomenclature_group_model:
        """Построение группы номенклатуры"""
        return nomenclature_group_model(name=data.get("name"))

    def _build_storage(self, data: dict) -> storage_model:
        """Построение склада"""
        return storage_model(name=data.get("name"))

    def _build_nomenclature(self, data: dict) -> nomenclature_model:
        """Построение номенклатуры"""
        name = data.get("name")
        full_name = data.get("full_name", name)
        group = self._deserialize_field(data.get("group"), nomenclature_group_model)
        range_unit = self._deserialize_field(data.get("range"), range_model)
        return nomenclature_model(name=name, full_name=full_name, group=group, range_unit=range_unit)

    def _build_recipe_row(self, data: dict) -> recipe_row_model:
        """Построение строки рецепта"""
        nom = self._deserialize_field(data.get("nomenclature"), nomenclature_model)
        brutto = float(data.get("brutto", 0.0))
        netto = float(data.get("netto", brutto))
        range_unit = self._deserialize_field(data.get("range"), range_model)
        
        # Восстановление вложенного рецепта полуфабриката
        sub_recipe_data = data.get("sub_recipe")
        sub_recipe = None
        if isinstance(sub_recipe_data, dict):
            sub_recipe = self._deserialize_field(sub_recipe_data, recipe_model)
        return recipe_row_model(
            nomenclature=nom,
            brutto=brutto,
            netto=netto,
            range_unit=range_unit,
            sub_recipe=sub_recipe,
        )
    def _build_recipe(self, data: dict) -> recipe_model:
        """Построение технологической карты"""
        name = data.get("name")
        dish = self._deserialize_field(data.get("dish"), nomenclature_model)
        cooking_time = int(data.get("cooking_time", 0))
        instructions = data.get("instructions", [])
        portions = int(data.get("portions", 1))

        recipe = recipe_model(
            name=name,
            dish=dish,
            cooking_time=cooking_time,
            instructions=instructions,
            portions=portions,
        )
        for row_dict in data.get("rows", []):
            row = self._deserialize_field(row_dict, recipe_row_model)
            recipe.add_row(row)
        return recipe