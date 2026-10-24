from src.core.abstract_convertor import abstract_convertor
from src.core.validator import validator


class basic_convertor(abstract_convertor):
    """
    Конвертор простых типов данных
    """

    def convert(self, source: object) -> dict:
        validator.validate(source)
        result = {}

        for field in self.get_fields(source):
            val = getattr(source, field)
            
            if isinstance(val, (int, float, str, bool)):
                result[field] = val

        return result