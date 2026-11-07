from datetime import date, datetime
from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer
from src.core.exception import arguments_exception


class datetime_deserializer(abstract_deserializer):
    """
    Десериализатор даты и времени из строк формата ISO 8601
    """

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Optional[datetime | date]:
        """
        Преобразование ISO-строки в объект datetime или date
        """
        if data is None:
            return None

        if isinstance(data, (datetime, date)):
            return data

        if isinstance(data, str):
            clean_str = data.strip()
            if not clean_str:
                return None
            try:
                # Преобразуем ISO строку
                parsed_dt = datetime.fromisoformat(clean_str)
                if target_type is date and not issubclass(target_type, datetime):
                    return parsed_dt.date()
                return parsed_dt
            except ValueError:
                raise arguments_exception(
                    field="datetime",
                    message=f"Невозможно преобразовать строку '{data}' в дату/время ISO 8601",
                )

        raise arguments_exception(
            field="datetime",
            message=f"Некорректный тип для даты: {type(data)}",
        )