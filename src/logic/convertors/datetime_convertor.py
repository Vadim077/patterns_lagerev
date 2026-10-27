from datetime import datetime
from src.core.abstract_convertor import abstract_convertor
from src.core.validator import validator


class datetime_convertor(abstract_convertor):
    """
    Конвертор свойств даты и времени в строку
    """

    def convert(self, source: object) -> dict:
        validator.validate(source)
        result = {}

        for field in self.get_fields(source):
            val = getattr(source, field)
            if isinstance(val, datetime):
                result[field] = val.isoformat()

        return result