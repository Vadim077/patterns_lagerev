from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.exception import arguments_exception


class reference_deserializer(abstract_deserializer):
    """
    десериализатор
    """

    def __init__(self, service: Optional[abstract_deserialization_context] = None) -> None:
        self.__service = service

    @property
    def service(self) -> Optional[abstract_deserialization_context]:
        return self.__service

    @service.setter
    def service(self, value: Optional[abstract_deserialization_context]) -> None:
        self.__service = value

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Десериализация словаря в экземпляр модели/DTO через ее фабричный метод
        """
        if data is None:
            return None

        if not isinstance(data, dict):
            return None

        # 1. Проверка Identity Cache по id
        item_id = data.get("id")
        cls = target_type
        if cls is None:
            type_name = data.get("type")
            if type_name and self.__service:
                cls = self.__service.get_model_class(type_name)

        if cls is None:
            type_name = data.get("type")
            if type_name:
                raise arguments_exception(field="type", message=f"Неизвестный тип модели: {type_name}")
            return None

        if self.__service and item_id and self.__service.has_cache(cls, item_id):
            return self.__service.get_cache(cls, item_id)

        factory_method = getattr(cls, "create", None)
        if not callable(factory_method):
            raise arguments_exception(field="type", message=f"Тип {cls.__name__} не поддерживает десериализацию")

        return factory_method(data, service=self.__service)
