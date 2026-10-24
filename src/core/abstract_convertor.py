from abc import ABC, abstractmethod


class abstract_convertor(ABC):
    """
    Абстрактный базовый класс конвертора объекта в словарь
    """

    @abstractmethod
    def convert(self, source: object) -> dict:
        """
        Преобразование объекта в словарь
        """
        pass

    @staticmethod
    def get_fields(source: object, exclude: tuple = ()) -> list[str]:
        """
        Получение списка свойств объекта через рефлексию
        """
        cls = source if isinstance(source, type) else type(source)
        fields: dict[str, None] = {}
        for klass in reversed(cls.__mro__):
            for name, member in vars(klass).items():
                if not name.startswith("_") and name not in exclude and isinstance(member, property):
                    fields[name] = None
        return list(fields)