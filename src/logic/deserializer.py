import json
from typing import Any, Optional
from src.core.abstract_deserialize_factory import abstract_deserialize_factory
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.logic.deserialize_factory import deserialize_factory
class deserializer:
    """
    Координатор процесса десериализации
    """
    def __init__(self, factory: Optional[abstract_deserialize_factory] = None) -> None:
        self.__cache: dict[str, Any] = {}
        if factory is not None:
            self.__factory = factory
            if hasattr(self.__factory, "service"):
                self.__factory.service = self
        else:
            self.__factory = deserialize_factory(service=self)
    @property
    def factory(self) -> abstract_deserialize_factory:
        return self.__factory

    def has_cache(self, item_id: str) -> bool:
        """Проверка наличия объекта в кэше по id"""
        return item_id in self.__cache

    def get_cache(self, item_id: str) -> Optional[Any]:
        """Получение объекта из кэша по id"""
        return self.__cache.get(item_id)

    def set_cache(self, item_id: str, instance: Any) -> None:
        """Сохранение объекта в кэш"""
        self.__cache[item_id] = instance

    def clear_cache(self) -> None:
        """Очистить кэш объектов"""
        self.__cache.clear()

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Сквозная десериализация элементов, списков или словарей
        """
        if data is None:
            return None

        # 1. Списки элементов
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        # 2. Получение десериализатора через фабрику
        actual_type = target_type or type(data)
        handler = self.__factory.create(actual_type)

        # 3. Делегирование десериализации специализированному обработчику
        return handler.deserialize(data, target_type)

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