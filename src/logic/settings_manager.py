import json
from src.core.abstract_manager import abstract_manager
from src.core.validator import validator, operation_exception
from src.models.settings_model import settings_model
from src.models.organization_model import organization_model


"""
Менеджер настроек (Singleton)
"""
class settings_manager(abstract_manager):

    __default_file_name: str = "settings.json"
    __settings: settings_model = None
    __data: dict = {}
    __is_loaded: bool = False

    """
    Singleton паттерн
    """
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    """
    Загрузка данных из JSON файла
    """
    def load(self, file_name: str = ""):
        inner_file_name = file_name.strip() if file_name and file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name)

        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)
                self.__is_loaded = self.convert()
        except Exception as ex:
            raise operation_exception(f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}")

    """
    Обработка загруженных данных в модель settings_model
    """
    def convert(self) -> bool:
        if not self.__data or not isinstance(self.__data, dict):
            return False

        self.__settings = settings_model()

        if "boss_name" in self.__data:
            self.__settings.boss_name = self.__data["boss_name"]

        if "account_name" in self.__data:
            self.__settings.account_name = self.__data["account_name"]

        if "is_first_start" in self.__data:
            self.__settings.is_first_start = bool(self.__data["is_first_start"])

        if "company" in self.__data and isinstance(self.__data["company"], dict):
            comp = self.__data["company"]
            self.__settings.company = organization_model(
                name=comp.get("name"),
                inn=comp.get("inn"),
                bik=comp.get("bik"),
                account=comp.get("account"),
                ownership_type=comp.get("ownership_type"),
            )

        return True

    """
    Получить модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Флаг успешности загрузки
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded