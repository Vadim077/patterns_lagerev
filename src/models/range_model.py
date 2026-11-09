from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from typing import Optional
from src.core.abstract_deserialization_context import abstract_deserialization_context

class range_model(entity_model):
    """
    Модель единицы измерения.
    Содержит базовую единицу измерения и коэффициент пересчета.
    """

    def __init__(
        self,
        name: str = None,
        conversion_factor: float = 1.0,
        base_range: "range_model" = None,
    ) -> None:
        """
        Конструктор единицы измерения.

        :param name: наименование (до 50 символов)
        :param conversion_factor: коэффициент пересчета (> 0)
        :param base_range: ссылка на базовую единицу (если None, указывает на себя)
        """
        super().__init__(name=name)
        self._conversion_factor: float = 1.0
        self._base_range: "range_model" = None

        self.conversion_factor = conversion_factor
        self.base_range = base_range

    @property
    def conversion_factor(self) -> float:
        """Получить коэффициент пересчета."""
        return self._conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: float) -> None:
        """Установить коэффициент пересчета с валидацией (> 0)."""
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise arguments_exception(
                field="conversion_factor",
                message="Коэффициент пересчета должен быть положительным числом",
            )
        self._conversion_factor = float(value)

    @property
    def base_range(self) -> "range_model":
        """Получить базовую единицу измерения."""
        return self._base_range

    @base_range.setter
    def base_range(self, value: "range_model") -> None:
        """
        Установить базовую единицу измерения.
        Если передано None, базовой единицей считается сам объект.
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception(
                field="base_range",
                message="Базовая единица измерения должна быть объектом range_model",
            )
        self._base_range = value if value is not None else self

    """
    Фабричный метод: создать килограмм с базовой единицей грамм
    """
    @staticmethod
    def create_kilogramm() -> "range_model":
        gram = range_model(name="грамм", conversion_factor=1.0)
        return range_model(name="кг", conversion_factor=1000.0, base_range=gram)

    """
    Фабричный метод: создать грамм
    """
    @staticmethod
    def create_gram() -> "range_model":
        return range_model(name="грамм", conversion_factor=1.0)

    """
    Фабричный метод: создать штуку
    """
    @staticmethod
    def create_piece() -> "range_model":
        return range_model(name="штука", conversion_factor=1.0)

    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None) -> "range_model":
        """
        Фабричный метод создания единицы измерения из словаря.
        """
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        name = data.get("name")
        conversion_factor = float(data.get("conversion_factor", 1.0))

        instance = cls(name=name, conversion_factor=conversion_factor, base_range=None)
        item_id = data.get("id")
        if item_id:
            instance.id = item_id
            if service is not None:
                service.set_cache(cls, item_id, instance)

        base_range_data = data.get("base_range")
        if isinstance(base_range_data, dict):
            if service is not None:
                instance.base_range = service.deserialize(base_range_data, cls)
            else:
                instance.base_range = cls.create(base_range_data, service=None)
        return instance
