from enum import Enum

"""
Типы отчетов
"""
class report_type_enum(Enum):
    TXT = 1
    CSV = 2
    MARKDOWN = 3
    XML = 4
    HTML = 5

    @staticmethod
    def from_string(value: str) -> "report_type_enum":
        """
        Преобразование строкового представления в перечисление
        """
        if not value or not isinstance(value, str):
            return report_type_enum.TXT

        clean = value.strip().upper()
        mapping = {
            "TXT": report_type_enum.TXT,
            "CSV": report_type_enum.CSV,
            "MARKDOWN": report_type_enum.MARKDOWN,
            "MD": report_type_enum.MARKDOWN,
            "XML": report_type_enum.XML,
            "HTML": report_type_enum.HTML,
        }
        return mapping.get(clean, report_type_enum.TXT)