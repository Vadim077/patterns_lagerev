from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from src.models.nomenclature_group_model import nomenclature_group_model
from src.models.range_model import range_model


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
        self._group: group_model = None
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