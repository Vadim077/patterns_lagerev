from datetime import date, datetime
from src.core.abstract_convertor import abstract_convertor
from src.core.abstract_model import abstract_model
from src.core.validator import validator


class reference_convertor(abstract_convertor):
    """
    Конвертор ссылочных типов
    - Вложенные доменные модели
    - Списки, содержащие доменные модели
    - Защита от бесконечной рекурсии
    """

    def __init__(self, factory=None) -> None:
        self.__factory = factory
        self.__visited = set()

    @property
    def factory(self):
        return self.__factory

    @factory.setter
    def factory(self, value):
        self.__factory = value

    def convert(self, source: object) -> dict:
        validator.validate(source)
        result = {}

        source_id = id(source)
        self.__visited.add(source_id)

        try:
            for field in self.get_fields(source):
                val = getattr(source, field)

                # 1. Если свойство - список/кортеж (строки рецепта)
                if isinstance(val, (list, tuple)):
                    result[field] = [self._convert_item(item) for item in val]

                # 2. Если свойство - вложенная доменная модель (range_model)
                elif isinstance(val, abstract_model):
                    result[field] = self._convert_item(val)
        finally:
            self.__visited.discard(source_id)

        return result

    def _convert_item(self, item: object) -> object:
        """
        Рекурсивная конвертация элемента-ссылки
        """
        if not isinstance(item, abstract_model):
            return item

        # Защита от бесконечного цикла
        if id(item) in self.__visited:
            return getattr(item, "id", str(item))

        # Если задана фабрика - используем её для сквозной конвертации
        if self.__factory is not None:
            return self.__factory.convert(item)

        # Автономная конвертация модели со сбором полей
        self.__visited.add(id(item))
        try:
            res = {}
            for f in self.get_fields(item):
                v = getattr(item, f)
                if isinstance(v, (int, float, str, bool)):
                    res[f] = v
                elif isinstance(v, (datetime, date)):
                    res[f] = v.isoformat()
                elif isinstance(v, abstract_model):
                    res[f] = self._convert_item(v)
                elif isinstance(v, (list, tuple)):
                    res[f] = [self._convert_item(x) for x in v]
            return res
        finally:
            self.__visited.discard(id(item))