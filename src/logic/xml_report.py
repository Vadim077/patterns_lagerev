from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator, arguments_exception
from src.dtos.report_result_dto import report_result_dto
from src.models.recipe_model import recipe_model
from src.models.nomenclature_model import nomenclature_model
from src.models.range_model import range_model

"""
Формирование отчета в формате XML (структурированный текст)
"""
class xml_report(abstract_report):

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source)

        if isinstance(source, recipe_model):
            items_xml = ""
            for item in source.items:
                items_xml += f'    <item id="{item.unique_code}" name="{item.name}" brutto="{item.brutto}" netto="{item.netto}" />\n'
            content = (
                f'<?xml version="1.0" encoding="utf-8"?>\n'
                f'<recipe id="{source.unique_code}" name="{source.name}" brutto="{source.brutto}" netto="{source.netto}">\n'
                f'  <items>\n{items_xml}  </items>\n'
                f'</recipe>'
            )
        elif isinstance(source, nomenclature_model):
            group_name = source.group.name if getattr(source, "group", None) else ""
            range_name = source.range.name if getattr(source, "range", None) else ""
            content = (
                f'<?xml version="1.0" encoding="utf-8"?>\n'
                f'<nomenclature id="{source.unique_code}" name="{source.name}">\n'
                f'  <full_name>{source.full_name}</full_name>\n'
                f'  <group>{group_name}</group>\n'
                f'  <range>{range_name}</range>\n'
                f'</nomenclature>'
            )
        elif isinstance(source, range_model):
            base_name = source.base_range.name if getattr(source, "base_range", None) else ""
            content = (
                f'<?xml version="1.0" encoding="utf-8"?>\n'
                f'<range id="{source.unique_code}" name="{source.name}">\n'
                f'  <conversion_factor>{source.conversion_factor}</conversion_factor>\n'
                f'  <base_range>{base_name}</base_range>\n'
                f'</range>'
            )
        else:
            raise arguments_exception(field="source", message="Неподдерживаемый тип модели для формирования отчета")

        result = report_result_dto()
        result.text = content
        return result
