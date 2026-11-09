from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from src.models.nomenclature_group_model import nomenclature_group_model
from src.models.range_model import range_model
from typing import Optional
from src.core.abstract_deserialization_context import abstract_deserialization_context

class nomenclature_model(entity_model):
    """
    Модель номенклатуры.
    Содержит:
    - обычное наименование (до 50 символов, унаследовано);
    - полное наименование (до 255 символов);
    - группу номенклатуры (group_model);
    - единицу измерения (range_model).
    """

    def __init__(
        self,
        name: str = None,
        full_name: str = None,
        group: nomenclature_group_model = None,
        range_unit: range_model = None,
    ) -> None:
        """Конструктор номенклатуры."""
        super().__init__(name=name)
        self._full_name: str = ""
        self._group: nomenclature_group_model = None
        self._range: range_model = None

        if full_name is not None:
            self.full_name = full_name
        if group is not None:
            self.group = group
        if range_unit is not None:
            self.range = range_unit

    @property
    def full_name(self) -> str:
        """Получить полное наименование."""
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """Установить полное наименование (до 255 символов, п. 7 ТЗ)."""
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception(
                field="full_name",
                message="Полное наименование не может быть пустым",
            )
        cleaned = value.strip()
        if len(cleaned) > 255:
            raise arguments_exception(
                field="full_name",
                message="Полное наименование не должно превышать 255 символов",
            )
        self._full_name = cleaned

    @property
    def group(self) -> nomenclature_group_model:
        """Получить группу номенклатуры (п. 8 ТЗ)."""
        return self._group

    @group.setter
    def group(self, value: nomenclature_group_model) -> None:
        """Установить группу номенклатуры."""
        if value is not None and not isinstance(value, nomenclature_group_model):
            raise arguments_exception(
                field="group",
                message="Группа номенклатуры должна быть объектом group_model",
            )
        self._group = value

    @property
    def range(self) -> range_model:
        """Получить единицу измерения (п. 8 ТЗ)."""
        return self._range

    @range.setter
    def range(self, value: range_model) -> None:
        """Установить единицу измерения."""
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception(
                field="range",
                message="Единица измерения должна быть объектом range_model",
            )
        self._range = value

    """
    Фабричный метод: Мука
    """
    @staticmethod
    def create_flour(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Мука",
            full_name="Мука пшеничная высший сорт ГОСТ",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Сахар
    """
    @staticmethod
    def create_sugar(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Сахар",
            full_name="Сахар белый свекловичный ГОСТ",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Масло
    """
    @staticmethod
    def create_butter(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Масло",
            full_name="Масло сливочное 82.5% ГОСТ",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Яйцо
    """
    @staticmethod
    def create_egg(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Яйцо",
            full_name="Яйцо куриное столовое С0",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Песочное тесто (полуфабрикат)
    """
    @staticmethod
    def create_dough(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Песочное тесто",
            full_name="Тесто песочное охлажденное полуфабрикат",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Песочное печенье «Ромашка» (готовое блюдо)
    """
    @staticmethod
    def create_cookie(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Печенье Ромашка",
            full_name="Песочное печенье «Ромашка» ГОСТ",
            group=group,
            range_unit=range_unit,
        )

    """
    Фабричный метод: Картонная коробка (упаковка)
    """
    @staticmethod
    def create_packaging_box(group: nomenclature_group_model, range_unit: range_model) -> "nomenclature_model":
        return nomenclature_model(
            name="Коробка",
            full_name="Коробка картонная крафтовая для печенья",
            group=group,
            range_unit=range_unit,
        )
    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None) -> "nomenclature_model":
        """
        Фабричный метод создания номенклатуры из словаря
        """
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        instance = cls(
            name=data.get("name"),
            full_name=data.get("full_name"),
        )
        item_id = data.get("id")
        if item_id:
            instance.id = item_id
            if service is not None:
                service.set_cache(cls, item_id, instance)

        group_data = data.get("group")
        if isinstance(group_data, dict):
            if service is not None:
                instance.group = service.deserialize(group_data, nomenclature_group_model)
            else:
                instance.group = nomenclature_group_model.create(group_data, service=None)

        range_data = data.get("range")
        if isinstance(range_data, dict):
            if service is not None:
                instance.range = service.deserialize(range_data, range_model)
            else:
                instance.range = range_model.create(range_data, service=None)
        return instance
