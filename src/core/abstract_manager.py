from abc import ABC
"""
Абстрактный класс для реализации загрузки обработки данных
"""

class abstract_manager(ABC):
    # Полный путь к файлу
    __file_name: str = ""
    # Флаг. Загрузка и обработка данных
    __is_loaded: bool = False
    #
    __data:list = []

    """
    Загрузить данные
    """

    def load(self, file_name:str = "") -> None:
        pass

    """
    Обработать загруженные данные
    """
    
    def convert(self) -> bool:
        return False

    """
    Флаг. Данные обработаны
    """

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded