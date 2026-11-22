from typing import Any, Optional

from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.dtos.filter_item_dto import filter_item_dto


"""
DTO набора правил фильтрации данных
"""
class filter_dto(entity_model):
    __filters: list = None

    def __init__(self, filters: list = None) -> None:
        super().__init__(name="Набор фильтров")
        self.__filters = []
        if filters is not None:
            self.filters = filters

    @property
    def filters(self) -> list:
        """Список правил фильтрации"""
        return self.__filters

    @filters.setter
    def filters(self, source: list) -> None:
        validator.validate(source, list)
        validated = []
        for item in source:
            if isinstance(item, filter_item_dto):
                validated.append(item)
            elif isinstance(item, dict):
                validated.append(filter_item_dto.create(item))
            else:
                raise arguments_exception(field="filters", message="Элемент фильтра должен быть filter_item_dto")
        self.__filters = validated

    def add_filter(self, item: filter_item_dto) -> None:
        """Добавить правило фильтрации"""
        validator.validate(item, filter_item_dto)
        self.__filters.append(item)

    @property
    def is_empty(self) -> bool:
        """Признак отсутствия активных правил фильтрации"""
        return len(self.__filters) == 0

    @classmethod
    def create(cls, data: dict, service: Optional[Any] = None) -> "filter_dto":
        """Фабричный метод создания набора фильтров из словаря"""
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        raw_filters = data.get("filters")
        if raw_filters is None:
            raw_filters = []
            if "name" in data and data["name"] is not None and str(data["name"]).strip():
                name_op = data.get("name_filter_type") or data.get("filter_type") or "LIKE"
                raw_filters.append(filter_item_dto(field_name="name", filter_type=name_op, value=str(data["name"]).strip()))
            if "id" in data and data["id"] is not None and str(data["id"]).strip():
                id_op = data.get("id_filter_type") or "EQUALS"
                raw_filters.append(filter_item_dto(field_name="id", filter_type=id_op, value=str(data["id"]).strip()))
        elif not isinstance(raw_filters, list):
            raise arguments_exception(field="filters", message="Поле filters должно быть списком")

        instance = cls(filters=raw_filters)
        return instance

    def to_dict(self) -> dict:
        """Преобразование DTO в словарь"""
        return {
            "filters": [f.to_dict() for f in self.__filters],
        }
