from src.core.abstract_factory import abstract_factory
from src.core.abstract_report import abstract_report
from src.dtos.report_type_enum import report_type_enum
from src.logic.text_report import text_report
from src.logic.csv_report import csv_report
from src.logic.markdown_report import markdown_report
from src.logic.xml_report import xml_report
from src.logic.html_report import html_report
from src.core.exception import arguments_exception
from src.models.settings_model import settings_model
from src.logic.settings_manager import settings_manager

"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_factory):
    __mapping: dict = {}
    __settings: settings_model = None

    # Маппинг тип отчета и его реализация
    def __init__(self, settings: settings_model = None):
        self.__mapping = {}
        self.__mapping[report_type_enum.TXT] = text_report
        self.__mapping[report_type_enum.CSV] = csv_report
        self.__mapping[report_type_enum.MARKDOWN] = markdown_report
        self.__mapping[report_type_enum.XML] = xml_report
        self.__mapping[report_type_enum.HTML] = html_report

        if settings is not None:
            self.__settings = settings
        else:
            manager = settings_manager()
            if not manager.is_loaded:
                try:
                    manager.load()
                except Exception:
                    pass
            self.__settings = manager.settings

    @property
    def settings(self) -> settings_model:
        """
        Инкапсулированные настройки
        """
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        self.__settings = value

    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Создать отчет указанного типа
        """
        if report_type not in self.__mapping:
            raise arguments_exception(field="report_type", message=f"Указанный тип отчета {report_type} не реализован")

        report_class = self.__mapping[report_type]
        return report_class()

    def create_default(self) -> abstract_report:
        """
        Создать отчет по умолчанию из настроек
        """
        if self.__settings is None or self.__settings.response_format is None:
            return self.create(report_type_enum.TXT)
        return self.create(self.__settings.response_format)