import xml.etree.ElementTree as ET
from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto


class html_report(abstract_report):
    """Формирование HTML-отчета с использованием рефлексии."""

    _STYLE = "table { border-collapse: collapse; font-family: sans-serif; } th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; } th { background: #f0f0f0; }"

    @property
    def mimetype(self) -> str:
        return "text/html; charset=utf-8"

    @property
    def is_binary(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "html"

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)

        page = ET.Element("html", lang="ru")
        head = ET.SubElement(page, "head")
        ET.SubElement(head, "meta", charset="utf-8")
        ET.SubElement(head, "title").text = source.name
        ET.SubElement(head, "style").text = self._STYLE

        body = ET.SubElement(page, "body")
        ET.SubElement(body, "h2").text = f"Отчет: {source.name}"
        body.append(self._table(source))

        ET.indent(page, space="  ")
        content = f"<!DOCTYPE html>\n{ET.tostring(page, encoding='unicode', method='html')}\n"

        result = report_result_dto()
        result.text = content
        return result

    def _table(self, source: object) -> ET.Element:
        table = ET.Element("table")
        for field, value in self._fields(source):
            row = ET.SubElement(table, "tr")
            ET.SubElement(row, "th").text = field
            td = ET.SubElement(row, "td")
            self._fill_value(td, value)
        return table

    def _fill_value(self, element: ET.Element, value: object) -> None:
        if self._is_reference(value):
            element.text = self._format_reference(value)
        elif self._is_scalar(value):
            element.text = self._format_scalar(value)
        elif self._is_collection(value):
            ol = ET.SubElement(element, "ol")
            for item in value:
                li = ET.SubElement(ol, "li")
                self._fill_value(li, item)
        else:
            element.append(self._table(value))