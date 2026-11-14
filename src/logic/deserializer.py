import json
from typing import Any, Optional
from src.core.abstract_deserialize_factory import abstract_deserialize_factory
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.logic.deserialize_factory import deserialize_factory


class deserializer(abstract_deserialization_context):
    """
    Координатор процесса десериализации
    """

    def __init__(self, factory: Optional[abstract_deserialize_factory] = None) -> None:
        self.__cache: dict[tuple[type, str], object] = {}
        if factory is not None:
            self.__factory = factory
            self.__factory.service = self
        else:
            self.__factory = deserialize_factory(service=self)

    @property
    def factory(self) -> abstract_deserialize_factory:
        return self.__factory

    def has_cache(self, model_type: type, item_id: str) -> bool:
        """Проверка наличия объекта в кэше по id"""
        return (model_type, item_id) in self.__cache

    def get_cache(self, model_type: type, item_id: str) -> Optional[object]:
        """Получение объекта из кэша по id"""
        return self.__cache.get((model_type, item_id))

    def set_cache(self, model_type: type, item_id: str, instance: object) -> None:
        """Сохранение объекта в кэш"""
        self.__cache[(model_type, item_id)] = instance

    def clear_cache(self) -> None:
        """Очистить кэш объектов"""
        self.__cache.clear()

    def get_model_class(self, type_name: str) -> Optional[type]:
        """Получить класс модели или DTO по имени типа через фабрику"""
        return self.__factory.get_model_class(type_name)

    def register_class(self, cls: type) -> None:
        """Зарегистрировать новый класс в безопасном реестре фабрики"""
        self.__factory.register_class(cls)

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Сквозная десериализация элементов, списков или словарей
        """
        if data is None:
            return None

        # 1. Списки элементов
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        # 2. Определение целевого класса
        actual_type = target_type
        if actual_type is None and isinstance(data, dict):
            type_name = data.get("type")
            if type_name:
                actual_type = self.get_model_class(type_name)

        # 3. Подбор десериализатора через фабрику
        handler = self.__factory.create(actual_type or type(data))

        # 4. Делегирование десериализации обработчику
        return handler.deserialize(data, actual_type)

    def deserialize_json(self, json_string: str, target_type: Optional[type] = None) -> Any:
        """Десериализация из JSON-строки"""
        if not json_string or not isinstance(json_string, str):
            raise arguments_exception(field="json_string", message="JSON строка не может быть пустой")
        parsed = json.loads(json_string)
        return self.deserialize(parsed, target_type)

    def deserialize_file(self, file_path: str, target_type: Optional[type] = None) -> Any:
        """Десериализация данных напрямую из JSON файла"""
        validator.validate(file_path, str)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.deserialize(data, target_type)

    def open(self, file_path: str) -> dict:
        """Загрузка сырых данных JSON из файла в виде словаря"""
        validator.validate(file_path, str)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
