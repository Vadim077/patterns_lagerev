from src.core.abstract_model import abstract_model
from src.core.common import common
from src.core.validator import validator, operation_exception


class _counts_dict(dict):
    """Словарь счетчиков связей с поддержкой составных ключей."""

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            return super().get(item[1], 0)
        return super().__getitem__(item)

    def get(self, item, default=None):
        if isinstance(item, tuple) and len(item) == 2:
            return super().get(item[1], default)
        return super().get(item, default)

    def __contains__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            return super().__contains__(item[1])
        return super().__contains__(item)


"""
Репозиторий для хранения списка объектов и счетчика связей
"""
class storage_repository:
    # Исходный набор данных. Ключ - GUID, значение - abstract_model
    __data: dict = {}
    # Счетчик ссылок. Ключ - GUID, значение - число ссылок
    __counts: dict = {}

    def __init__(self) -> None:
        self.__data = {}
        self.__counts = _counts_dict()

    """
    Очистить индекс объектов и счетчиков
    """
    def clear(self) -> None:
        self.__data.clear()
        self.__counts.clear()

    """
    Перестроить индекс по текущему состоянию хранилища
    """
    def rebuild(self, storage) -> None:
        self.clear()

        # Первый проход: регистрация всех основных сущностей
        for collection in storage.data.values():
            for entity in collection:
                code = getattr(entity, "unique_code", None) or getattr(entity, "id", None)
                if code:
                    self.__data[code] = entity
                    self.__counts[code] = 0

        # Второй проход: подсчет входящих ссылок через рефлексию
        for collection in storage.data.values():
            for entity in collection:
                for ref in common.get_references(entity):
                    ref_code = getattr(ref, "unique_code", None) or getattr(ref, "id", None)
                    if ref_code and ref_code in self.__counts:
                        self.__counts[ref_code] += 1

    """
    Зарегистрировать доменный объект
    """
    def registry(self, source: abstract_model):
        validator.validate(source, abstract_model)
        code = getattr(source, "unique_code", None) or getattr(source, "id", None)
        if not code:
            return

        self.__data[code] = source
        if code not in self.__counts:
            self.__counts[code] = 0

        # Регистрация вложений через рефлексию
        for ref in common.get_references(source):
            ref_code = getattr(ref, "unique_code", None) or getattr(ref, "id", None)
            if not ref_code:
                continue

            self.__data[ref_code] = ref
            if ref_code not in self.__counts:
                self.__counts[ref_code] = 0
            self.__counts[ref_code] += 1

    """
    Зарегистрировать сразу несколько объектов
    """
    def registry_range(self, items: list):
        validator.validate(items, list)
        for item in items:
            self.registry(item)

    """
    Получить объект по уникальному коду или модели
    """
    def get(self, source):
        code = (
            getattr(source, "unique_code", None)
            or getattr(source, "id", None)
            or (source if isinstance(source, str) else None)
        )

        if code and code in self.__data:
            return self.__data.get(code)
        raise ValueError(f"Не найдена доменная сущность по коду : {code}!")

    """
    Проверить возможность удаления
    """
    def can_delete(self, source) -> bool:
        code = (
            getattr(source, "unique_code", None)
            or getattr(source, "id", None)
            or (source if isinstance(source, str) else None)
        )

        if not code or code not in self.__data:
            return False

        return self.__counts.get(code, 0) == 0

    """
    Удалить сущность из счетчиков
    """
    def delete(self, source):
        if not self.can_delete(source):
            code = getattr(source, "unique_code", None) or getattr(source, "id", str(source))
            raise ValueError(f"Невозможно удалить запись {code}!")

        code = (
            getattr(source, "unique_code", None)
            or getattr(source, "id", None)
            or (source if isinstance(source, str) else None)
        )

        # Уменьшаем счетчики для связанных сущностей
        entity = self.__data.get(code)
        if entity:
            for ref in common.get_references(entity):
                ref_code = getattr(ref, "unique_code", None) or getattr(ref, "id", None)
                if ref_code and ref_code in self.__counts:
                    self.__counts[ref_code] = max(0, self.__counts[ref_code] - 1)

        self.__data.pop(code, None)
        self.__counts.pop(code, None)

    """
    Исходный набор данных
    """
    @property
    def data(self) -> dict:
        return self.__data

    """
    Исходный набор счетчиков
    """
    @property
    def counts(self) -> dict:
        return self.__counts
