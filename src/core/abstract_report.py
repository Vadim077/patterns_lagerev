import io
import flask
from abc import ABC, abstractmethod
from typing import Sequence
from src.core.abstract_model import abstract_model
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """
    Абстрактный класс отчета
    """

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """MIME-тип формируемого отчета."""
        pass

    @property
    @abstractmethod
    def is_binary(self) -> bool:
        """Признак формирования бинарных данных для скачивания."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Расширение файла отчета."""
        pass

    @abstractmethod
    def build(self, source: abstract_model) -> report_result_dto:
        """Сформировать отчет по переданной модели."""
        pass

    def to_http_response(self, result: report_result_dto, filename: str = "report") -> flask.Response:
        """
        Полиморфное формирование HTTP-ответа
        """
        if self.is_binary:
            raw_bytes = bytes(result.binary) if result.binary else (result.text.encode("utf-8") if result.text else b"")
            return flask.send_file(
                io.BytesIO(raw_bytes),
                mimetype=self.mimetype,
                as_attachment=True,
                download_name=f"{filename}.{self.file_extension}",
            )
        return flask.Response(result.text, mimetype=self.mimetype)

    # --- Методы рефлексии---

    @staticmethod
    def get_fields(source: object, exclude: tuple = ()) -> list[str]:
        """
        Получение списка публичных полей (@property) объекта через рефлексию.
        Обходит MRO в обратном порядке для сохранения естественного порядка объявления.
        """
        cls = source if isinstance(source, type) else type(source)
        fields: dict[str, None] = {}
        for klass in reversed(cls.__mro__):
            for name, member in vars(klass).items():
                if not name.startswith("_") and name not in exclude and isinstance(member, property):
                    fields[name] = None
        return list(fields)

    def _fields(self, source: object) -> list[tuple[str, object]]:
        """Возвращает пары (имя_поля, значение) через рефлексию."""
        return [(field, getattr(source, field)) for field in self.get_fields(source)]

    @staticmethod
    def _is_scalar(value: object) -> bool:
        """Проверка, является ли значение простым скалярным типом."""
        return value is None or isinstance(value, (str, int, float, bool))

    @staticmethod
    def _is_reference(value: object) -> bool:
        """Проверка, является ли значение ссылкой на другую модель."""
        return isinstance(value, abstract_model)

    @staticmethod
    def _is_collection(value: object) -> bool:
        """Проверка, является ли значение коллекцией элементов."""
        return isinstance(value, (list, tuple))

    @staticmethod
    def _format_reference(entity: abstract_model) -> str:
        """Форматирование ссылочной сущности: Имя [id]."""
        return f"{entity.name} [{entity.id}]"

    @staticmethod
    def _format_scalar(value: object) -> str:
        """Форматирование скалярного значения."""
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:.3f}".rstrip("0").rstrip(".")
        return str(value)