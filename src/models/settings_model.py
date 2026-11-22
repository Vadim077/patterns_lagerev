from src.core.abstract_model import abstract_model
from src.models.organization_model import organization_model
from src.dtos.report_type_enum import report_type_enum
from typing import Optional

from src.core.abstract_deserialization_context import (
    abstract_deserialization_context,
)
from src.core.exception import arguments_exception

"""
Модель настроек приложения
"""
class settings_model(abstract_model):

    def __init__(self) -> None:
        super().__init__()
        self.__company: organization_model = None
        self.__boss_name: str = ""
        self.__account_name: str = ""
        self.__is_first_start: bool = True
        self.__response_format: report_type_enum = report_type_enum.TXT

    """
    Флаг первого старта приложения
    """
    @property
    def is_first_start(self) -> bool:
        return self.__is_first_start

    """
    Установить флаг первого старта
    """
    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        self.__is_first_start = bool(value)

    """
    Карточка организации
    """
    @property
    def company(self) -> organization_model:
        return self.__company

    """
    Установить карточку организации
    """
    @company.setter
    def company(self, value: organization_model) -> None:
        self.__company = value

    """
    Наименование руководителя
    """
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    """
    Установить наименование руководителя
    """
    @boss_name.setter
    def boss_name(self, value: str) -> None:
        self.__boss_name = value.strip() if value else ""

    """
    Наименование главного бухгалтера
    """
    @property
    def account_name(self) -> str:
        return self.__account_name

    """
    Установить наименование главного бухгалтера
    """
    @account_name.setter
    def account_name(self, value: str) -> None:
        self.__account_name = value.strip() if value else ""

    """
    Формат ответа по умолчанию
    """
    @property
    def response_format(self) -> report_type_enum:
        return self.__response_format

    @response_format.setter
    def response_format(self, value) -> None:
        if isinstance(value, report_type_enum):
            self.__response_format = value
        elif isinstance(value, str):
            self.__response_format = report_type_enum.from_string(value)
        else:
            self.__response_format = report_type_enum.TXT

    """
    Фабричный метод создания настроек из словаря
    """
    @classmethod
    def create(
        cls,
        data: dict,
        service: Optional[abstract_deserialization_context] = None,
    ) -> "settings_model":
        if data is None or not isinstance(data, dict):
            raise arguments_exception(
                field="data",
                message="Данные должны быть словарём",
            )

        instance = cls()

        if "boss_name" in data:
            instance.boss_name = data["boss_name"]

        if "account_name" in data:
            instance.account_name = data["account_name"]

        if "is_first_start" in data:
            instance.is_first_start = data["is_first_start"]

        if "response_format" in data:
            instance.response_format = data["response_format"]

        company_data = data.get("company")

        if isinstance(company_data, dict):
            if service is not None:
                instance.company = service.deserialize(
                    company_data,
                    organization_model,
                )
            else:
                instance.company = organization_model.create(company_data)

        return instance