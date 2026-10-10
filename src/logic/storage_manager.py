from src.core.abstract_manager import abstract_manager
from src.models import (
    settings_model,
    range_model,
    nomenclature_group_model,
    storage_model,
    nomenclature_model,
)


"""
Центральное хранилище данных приложения (Singleton)
Хранит коллекции: складов, единиц измерения, групп номенклатуры, номенклатуры
Каждый объект в коллекциях гарантированно уникален
"""
class storage_manager(abstract_manager):

    __settings: settings_model = None
    __ranges: list = []
    __groups: list = []
    __storages: list = []
    __nomenclatures: list = []

    """
    Паттерн Singleton
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    """
    Конструктор хранилища
    """
    def __init__(self, settings: settings_model = None) -> None:
        if settings is not None:
            self.__settings = settings
            self.convert()

    """
    Получить текущие настройки
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Установить настройки и запустить обработку
    """
    @settings.setter
    def settings(self, value: settings_model) -> None:
        self.__settings = value
        self.convert()

    """
    Список единиц измерения
    """
    @property
    def ranges(self) -> list[range_model]:
        return self.__ranges

    """
    Список групп номенклатуры
    """
    @property
    def groups(self) -> list[nomenclature_group_model]:
        return self.__groups

    """
    Список складов
    """
    @property
    def storages(self) -> list[storage_model]:
        return self.__storages

    """
    Список номенклатуры
    """
    @property
    def nomenclatures(self) -> list[nomenclature_model]:
        return self.__nomenclatures

    """
    Добавить элемент в список с проверкой уникальности
    """
    def __append_unique(self, target_list: list, item: object) -> bool:
        if item is not None and item not in target_list:
            target_list.append(item)
            return True
        return False

    """
    Добавить единицу измерения (с гарантией уникальности)
    """
    def add_range(self, item: range_model) -> bool:
        return self.__append_unique(self.__ranges, item)

    """
    Добавить группу номенклатуры (с гарантией уникальности)
    """
    def add_group(self, item: nomenclature_group_model) -> bool:
        return self.__append_unique(self.__groups, item)

    """
    Добавить склад (с гарантией уникальности)
    """
    def add_storage(self, item: storage_model) -> bool:
        return self.__append_unique(self.__storages, item)

    """
    Добавить номенклатуру (с гарантией уникальности)
    """
    def add_nomenclature(self, item: nomenclature_model) -> bool:
        return self.__append_unique(self.__nomenclatures, item)

    """
    Переопределенный метод обработки данных
    При первом старте (is_first_start == True) формирует первичные данные
    """
    def convert(self) -> bool:
        if self.__settings is None or not self.__settings.is_first_start:
            return False

        self.__init_ranges()
        self.__init_groups()
        self.__init_storages()
        self.__init_nomenclatures()
        return True

    """
    Очистить все коллекции (для изолированных тестов)
    """
    def clear(self) -> None:
        self.__ranges.clear()
        self.__groups.clear()
        self.__storages.clear()
        self.__nomenclatures.clear()

    """
    Генерация базовых и производных единиц измерения
    """
    def __init_ranges(self) -> None:
        gram = range_model("грамм", 1)
        kg = range_model("кг", 1000, gram)
        ml = range_model("миллилитр", 1)
        liter = range_model("литр", 1000, ml)
        piece = range_model("штука", 1)

        for unit in [gram, kg, ml, liter, piece]:
            self.add_range(unit)

    """
    Генерация групп номенклатуры
    """
    def __init_groups(self) -> None:
        group_raw = nomenclature_group_model("Сырье")
        group_ingredients = nomenclature_group_model("Ингредиенты")

        for group in [group_raw, group_ingredients]:
            self.add_group(group)

    """
    Генерация складов
    """
    def __init_storages(self) -> None:
        storage_main = storage_model("Основной склад")
        storage_cold = storage_model("Холодильник")

        for storage in [storage_main, storage_cold]:
            self.add_storage(storage)

    """
    Генерация номенклатуры с привязкой к созданным группам и единицам
    """
    def __init_nomenclatures(self) -> None:
        if not self.__groups or len(self.__ranges) < 5:
            return

        group_raw = self.__groups[0]          # Сырье
        group_ing = self.__groups[1]          # Ингредиенты

        kg = self.__ranges[1]                 # кг
        piece = self.__ranges[4]              # штука

        flour = nomenclature_model(
            name="Мука",
            full_name="Мука пшеничная высший сорт ГОСТ",
            group=group_raw,
            range_unit=kg,
        )

        sugar = nomenclature_model(
            name="Сахар",
            full_name="Сахар белый свекловичный ГОСТ",
            group=group_raw,
            range_unit=kg,
        )

        butter = nomenclature_model(
            name="Масло",
            full_name="Масло сливочное 82.5% ГОСТ",
            group=group_ing,
            range_unit=kg,
        )

        egg = nomenclature_model(
            name="Яйцо",
            full_name="Яйцо куриное столовое С0",
            group=group_ing,
            range_unit=piece,
        )

        for item in [flour, sugar, butter, egg]:
            self.add_nomenclature(item)