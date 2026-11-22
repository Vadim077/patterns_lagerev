from src.core.abstract_manager import abstract_manager
from src.core.validator import operation_exception, validator
from src.logic.deserializer import deserializer
from src.models.settings_model import settings_model


"""
Менеджер настроек Singleton
"""
class settings_manager(abstract_manager):

    __default_file_name: str = "settings.json"
    __settings: settings_model = None
    __is_loaded: bool = False

    """
    Singleton паттерн
    """
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)

        return cls.instance

    """
    Загрузка настроек через общий механизм десериализации
    """
    def load(self, file_name: str = "") -> None:
        inner_file_name = (
            file_name.strip()
            if file_name and file_name.strip()
            else self.__default_file_name
        )

        validator.validate(inner_file_name, str)

        try:
            service = deserializer()

            loaded_settings = service.deserialize_file(
                inner_file_name,
                settings_model,
            )

            if not isinstance(loaded_settings, settings_model):
                raise operation_exception(
                    "Десериализатор вернул некорректную модель настроек"
                )

            self.__settings = loaded_settings
            self.__is_loaded = True

        except Exception as exception:
            self.__is_loaded = False

            raise operation_exception(
                "Ошибка при загрузке и обработке файла "
                f"{inner_file_name}. Детали: {exception}"
            ) from exception

    """
    Обработка настроек
    """
    def convert(self) -> bool:
        return self.__is_loaded

    """
    Получить модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Получить статус загрузки настроек
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded