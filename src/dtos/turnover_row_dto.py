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

    @property
    def initial_balance(self) -> float:
        """Начальный остаток (бухгалтерский синоним start_balance)"""
        return self.__start_balance

    @property
    def inflow(self) -> float:
        """Приход за период (бухгалтерский синоним receipts)"""
        return self.__receipts

    @property
    def outflow(self) -> float:
        """Расход за период (бухгалтерский синоним expenditures)"""
        return self.__expenditures

    @property
    def final_balance(self) -> float:
        """Конечный остаток (бухгалтерский синоним end_balance)"""
        return self.__end_balance

    @classmethod
    def create(cls, data: dict, service: Optional[Any] = None) -> "turnover_row_dto":
        """Фабричный метод создания строки ОСВ из словаря"""
        if data is None or not isinstance(data, dict):
            raise arguments_exception(field="data", message="Данные должны быть словарем")

        storage_data = data.get("storage")
        storage_id = data.get("storage_id") or (storage_data.get("id") if isinstance(storage_data, dict) else "")
        storage_name = data.get("storage_name") or (storage_data.get("name") if isinstance(storage_data, dict) else "")

        nom_data = data.get("nomenclature")
        nom_id = data.get("nomenclature_id") or (nom_data.get("id") if isinstance(nom_data, dict) else "")
        nom_name = data.get("nomenclature_name") or (nom_data.get("name") if isinstance(nom_data, dict) else "")

        range_data = data.get("range")
        range_id = data.get("range_id") or (range_data.get("id") if isinstance(range_data, dict) else "")
        range_name = data.get("range_name") or (range_data.get("name") if isinstance(range_data, dict) else "")

        start_bal = data.get("start_balance") if data.get("start_balance") is not None else data.get("initial_balance", 0.0)
        rec = data.get("receipts") if data.get("receipts") is not None else data.get("inflow", 0.0)
        exp = data.get("expenditures") if data.get("expenditures") is not None else data.get("outflow", 0.0)
        end_bal = data.get("end_balance") if data.get("end_balance") is not None else data.get("final_balance", 0.0)

        return cls(
            storage_id=str(storage_id or ""),
            storage_name=str(storage_name or ""),
            nomenclature_id=str(nom_id or ""),
            nomenclature_name=str(nom_name or ""),
            range_id=str(range_id or ""),
            range_name=str(range_name or ""),
            start_balance=float(start_bal),
            receipts=float(rec),
            expenditures=float(exp),
            end_balance=float(end_bal),
        )

    def to_dict(self) -> dict:
        """Преобразование DTO в словарь"""
        return {
            "storage_id": self.__storage_id,
            "storage_name": self.__storage_name,
            "storage": {
                "id": self.__storage_id,
                "name": self.__storage_name,
            },
            "nomenclature_id": self.__nomenclature_id,
            "nomenclature_name": self.__nomenclature_name,
            "nomenclature": {
                "id": self.__nomenclature_id,
                "name": self.__nomenclature_name,
            },
            "range_id": self.__range_id,
            "range_name": self.__range_name,
            "range": {
                "id": self.__range_id,
                "name": self.__range_name,
            },
            "start_balance": self.__start_balance,
            "initial_balance": self.__start_balance,
            "receipts": self.__receipts,
            "inflow": self.__receipts,
            "expenditures": self.__expenditures,
            "outflow": self.__expenditures,
            "end_balance": self.__end_balance,
            "final_balance": self.__end_balance,
        }
