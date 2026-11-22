from typing import Optional, Union
from src.core.abstract_prototype import abstract_prototype
from src.core.common import common
from src.core.validator import validator
from src.dtos.filter_dto import filter_dto
from src.dtos.filter_item_dto import filter_item_dto


"""
Универсальная реализация паттерна 'Прототип' для фильтрации данных
"""
class prototype(abstract_prototype):
    __data: list = []

    def __init__(self, data: Union[list, tuple]) -> None:
        validator.validate(data, (list, tuple))
        self.__data = list(data)

    """
    Набор данных текущего прототипа
    """
    @property
    def data(self) -> list:
        return self.__data

    """
    Клонировать прототип с применением фильтрации
    Возвращает новый экземпляр prototype с отфильтрованными данными
    """
    def clone(self, filter_instance: Optional[Union[filter_dto, filter_item_dto]] = None) -> "prototype":
        if filter_instance is None:
            return prototype(list(self.__data))

        # Если передан единичный filter_item_dto
        if isinstance(filter_instance, filter_item_dto):
            rules = [filter_instance]
        elif isinstance(filter_instance, filter_dto):
            rules = filter_instance.filters
        else:
            return prototype(list(self.__data))

        current_data = list(self.__data)

        # Последовательное применение каждого правила фильтрации
        for rule in rules:
            filtered_subset = []
            for item in current_data:
                field_values = common.get_values_by_path(item, rule.field_name)
                # Если хотя бы одно значение по пути удовлетворяет условию
                if any(common.match_value(val, rule.value, rule.filter_type) for val in field_values):
                    filtered_subset.append(item)

            current_data = filtered_subset

        return prototype(current_data)
