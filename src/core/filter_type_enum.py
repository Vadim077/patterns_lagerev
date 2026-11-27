from enum import Enum


"""
Перечисление поддерживаемых операций фильтрации
"""
class filter_type_enum(Enum):
    EQUALS = "EQUALS"
    LIKE = "LIKE"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"

    @classmethod
    def from_string(cls, value: str) -> "filter_type_enum":
        """Преобразование строки в элемент перечисления."""
        if not value or not isinstance(value, str):
            return cls.EQUALS

        val = value.strip().upper()
        mapping = {
            "EQ": cls.EQUALS,
            "EQUALS": cls.EQUALS,
            "LIKE": cls.LIKE,
            "GT": cls.GREATER_THAN,
            "GREATER_THAN": cls.GREATER_THAN,
            "LT": cls.LESS_THAN,
            "LESS_THAN": cls.LESS_THAN,
            "GTE": cls.GREATER_EQUAL,
            "GREATER_EQUAL": cls.GREATER_EQUAL,
            "LTE": cls.LESS_EQUAL,
            "LESS_EQUAL": cls.LESS_EQUAL,
        }
        return mapping.get(val, cls.EQUALS)
