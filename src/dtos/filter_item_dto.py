from typing import Any, Optional

from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from src.core.filter_type_enum import filter_type_enum
from src.core.validator import validator


"""
DTO одного правила фильтрации по полю модели
"""
class filter_item_dto(entity_model):
    __field_name: str = ""
    __filter_type: filter_type_enum = filter_type_enum.EQUALS
    __value: Any = None

    def __init__(
        self,
        field_name: str = "",
        filter_type: filter_type_enum = filter_type_enum.EQUALS,
        value: Any = None,
    ) -> None:
        super().__init__(name="Правило фильтрации")
        if field_name:
            self.field_name = field_name
        self.filter_type = filter_type
        self.value = value

    @property
    def field_name(self) -> str:
        """Имя поля для фильтрации (поддерживает точечную нотацию)"""
        return self.__field_name

    @field_name.setter
    def field_name(self, source: str) -> None:
        validator.validate(source, str)
        if not source.strip():
            raise arguments_exception(field="field_name", message="Имя поля не может быть пустым")
        self.__field_name = source.strip()

    @property
    def filter_type(self) -> filter_type_enum:
        """Операция фильтрации"""
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, source: Any) -> None:
        if isinstance(source, str):
            self.__filter_type = filter_type_enum.from_string(source)
        elif isinstance(source, filter_type_enum):
            self.__filter_type = source
        else:
            raise arguments_exception(field="filter_type", message="Некорректный тип операции фильтрации")

    @property
    def value(self) -> Any:
        """Значение для сравнения"""
        return self.__value

    @value.setter
    def value(self, source: Any) -> None:
        self.__value = source

    @classmethod
    def create(cls, data: dict, service: Optional[Any] = None) -> "filter_item_dto":
        """Фабричный метод создания правила фильтрации из словаря"""
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        field_name = data.get("field_name") or data.get("field", "")
        filter_type = data.get("filter_type") or data.get("operator", "EQUALS")
        val = data.get("value")

        instance = cls(
            field_name=str(field_name) if field_name else "",
            filter_type=filter_type,
            value=val,
        )
        return instance

    def to_dict(self) -> dict:
        """Преобразование DTO в словарь"""
        return {
            "field_name": self.__field_name,
            "filter_type": self.__filter_type.value,
            "value": self.__value,
        }
