from src.core.entity_model import entity_model
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.exception import arguments_exception
from typing import Optional

class nomenclature_group_model(entity_model):
    """Модель группы номенклатуры. """

    def __init__(self, name: str = None) -> None:
        """Конструктор группы номенклатуры."""
        super().__init__(name=name)

    """
    Фабричный метод: группа Сырье
    """
    @staticmethod
    def create_raw() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Сырье")

    """
    Фабричный метод: группа Ингредиенты
    """
    @staticmethod
    def create_ingredients() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Ингредиенты")

    """
    Фабричный метод: группа Полуфабрикаты
    """
    @staticmethod
    def create_semi_finished() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Полуфабрикаты")

    """
    Фабричный метод: группа Готовая продукция
    """
    @staticmethod
    def create_products() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Готовая продукция")

    """
    Фабричный метод: группа Упаковка
    """
    @staticmethod
    def create_packaging() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Упаковка")

    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None) -> "nomenclature_group_model":
        """
        Фабричный метод создания группы номенклатуры из словаря
        """
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")
        instance = cls(name=data.get("name"))
        item_id = data.get("id")
        if item_id:
            instance.id = item_id
            if service is not None:
                service.set_cache(cls, item_id, instance)
        return instance
