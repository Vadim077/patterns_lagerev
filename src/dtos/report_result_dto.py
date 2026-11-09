from src.core.entity_model import entity_model
from src.core.validator import validator
from typing import Optional
from src.core.exception import arguments_exception
from src.core.abstract_deserialization_context import abstract_deserialization_context

"""
Модель для хранения результата формирования отчета
"""
class report_result_dto(entity_model):
    __text: str = ""
    __binary: list

    def __init__(self, text: str = "", binary: list = []):
        self.__text = text if len(binary) == 0 else ""
        self.__binary = binary if len(text.strip()) == 0 else []

    """
    Текстовый результат
    """
    @property
    def text(self) -> str:
        return self.__text

    """
    Бинарный результат
    """

    @property
    def binary(self) -> list:
        return self.__binary

    @text.setter
    def text(self, value: str) -> None:
        validator.validate(value, str)
        self.__text = value
        self.__binary = []
    @binary.setter
    def binary(self, value: list) -> None:
        validator.validate(value, list)
        self.__binary = value
        if len(value) > 0:
            self.__text = ""

    @classmethod
    def create(cls, data: dict, service: Optional[abstract_deserialization_context] = None) -> "report_result_dto":
        """
        Фабричный метод создания DTO результата отчета из словаря
        """
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")
        text = data.get("text", "")
        binary = data.get("binary", [])
        instance = cls(text=text, binary=binary)
        name = data.get("name")
        if name:
            instance.name = name
        item_id = data.get("id")
        if item_id:
            instance.id = item_id
            if service is not None:
                service.set_cache(cls, item_id, instance)
        return instance
