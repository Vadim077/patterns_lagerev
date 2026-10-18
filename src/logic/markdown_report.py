from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto


class markdown_report(abstract_report):
    """Формирование отчета в формате Markdown с использованием рефлексии."""

    @property
    def mimetype(self) -> str:
        return "text/markdown; charset=utf-8"

    @property
    def is_binary(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "md"

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)

        lines = [f"# {source.name}", ""]
        lines.extend(self._object_lines(source, level=0))
        content = "\n".join(lines) + "\n"

        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        return result

    def _object_lines(self, source: object, level: int) -> list[str]:
        indent = "  " * level
        lines = []
        for field, value in self._fields(source):
            if self._is_reference(value):
                lines.append(f"{indent}- **{field}**: {self._format_reference(value)}")
            elif self._is_scalar(value):
                lines.append(f"{indent}- **{field}**: {self._format_scalar(value)}")
            elif self._is_collection(value):
                lines.append(f"{indent}- **{field}**:")
                for idx, item in enumerate(value, start=1):
                    item_indent = "  " * (level + 1)
                    if self._is_reference(item):
                        lines.append(f"{item_indent}{idx}. {self._format_reference(item)}")
                    elif self._is_scalar(item):
                        lines.append(f"{item_indent}{idx}. {self._format_scalar(item)}")
                    else:
                        sub_lines = self._object_lines(item, level + 2)
                        lines.append(f"{item_indent}{idx}.")
                        lines.extend(sub_lines)
            else:
                lines.append(f"{indent}- **{field}**:")
                lines.extend(self._object_lines(value, level + 1))
        return lines