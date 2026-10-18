import csv
import io
from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto


class csv_report(abstract_report):
    """Формирование отчета в формате CSV с использованием рефлексии."""

    @property
    def mimetype(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def is_binary(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "csv"

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["field", "value"])

        for row in self._object_rows(source, ""):
            writer.writerow(row)

        content = buffer.getvalue()
        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        return result

    def _object_rows(self, source: object, path: str) -> list[tuple[str, str]]:
        rows = []
        for field, value in self._fields(source):
            current_path = f"{path}.{field}" if path else field
            if self._is_reference(value):
                rows.append((current_path, self._format_reference(value)))
            elif self._is_scalar(value):
                rows.append((current_path, self._format_scalar(value)))
            elif self._is_collection(value):
                for idx, item in enumerate(value, start=1):
                    item_path = f"{current_path}[{idx}]"
                    if self._is_reference(item) or self._is_scalar(item):
                        rows.append((item_path, self._format_reference(item) if self._is_reference(item) else self._format_scalar(item)))
                    else:
                        rows.extend(self._object_rows(item, item_path))
            else:
                rows.extend(self._object_rows(value, current_path))
        return rows