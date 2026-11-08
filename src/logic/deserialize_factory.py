from datetime import date, datetime
from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.core.validator import validator
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.nomenclature_deserializer import nomenclature_deserializer
from src.logic.deserializers.nomenclature_group_deserializer import nomenclature_group_deserializer
from src.logic.deserializers.range_deserializer import range_deserializer
from src.logic.deserializers.recipe_deserializer import recipe_deserializer
from src.logic.deserializers.recipe_row_deserializer import recipe_row_deserializer
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    storage_model,
)
from src.logic.deserializers.storage_deserializer import storage_deserializer
from src.core.abstract_deserialize_factory import abstract_deserialize_factory

class deserialize_factory(abstract_deserialize_factory):

    """
    Фабрика десериализаторов
    """

    def __init__(self, service: Optional[Any] = None) -> None:
        self.__service = service
        self.__basic_deserializer = basic_deserializer()
        self.__datetime_deserializer = datetime_deserializer()

        self.__range_deserializer = range_deserializer(service)
        self.__group_deserializer = nomenclature_group_deserializer(service)
        self.__storage_deserializer = storage_deserializer(service)
        self.__nomenclature_deserializer = nomenclature_deserializer(service)
        self.__recipe_row_deserializer = recipe_row_deserializer(service)
        self.__recipe_deserializer = recipe_deserializer(service)

        # Реестр специализированных десериализаторов по типам
        self._maps: dict[type, abstract_deserializer] = {
            int: self.__basic_deserializer,
            float: self.__basic_deserializer,
            str: self.__basic_deserializer,
            bool: self.__basic_deserializer,
            datetime: self.__datetime_deserializer,
            date: self.__datetime_deserializer,
            range_model: self.__range_deserializer,
            nomenclature_group_model: self.__group_deserializer,
            storage_model: self.__storage_deserializer,
            nomenclature_model: self.__nomenclature_deserializer,
            recipe_row_model: self.__recipe_row_deserializer,
            recipe_model: self.__recipe_deserializer,
        }

    @property
    def service(self) -> Optional[Any]:
        return self.__service

    @service.setter
    def service(self, value: Optional[Any]) -> None:
        self.__service = value
        # Обновляем ссылку на сервис у десериализаторов моделей
        self.__range_deserializer = range_deserializer(value)
        self.__group_deserializer = nomenclature_group_deserializer(value)
        self.__storage_deserializer = storage_deserializer(value)
        self.__nomenclature_deserializer = nomenclature_deserializer(value)
        self.__recipe_row_deserializer = recipe_row_deserializer(value)
        self.__recipe_deserializer = recipe_deserializer(value)
        self._maps[range_model] = self.__range_deserializer
        self._maps[nomenclature_group_model] = self.__group_deserializer
        self._maps[storage_model] = self.__storage_deserializer
        self._maps[nomenclature_model] = self.__nomenclature_deserializer
        self._maps[recipe_row_model] = self.__recipe_row_deserializer
        self._maps[recipe_model] = self.__recipe_deserializer

    def register(self, type_key: type, handler: abstract_deserializer) -> None:
        """Регистрация нового десериализатора под пользовательский тип"""
        validator.validate(type_key, type)
        validator.validate(handler, abstract_deserializer)
        self._maps[type_key] = handler

    def create(self, target_type_or_data: Any) -> abstract_deserializer:
        """
        Паттерн 'Фабрика': подбирает нужный экземпляр десериализатора по типу
        """
        if target_type_or_data is None:
            return self.__basic_deserializer

        t = target_type_or_data if isinstance(target_type_or_data, type) else type(target_type_or_data)

        # 1. Прямой поиск типа в реестре
        if t in self._maps:
            return self._maps[t]

        # 2. Поиск с учетом наследования
        for registered_type, handler in self._maps.items():
            if issubclass(t, registered_type):
                return handler

        return self.__basic_deserializer