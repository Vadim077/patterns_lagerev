from src.core.entity_model import entity_model
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.exception import arguments_exception
from typing import Optional

class storage_model(entity_model):
    """Модель склада"""

    def __init__(self, name: str = None) -> None:
        """Конструктор склада."""
        super().__init__(name=name)

    """
    Фабричный метод: Основной склад
    """
    @staticmethod
    def create_main() -> "storage_model":
        return storage_model(name="Основной склад")

    """
    Фабричный метод: Холодильник
    """
    @staticmethod
    def create_cold() -> "storage_model":
        return storage_model(name="Холодильник")

    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None) -> "storage_model":
        """
        Фабричный метод создания склада из словаря.
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
