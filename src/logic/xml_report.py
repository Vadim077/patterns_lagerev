import xml.etree.ElementTree as ET
from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator
from src.dtos.report_result_dto import report_result_dto


class xml_report(abstract_report):
    """Формирование XML-отчета с использованием рефлексии."""

    @property
    def mimetype(self) -> str:
        return "application/xml; charset=utf-8"

    @property
    def is_binary(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "xml"

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)

        root = ET.Element(type(source).__name__)
        self._fill_object(root, source)
        ET.indent(root, space="  ")
        content = f'<?xml version="1.0" encoding="utf-8"?>\n{ET.tostring(root, encoding="unicode")}\n'

        result = report_result_dto()
        result.text = content
        return result

    def _fill_object(self, element: ET.Element, source: object) -> None:
        for field, value in self._fields(source):
            sub = ET.SubElement(element, field)
            self._fill_value(sub, value)

    def _fill_value(self, element: ET.Element, value: object) -> None:
        if self._is_reference(value):
            element.set("id", str(value.id))
            element.text = value.name
        elif self._is_scalar(value):
            element.text = self._format_scalar(value)
        elif self._is_collection(value):
            for item in value:
                item_elem = ET.SubElement(element, "item")
                self._fill_value(item_elem, item)
        else:
            self._fill_object(element, value)