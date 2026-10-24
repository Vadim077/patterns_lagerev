from datetime import datetime
from src.core.abstract_convertor import abstract_convertor
from src.core.validator import validator
from src.logic.convertors.basic_convertor import basic_convertor
from src.logic.convertors.datetime_convertor import datetime_convertor
from src.logic.convertors.reference_convertor import reference_convertor


class convert_factory:
    """
    Фабрика конвертации объектов в формат словарей
    """

    def __init__(self, convertors: list[abstract_convertor] = None) -> None:
        """
        Конструктор фабрики: регистрирует специализированные конверторы по типам
        """
        if convertors is not None:
            self.__convertors = convertors
        else:
            self.__convertors = [
                basic_convertor(),
                datetime_convertor(),
                reference_convertor(),
            ]

    def convert(self, source: object) -> object:
        """
        Метод конвертации:
        - 1. int, float, str, bool -> возвращаются как есть
        - 2. datetime -> ISO 8601 строка
        - 3. list / tuple -> список сконвертированных элементов
        - 4. dict -> словарь со сконвертированными значениями
        - 5. Модели / объекты -> словарь {поле: значение}, собранный через конверторы
        """
        validator.validate(source)

        # 1.
        if isinstance(source, (int, float, str, bool)):
            return source

        # 2
        if isinstance(source, datetime):
            return source.isoformat()

        # 3
        if isinstance(source, (list, tuple)):
            return [self.convert(item) for item in source]

        # 4
        if isinstance(source, dict):
            return {str(key): self.convert(value) for key, value in source.items()}

        # 5
        result = {}
        for convertor in self.__convertors:
            for field, value in convertor.convert(source).items():
                result[field] = value

        # Рекурсивно обрабатываем вложенные списки и словари в свойствах объекта
        for field in abstract_convertor.get_fields(source):
            val = getattr(source, field, None)
            if isinstance(val, (list, tuple)):
                result[field] = [self.convert(item) for item in val]
            elif isinstance(val, dict):
                result[field] = {str(k): self.convert(v) for k, v in val.items()}

        return result