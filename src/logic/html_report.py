from src.core.abstract_report import abstract_report
from src.core.abstract_model import abstract_model
from src.core.validator import validator, arguments_exception
from src.dtos.report_result_dto import report_result_dto
from src.models.recipe_model import recipe_model
from src.models.nomenclature_model import nomenclature_model
from src.models.range_model import range_model

"""
Формирование отчета в формате HTML (структурированный текст)
"""
class html_report(abstract_report):

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source)

        if isinstance(source, recipe_model):
            rows_html = ""
            for item in source.items:
                rows_html += f"      <tr><td>{item.unique_code}</td><td>{item.name}</td><td>{item.brutto}</td><td>{item.netto}</td></tr>\n"
            title = source.name if "Рецепт" in source.name else f"Рецепт: {source.name}"
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{source.name}</title></head>\n<body>\n"
                f"  <h2>{title}</h2>\n"
                f"  <p>Брутто: {source.brutto}, Нетто: {source.netto}</p>\n"
                f"  <table border='1'>\n"
                f"    <thead><tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr></thead>\n"
                f"    <tbody>\n{rows_html}    </tbody>\n"
                f"  </table>\n</body>\n</html>"
            )
        elif isinstance(source, nomenclature_model):
            group_name = source.group.name if getattr(source, "group", None) else ""
            range_name = source.range.name if getattr(source, "range", None) else ""
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{source.name}</title></head>\n<body>\n"
                f"  <h2>Номенклатура: {source.name}</h2>\n"
                f"  <table border='1'>\n"
                f"    <tr><th>Код</th><td>{source.unique_code}</td></tr>\n"
                f"    <tr><th>Наименование</th><td>{source.name}</td></tr>\n"
                f"    <tr><th>Полное наименование</th><td>{source.full_name}</td></tr>\n"
                f"    <tr><th>Группа</th><td>{group_name}</td></tr>\n"
                f"    <tr><th>Единица измерения</th><td>{range_name}</td></tr>\n"
                f"  </table>\n</body>\n</html>"
            )
        elif isinstance(source, range_model):
            base_name = source.base_range.name if getattr(source, "base_range", None) else ""
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{source.name}</title></head>\n<body>\n"
                f"  <h2>Единица измерения: {source.name}</h2>\n"
                f"  <table border='1'>\n"
                f"    <tr><th>Код</th><td>{source.unique_code}</td></tr>\n"
                f"    <tr><th>Наименование</th><td>{source.name}</td></tr>\n"
                f"    <tr><th>Коэффициент</th><td>{source.conversion_factor}</td></tr>\n"
                f"    <tr><th>Базовая единица</th><td>{base_name}</td></tr>\n"
                f"  </table>\n</body>\n</html>"
            )
        else:
            raise arguments_exception(field="source", message="Неподдерживаемый тип модели для формирования отчета")

        result = report_result_dto()
        result.text = content
        return result
