import json
from datetime import date, datetime
from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.core.abstract_model import abstract_model
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.model_deserializer import model_deserializer
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    storage_model,
)


class deserialize_factory:
    """
    Фабрика десериализации данных
    """

    def __init__(self, deserializers: list[abstract_deserializer] = None) -> None:
        self.__basic_deserializer = basic_deserializer()
        self.__datetime_deserializer = datetime_deserializer()
        self.__model_deserializer = model_deserializer(self)

        # Маппинг типов на десериализаторы
        self.__mapping: dict[type, abstract_deserializer] = {
            int: self.__basic_deserializer,
            float: self.__basic_deserializer,
            str: self.__basic_deserializer,
            bool: self.__basic_deserializer,
            datetime: self.__datetime_deserializer,
            date: self.__datetime_deserializer,
            abstract_model: self.__model_deserializer,
            dict: self.__model_deserializer,
        }

        # Маппинг строковых ключей коллекций верхнего уровня на классы моделей
        self.__key_mapping: dict[str, type] = {
            "ranges": range_model,
            "groups": nomenclature_group_model,
            "storages": storage_model,
            "nomenclatures": nomenclature_model,
            "recipes": recipe_model,
        }

        if deserializers is not None:
            self.__deserializers = deserializers
        else:
            self.__deserializers = [
                self.__basic_deserializer,
                self.__datetime_deserializer,
                self.__model_deserializer,
            ]

    @property
    def basic_deserializer(self) -> basic_deserializer:
        return self.__basic_deserializer

    @property
    def datetime_deserializer(self) -> datetime_deserializer:
        return self.__datetime_deserializer

    @property
    def model_deserializer(self) -> model_deserializer:
        return self.__model_deserializer

    def register(self, type_key: type, deserializer: abstract_deserializer) -> None:
        """Регистрация специализированного десериализатора под новый тип"""
        validator.validate(type_key, type)
        validator.validate(deserializer, abstract_deserializer)
        self.__mapping[type_key] = deserializer

    def register_key(self, key: str, model_type: type) -> None:
        """Регистрация связи строкового ключа коллекции с классом модели"""
        validator.validate(key, str)
        validator.validate(model_type, type)
        self.__key_mapping[key.strip().lower()] = model_type

    def create(self, target_type_or_data: Any) -> abstract_deserializer:
        """
        Паттерн 'Фабрика': подбирает нужный экземпляр десериализатора по типу
        """
        if target_type_or_data is None:
            return self.__basic_deserializer

        t = target_type_or_data if isinstance(target_type_or_data, type) else type(target_type_or_data)

        # 1. Прямой поиск в словаре маппинга
        if t in self.__mapping:
            return self.__mapping[t]

        # 2. Поиск по наследованию
        for registered_type, deser in self.__mapping.items():
            if issubclass(t, registered_type):
                return deser

        return self.__basic_deserializer

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Сквозная десериализация структуры данных, коллекций или одиночных объектов
        """
        if data is None:
            return None

        # 1. Списки элементов
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        # 2. Словари
        if isinstance(data, dict):
            # Проверяем: это словарь коллекций верхнего уровня
            is_dump = any(k in self.__key_mapping for k in data) and all(
                isinstance(v, list) for k, v in data.items() if k in self.__key_mapping
            )
            if is_dump and target_type is None:
                res = {}
                for k, v in data.items():
                    model_cls = self.__key_mapping.get(k.lower())
                    if model_cls and isinstance(v, list):
                        res[k] = [self.deserialize(item, model_cls) for item in v]
                    else:
                        res[k] = self.deserialize(v)
                return res

            # Для модели передаем в model_deserializer
            return self.__model_deserializer.deserialize(data, target_type)

        # 3. Примитивы и прочие типы
        deserializer = self.create(target_type or type(data))
        return deserializer.deserialize(data, target_type)

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