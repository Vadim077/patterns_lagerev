from abc import ABC, abstractmethod


"""
Абстрактный класс прототипа для клонирования и фильтрации данных
"""
class abstract_prototype(ABC):

    @abstractmethod
    def clone(self, filter_instance = None) -> "abstract_prototype":
        """Создает новый экземпляр прототипа с отфильтрованными данными"""
        pass
