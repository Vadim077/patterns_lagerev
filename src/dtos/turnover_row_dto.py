from typing import Any, Optional

from src.core.entity_model import entity_model
from src.core.exception import arguments_exception
from src.core.validator import validator


"""
Строка Оборотно-сальдовой ведомости (ОСВ) по складу и номенклатуре
"""
class turnover_row_dto(entity_model):
    __storage_id: str = ""
    __storage_name: str = ""
    __nomenclature_id: str = ""
    __nomenclature_name: str = ""
    __range_id: str = ""
    __range_name: str = ""
    __start_balance: float = 0.0
    __receipts: float = 0.0
    __expenditures: float = 0.0
    __end_balance: float = 0.0

    def __init__(
        self,
        storage_id: str = "",
        storage_name: str = "",
        nomenclature_id: str = "",
        nomenclature_name: str = "",
        range_id: str = "",
        range_name: str = "",
        start_balance: float = 0.0,
        receipts: float = 0.0,
        expenditures: float = 0.0,
        end_balance: float = 0.0,
    ) -> None:
        super().__init__(name="Строка ОСВ")
        self.__storage_id = storage_id
        self.__storage_name = storage_name
        self.__nomenclature_id = nomenclature_id
        self.__nomenclature_name = nomenclature_name
        self.__range_id = range_id
        self.__range_name = range_name
        self.__start_balance = float(start_balance)
        self.__receipts = float(receipts)
        self.__expenditures = float(expenditures)
        self.__end_balance = float(end_balance)

    @property
    def storage_id(self) -> str:
        """Идентификатор склада"""
        return self.__storage_id

    @storage_id.setter
    def storage_id(self, source: str) -> None:
        validator.validate(source, str)
        self.__storage_id = source

    @property
    def storage_name(self) -> str:
        """Наименование склада"""
        return self.__storage_name

    @storage_name.setter
    def storage_name(self, source: str) -> None:
        validator.validate(source, str)
        self.__storage_name = source

    @property
    def nomenclature_id(self) -> str:
        """Идентификатор номенклатуры"""
        return self.__nomenclature_id

    @nomenclature_id.setter
    def nomenclature_id(self, source: str) -> None:
        validator.validate(source, str)
        self.__nomenclature_id = source

    @property
    def nomenclature_name(self) -> str:
        """Наименование номенклатуры"""
        return self.__nomenclature_name

    @nomenclature_name.setter
    def nomenclature_name(self, source: str) -> None:
        validator.validate(source, str)
        self.__nomenclature_name = source

    @property
    def range_id(self) -> str:
        """Идентификатор единицы измерения"""
        return self.__range_id

    @range_id.setter
    def range_id(self, source: str) -> None:
        validator.validate(source, str)
        self.__range_id = source

    @property
    def range_name(self) -> str:
        """Наименование единицы измерения"""
        return self.__range_name

    @range_name.setter
    def range_name(self, source: str) -> None:
        validator.validate(source, str)
        self.__range_name = source

    @property
    def start_balance(self) -> float:
        """Начальный остаток на начало периода"""
        return self.__start_balance

    @start_balance.setter
    def start_balance(self, source: float) -> None:
        validator.validate(source, (int, float))
        self.__start_balance = float(source)

    @property
    def receipts(self) -> float:
        """Поступление за период"""
        return self.__receipts

    @receipts.setter
    def receipts(self, source: float) -> None:
        validator.validate(source, (int, float))
        self.__receipts = float(source)

    @property
    def expenditures(self) -> float:
        """Расход за период"""
        return self.__expenditures

    @expenditures.setter
    def expenditures(self, source: float) -> None:
        validator.validate(source, (int, float))
        self.__expenditures = float(source)

    @property
    def end_balance(self) -> float:
        """Конечный остаток на конец периода"""
        return self.__end_balance

    @end_balance.setter
    def end_balance(self, source: float) -> None:
        validator.validate(source, (int, float))
        self.__end_balance = float(source)

    @classmethod
    def create(cls, data: dict, service: Optional[Any] = None) -> "turnover_row_dto":
        """Фабричный метод создания строки ОСВ из словаря"""
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        return cls(
            storage_id=str(data.get("storage_id", "")),
            storage_name=str(data.get("storage_name", "")),
            nomenclature_id=str(data.get("nomenclature_id", "")),
            nomenclature_name=str(data.get("nomenclature_name", "")),
            range_id=str(data.get("range_id", "")),
            range_name=str(data.get("range_name", "")),
            start_balance=float(data.get("start_balance", 0.0)),
            receipts=float(data.get("receipts", 0.0)),
            expenditures=float(data.get("expenditures", 0.0)),
            end_balance=float(data.get("end_balance", 0.0)),
        )

    def to_dict(self) -> dict:
        """Преобразование DTO в словарь"""
        return {
            "storage_id": self.__storage_id,
            "storage_name": self.__storage_name,
            "nomenclature_id": self.__nomenclature_id,
            "nomenclature_name": self.__nomenclature_name,
            "range_id": self.__range_id,
            "range_name": self.__range_name,
            "start_balance": self.__start_balance,
            "receipts": self.__receipts,
            "expenditures": self.__expenditures,
            "end_balance": self.__end_balance,
        }
