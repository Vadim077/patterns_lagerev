from src.core.abstract_convertor import abstract_convertor
from src.core.abstract_model import abstract_model
from src.core.validator import validator


class reference_convertor(abstract_convertor):
    """
    Конвертор ссылочных типов
    Сериализует ссылку в виде идентификатора id связанной сущности
    """

    def convert(self, source: object) -> dict:
        validator.validate(source)
        result = {}

        for field in self.get_fields(source):
            val = getattr(source, field)
            if isinstance(val, abstract_model):
                result[field] = val.id

        return result