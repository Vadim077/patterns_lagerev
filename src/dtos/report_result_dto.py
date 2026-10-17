from src.core.entity_model import entity_model
from src.core.validator import validator

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