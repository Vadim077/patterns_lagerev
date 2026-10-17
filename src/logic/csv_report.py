from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator, arguments_exception
from src.dtos.report_result_dto import report_result_dto
from src.models.recipe_model import recipe_model
from src.models.nomenclature_model import nomenclature_model
from src.models.range_model import range_model

"""
Формирование отчета в формате CSV (бинарный вывод для скачивания)
"""
class csv_report(abstract_report):

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source)

        if isinstance(source, recipe_model):
            header = "Код;Наименование;Брутто;Нетто\n"
            rows = [f"{item.unique_code};{item.name};{item.brutto};{item.netto}" for item in source.items]
            content = header + "\n".join(rows)
        elif isinstance(source, nomenclature_model):
            header = "Код;Наименование;Полное наименование;Группа;Единица измерения\n"
            group_name = source.group.name if getattr(source, "group", None) else ""
            range_name = source.range.name if getattr(source, "range", None) else ""
            row = f"{source.unique_code};{source.name};{source.full_name};{group_name};{range_name}"
            content = header + row
        elif isinstance(source, range_model):
            header = "Код;Наименование;Коэффициент;Базовая единица\n"
            base_name = source.base_range.name if getattr(source, "base_range", None) else ""
            row = f"{source.unique_code};{source.name};{source.conversion_factor};{base_name}"
            content = header + row
        else:
            raise arguments_exception(field="source", message="Неподдерживаемый тип модели для формирования отчета")

        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        return result
