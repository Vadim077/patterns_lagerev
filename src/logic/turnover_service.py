import datetime
from typing import Any, Optional, Union

from src.core.common import common
from src.core.filter_type_enum import filter_type_enum
from src.core.validator import validator
from src.dtos.filter_dto import filter_dto
from src.dtos.filter_item_dto import filter_item_dto
from src.dtos.turnover_row_dto import turnover_row_dto
from src.logic.prototype import prototype
from src.logic.storage_manager import storage_manager


"""
Сервис формирования Оборотно-сальдовой ведомости на базе паттерна Прототип
"""
class turnover_service:
    __storage: storage_manager = None

    def __init__(self, storage: storage_manager) -> None:
        validator.validate(storage, storage_manager)
        self.__storage = storage

    """
    Сформировать строки ОСВ с учетом переданных фильтров и периода
    """
    def build(
        self,
        filter_instance: Optional[Union[filter_dto, dict]] = None,
        date_from: Optional[Union[datetime.datetime, datetime.date, str]] = None,
        date_to: Optional[Union[datetime.datetime, datetime.date, str]] = None,
    ) -> list[turnover_row_dto]:
        # Преобразование словаря в DTO при необходимости
        if isinstance(filter_instance, dict):
            filter_instance = filter_dto.create(filter_instance)

        # Извлечение дат из фильтров или параметров
        dt_from, dt_to, other_filters = self.__extract_period_and_filters(
            filter_instance, date_from, date_to
        )

        all_transactions = self.__storage.transactions

        # 1. Применяем прототип для фильтрации по складу, номенклатуре и верхней дате
        non_date_filter = filter_dto(filters=other_filters) if other_filters else None
        filtered_prototype = prototype(all_transactions).clone(non_date_filter)

        # Отсекаем транзакции позже date_to через прототип
        if dt_to is not None:
            upper_date_filter = filter_item_dto(
                field_name="period",
                filter_type=filter_type_enum.LESS_EQUAL,
                value=dt_to,
            )
            filtered_prototype = filtered_prototype.clone(upper_date_filter)

        candidate_transactions = filtered_prototype.data

        # 2. Группировка транзакций по парам (склад, номенклатура)
        grouped_movements: dict[tuple[str, str], list] = {}
        for tx in candidate_transactions:
            if tx.storage and tx.nomenclature:
                key = (tx.storage.id, tx.nomenclature.id)
                grouped_movements.setdefault(key, []).append(tx)

        # 3. Расчет сальдо и оборотов для каждой группы с пересчетом в базовую единицу
        rows: list[turnover_row_dto] = []
        for (storage_id, nomenclature_id), movements in grouped_movements.items():
            first_tx = movements[0]
            storage = first_tx.storage
            nomenclature = first_tx.nomenclature

            # Корневая базовая единица номенклатуры
            base_range = self.__get_base_range(nomenclature.range)

            start_balance = 0.0
            receipts = 0.0
            expenditures = 0.0

            for tx in movements:
                # Пересчет количества в базовую единицу измерения
                factor = tx.range.conversion_factor if tx.range else 1.0
                base_value = tx.value * factor

                # Если транзакция была ДО начала периода - она входит в начальный остаток
                if dt_from is not None and tx.period < dt_from:
                    start_balance += base_value
                else:
                    if base_value > 0:
                        receipts += base_value
                    else:
                        expenditures += abs(base_value)

            end_balance = start_balance + receipts - expenditures

            row = turnover_row_dto(
                storage_id=storage.id,
                storage_name=storage.name,
                nomenclature_id=nomenclature.id,
                nomenclature_name=nomenclature.name,
                range_id=base_range.id if base_range else "",
                range_name=base_range.name if base_range else "",
                start_balance=round(start_balance, 4),
                receipts=round(receipts, 4),
                expenditures=round(expenditures, 4),
                end_balance=round(end_balance, 4),
            )
            rows.append(row)

        return rows

    def __extract_period_and_filters(
        self,
        filter_instance: Optional[filter_dto],
        date_from: Any,
        date_to: Any,
    ) -> tuple[Optional[datetime.datetime], Optional[datetime.datetime], list]:
        """Извлечение дат начала/окончания и оставшихся правил фильтрации"""
        dt_from = self.__parse_datetime(date_from)
        dt_to = self.__parse_datetime(date_to, is_end_of_day=True)
        other_filters: list[filter_item_dto] = []

        if filter_instance is not None:
            for item in filter_instance.filters:
                field = item.field_name.strip().lower()
                op = item.filter_type

                if field in ("period", "date", "period_from", "date_from") and op in (
                    filter_type_enum.GREATER_EQUAL,
                    filter_type_enum.GREATER_THAN,
                    filter_type_enum.EQUALS,
                ):
                    parsed = self.__parse_datetime(item.value)
                    if parsed:
                        dt_from = parsed
                elif field in ("period", "date", "period_to", "date_to") and op in (
                    filter_type_enum.LESS_EQUAL,
                    filter_type_enum.LESS_THAN,
                ):
                    parsed = self.__parse_datetime(item.value, is_end_of_day=True)
                    if parsed:
                        dt_to = parsed
                else:
                    other_filters.append(item)

        return dt_from, dt_to, other_filters

    @staticmethod
    def __parse_datetime(value: Any, is_end_of_day: bool = False) -> Optional[datetime.datetime]:
        """Парсинг произвольного значения даты/времени"""
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            return value

        if isinstance(value, datetime.date):
            time_part = datetime.time.max if is_end_of_day else datetime.time.min
            return datetime.datetime.combine(value, time_part)

        if isinstance(value, str):
            val_str = value.strip()
            try:
                return datetime.datetime.fromisoformat(val_str)
            except Exception:
                try:
                    d = datetime.date.fromisoformat(val_str)
                    time_part = datetime.time.max if is_end_of_day else datetime.time.min
                    return datetime.datetime.combine(d, time_part)
                except Exception:
                    return None

        return None

    @staticmethod
    def __get_base_range(range_obj: Optional[Any]) -> Optional[Any]:
        """Получить корневую базовую единицу измерения номенклатуры"""
        if range_obj is None:
            return None
        current = range_obj
        visited_ids = set()
        while hasattr(current, "base_range") and current.base_range and current.base_range is not current:
            curr_id = id(current)
            if curr_id in visited_ids:
                break
            visited_ids.add(curr_id)
            current = current.base_range
        return current
