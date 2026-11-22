import datetime
from typing import Optional

from src.core.abstract_model import abstract_model
from src.core.validator import validator, arguments_exception
from src.models.range_model import range_model
from src.models.storage_model import storage_model
from src.models.nomenclature_model import nomenclature_model


"""
Модель складской транзакции (движение товаров)
"""
class transaction_model(abstract_model):
    __range: range_model = None
    __storage: storage_model = None
    __nomenclature: nomenclature_model = None
    __value: float = 0.0
    __period: datetime.datetime = None

    def __init__(self, name: str = None) -> None:
        super().__init__(name=name or "Складская транзакция")

    @property
    def range(self) -> range_model:
        """Единица измерения транзакции"""
        return self.__range

    @range.setter
    def range(self, source: range_model) -> None:
        validator.validate(source, range_model)
        self.__range = source

    @property
    def storage(self) -> storage_model:
        """Склад транзакции"""
        return self.__storage

    @storage.setter
    def storage(self, source: storage_model) -> None:
        validator.validate(source, storage_model)
        self.__storage = source

    @property
    def nomenclature(self) -> nomenclature_model:
        """Номенклатура транзакции"""
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, source: nomenclature_model) -> None:
        validator.validate(source, nomenclature_model)
        self.__nomenclature = source

    @property
    def period(self) -> datetime.datetime:
        """Период (дата и время) транзакции"""
        return self.__period

    @period.setter
    def period(self, source: datetime.datetime) -> None:
        if source is None or not isinstance(source, (datetime.datetime, datetime.date)):
            raise arguments_exception(field="period", message="Некорректная дата транзакции")
        if isinstance(source, datetime.date) and not isinstance(source, datetime.datetime):
            source = datetime.datetime.combine(source, datetime.time.min)
        self.__period = source

    @property
    def value(self) -> float:
        """Количество (+ поступление, - списание)"""
        return self.__value

    @value.setter
    def value(self, source: float) -> None:
        if source is None or not isinstance(source, (int, float)) or isinstance(source, bool):
            raise arguments_exception(field="value", message="Значение должно быть числом")
        float_val = float(source)
        if float_val == 0.0:
            raise arguments_exception(field="value", message="Значение не может быть равно 0")
        self.__value = float_val

    @classmethod
    def create(cls, data: dict, service = None):
        """Фабричный метод создания экземпляра транзакции из словаря"""
        instance = super().create(data, service)
        if not isinstance(data, dict):
            return instance

        val = data.get("value")
        if val is not None and val != 0:
            instance.value = float(val)

        period_raw = data.get("period")
        if period_raw is not None:
            if isinstance(period_raw, str):
                try:
                    instance.period = datetime.datetime.fromisoformat(period_raw)
                except Exception:
                    pass
            elif isinstance(period_raw, (datetime.datetime, datetime.date)):
                instance.period = period_raw

        storage_data = data.get("storage")
        if storage_data is not None:
            if service and isinstance(storage_data, dict):
                instance.storage = service.deserialize(storage_data, storage_model)
            elif isinstance(storage_data, storage_model):
                instance.storage = storage_data

        nomenclature_data = data.get("nomenclature")
        if nomenclature_data is not None:
            if service and isinstance(nomenclature_data, dict):
                instance.nomenclature = service.deserialize(nomenclature_data, nomenclature_model)
            elif isinstance(nomenclature_data, nomenclature_model):
                instance.nomenclature = nomenclature_data

        range_data = data.get("range")
        if range_data is not None:
            if service and isinstance(range_data, dict):
                instance.range = service.deserialize(range_data, range_model)
            elif isinstance(range_data, range_model):
                instance.range = range_data

        return instance
