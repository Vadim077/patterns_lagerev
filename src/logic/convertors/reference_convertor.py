from typing import Optional, TYPE_CHECKING
from src.core.abstract_convertor import abstract_convertor
from src.core.abstract_model import abstract_model
from src.core.validator import validator

if TYPE_CHECKING:
    from src.logic.convert_factory import convert_factory


class reference_convertor(abstract_convertor):
    """
    Конвертор ссылочных типов:
    - Вложенные доменные модели
    - Списки, содержащие доменные модели
    - Защита от бесконечной рекурсии при циклических ссылках
    """

    def __init__(self, factory: Optional["convert_factory"] = None) -> None:
        self.__factory = factory
        self.__visited = set()

    @property
    def factory(self) -> Optional["convert_factory"]:
        return self.__factory

    @factory.setter
    def factory(self, value: Optional["convert_factory"]) -> None:
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
                    if val == source or id(val) in self.__visited:
                        result[field] = None
                    else:
                        result[field] = self._convert_item(val)
        finally:
            self.__visited.discard(source_id)

        return result

    def _convert_item(self, item: object) -> object:
        """
        Рекурсивная конвертация элемента-ссылки через фабрику
        """
        if not isinstance(item, abstract_model):
            return item

        # Защита от бесконечного цикла
        if id(item) in self.__visited:
            return None

        if self.__factory is not None:
            return self.__factory.convert(item)

        # Если фабрика не была передана, используем дефолтную фабрику
        from src.logic.convert_factory import convert_factory
        return convert_factory().convert(item)