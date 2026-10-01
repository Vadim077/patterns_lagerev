from src.core.abstract_model import abstract_model
from src.models.organization_model import organization_model


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