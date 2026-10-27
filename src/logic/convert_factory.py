from datetime import date, datetime
from src.core.abstract_convertor import abstract_convertor
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.logic.convertors.basic_convertor import basic_convertor
from src.logic.convertors.datetime_convertor import datetime_convertor
from src.logic.convertors.reference_convertor import reference_convertor


class convert_factory:
    """
    Фабрика конвертации объектов:
    - Подбирает нужный конвертор по типу объекта через словарь маппинга
    """

    def __init__(self, convertors: list[abstract_convertor] = None) -> None:
        self.__basic_convertor = basic_convertor()
        self.__datetime_convertor = datetime_convertor()
        self.__reference_convertor = reference_convertor(self)

        # Маппинг типов на конверторы
        self.__mapping: dict[type, abstract_convertor] = {
            int: self.__basic_convertor,
            float: self.__basic_convertor,
            str: self.__basic_convertor,
            bool: self.__basic_convertor,
            datetime: self.__datetime_convertor,
            date: self.__datetime_convertor,
        }

        if convertors is not None:
            self.__convertors = convertors
        else:
            self.__convertors = [
                self.__basic_convertor,
                self.__datetime_convertor,
                self.__reference_convertor,
            ]

    @property
    def basic_convertor(self) -> basic_convertor:
        return self.__basic_convertor

    @property
    def datetime_convertor(self) -> datetime_convertor:
        return self.__datetime_convertor

    @property
    def reference_convertor(self) -> reference_convertor:
        return self.__reference_convertor

    def register(self, type_key: type, convertor: abstract_convertor) -> None:
        """
        Регистрация конвертора под новый тип данных
        """
        validator.validate(type_key, type)
        validator.validate(convertor, abstract_convertor)
        self.__mapping[type_key] = convertor

    def create(self, value_or_type: object) -> abstract_convertor:
        """
        подбирает нужный экзепляр конвертора по типу
        """
        if value_or_type is None:
            raise arguments_exception(field="value_or_type", message="Объект не может быть None")

        target_type = value_or_type if isinstance(value_or_type, type) else type(value_or_type)

        # 1. Поиск по прямому совпадению в словаре маппинга
        if target_type in self.__mapping:
            return self.__mapping[target_type]

        # 2. Поиск по наследованию типов
        for registered_type, convertor in self.__mapping.items():
            if issubclass(target_type, registered_type):
                return convertor

        # 3. По умолчанию для доменных моделей и сложных структур
        return self.__reference_convertor

    def convert(self, source: object) -> object:
        """
        Сквозная конвертация структуры данных
        """
        if source is None:
            raise arguments_exception(field="source", message="Источник не может быть None")

        # 1. Списки и кортежи
        if isinstance(source, (list, tuple)):
            return [self.convert(item) for item in source]

        # 2. Словари
        if isinstance(source, dict):
            return {str(k): self.convert(v) for k, v in source.items()}

        # 3. Простые типы и даты через маппинг
        src_type = type(source)
        if src_type in self.__mapping:
            convertor = self.__mapping[src_type]
            if isinstance(convertor, datetime_convertor):
                return source.isoformat()
            return source

        # 4. бъединяем поля от конверторов
        result = {}
        for convertor in self.__convertors:
            for field, value in convertor.convert(source).items():
                result[field] = value

        return result