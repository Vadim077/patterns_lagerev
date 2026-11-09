from datetime import date, datetime
from typing import Any, Optional
from src.core.abstract_deserialize_factory import abstract_deserialize_factory
from src.core.abstract_deserialization_context import abstract_deserialization_context
from src.core.abstract_deserializer import abstract_deserializer
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.reference_deserializer import reference_deserializer
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    storage_model,
)

class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика десериализаторов
    """

    def __init__(self, service: Optional[abstract_deserialization_context] = None) -> None:
        self.__service = service
        self.__basic_deserializer = basic_deserializer()
        self.__datetime_deserializer = datetime_deserializer()
        self.__reference_deserializer = reference_deserializer(service)

        # Маппинг примитивных типов на специализированные десериализаторы
        self._maps: dict[type, abstract_deserializer] = {
            int: self.__basic_deserializer,
            float: self.__basic_deserializer,
            str: self.__basic_deserializer,
            bool: self.__basic_deserializer,
            datetime: self.__datetime_deserializer,
            date: self.__datetime_deserializer,
        }

        # Безопасный реестр
        self._classes: dict[str, type] = {
            range_model.__name__: range_model,
            nomenclature_group_model.__name__: nomenclature_group_model,
            storage_model.__name__: storage_model,
            nomenclature_model.__name__: nomenclature_model,
            recipe_row_model.__name__: recipe_row_model,
            recipe_model.__name__: recipe_model,
            report_result_dto.__name__: report_result_dto,
        }

    @property
    def service(self) -> Optional[abstract_deserialization_context]:
        return self.__service

    @service.setter
    def service(self, value: Optional[abstract_deserialization_context]) -> None:
        self.__service = value
        self.__reference_deserializer.service = value

    @property
    def basic_deserializer(self) -> basic_deserializer:
        return self.__basic_deserializer

    @property
    def datetime_deserializer(self) -> datetime_deserializer:
        return self.__datetime_deserializer

    @property
    def reference_deserializer(self) -> reference_deserializer:
        return self.__reference_deserializer

    def register_class(self, cls: type) -> None:
        """Регистрация класса модели или DTO в реестре разрешенных типов"""
        validator.validate(cls, type)
        self._classes[cls.__name__] = cls

    def get_model_class(self, type_name: str) -> Optional[type]:
        """Получить класс модели или DTO по строковому имени типа"""
        return self._classes.get(type_name)

    def register(self, type_key: type, handler: abstract_deserializer) -> None:
        """Регистрация пользовательского десериализатора под конкретный тип"""
        validator.validate(type_key, type)
        validator.validate(handler, abstract_deserializer)
        self._maps[type_key] = handler

    def create(self, target_type_or_data: Any) -> abstract_deserializer:
        """
        Паттерн 'Фабрика': подбирает десериализатор по типу целевого объекта
        """
        if target_type_or_data is None:
            return self.__basic_deserializer

        t = target_type_or_data if isinstance(target_type_or_data, type) else type(target_type_or_data)

        # 1. Прямой поиск типа в маппинге примитивов
        if t in self._maps:
            return self._maps[t]

        # 2. Поиск с учетом наследования
        for registered_type, handler in self._maps.items():
            if isinstance(t, type) and issubclass(t, registered_type):
                return handler

        # 3. Для всех доменных моделей и DTO используется reference_deserializer
        return self.__reference_deserializer
