from src.dtos.report_type_enum import report_type_enum


class report_format_service:
    """
    Сервис получения доступных форматов отчётов.
    """

    """
    Получить список названий поддерживаемых форматов
    """
    def get_formats(self) -> list[str]:
        return [
            report_format.name
            for report_format in report_type_enum
        ]