from src.core.abstract_manager import abstract_manager
from src.models import (
    settings_model,
    range_model,
    nomenclature_group_model,
    storage_model,
    nomenclature_model,
    recipe_model,
)
import json
from src.logic.convert_factory import convert_factory
from src.logic.deserializer import deserializer

"""
Центральное хранилище данных приложения (Singleton)
Хранит коллекции: складов, единиц измерения, групп номенклатуры, номенклатуры, рецептов
Каждый объект в коллекциях гарантированно уникален
"""
class storage_manager(abstract_manager):

    __settings: settings_model = None
    __ranges: list = []
    __groups: list = []
    __storages: list = []
    __nomenclatures: list = []
    __recipes: list = []
    __collections_map: dict = None

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
    Ключи коллекций хранилища для сериализации и десериализации
    """
    @staticmethod
    def range_key() -> str:
        return range_model.__name__

    @staticmethod
    def group_key() -> str:
        return nomenclature_group_model.__name__

    @staticmethod
    def storage_key() -> str:
        return storage_model.__name__

    @staticmethod
    def nomenclature_key() -> str:
        return nomenclature_model.__name__

    @staticmethod
    def recipe_key() -> str:
        return recipe_model.__name__

    """
    Словарь всех коллекций данных хранилища по ключам моделей
    """
    @property
    def data(self) -> dict[str, list]:
        return {
            self.range_key(): self.__ranges,
            self.group_key(): self.__groups,
            self.storage_key(): self.__storages,
            self.nomenclature_key(): self.__nomenclatures,
            self.recipe_key(): self.__recipes,
        }

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
    Список рецептов (технологических карт)
    """
    @property
    def recipes(self) -> list[recipe_model]:
        return self.__recipes

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
    Добавить рецепт (с гарантией уникальности)
    """
    def add_recipe(self, item: recipe_model) -> bool:
        return self.__append_unique(self.__recipes, item)

    """
    Инициализация маппинга коллекций для поиска
    """
    def __init_collections_map(self) -> None:
        self.__collections_map = {
            "recipe": self.__recipes,
            "recipes": self.__recipes,
            "рецепт": self.__recipes,
            "рецепты": self.__recipes,
            "nomenclature": self.__nomenclatures,
            "nomenclatures": self.__nomenclatures,
            "номенклатура": self.__nomenclatures,
            "range": self.__ranges,
            "ranges": self.__ranges,
            "единица": self.__ranges,
            "единицы": self.__ranges,
            "единица_измерения": self.__ranges,
            "storage": self.__storages,
            "storages": self.__storages,
            "склад": self.__storages,
            "склады": self.__storages,
            "group": self.__groups,
            "groups": self.__groups,
            "группа": self.__groups,
            "группы": self.__groups,
        }

    """
    Поиск сущности в хранилище по её типу и уникальному коду (ID)
    Инкапсулирует логику доступа к коллекциям
    """
    def find_by_id(self, entity_type: str, entity_id: str) -> object:
        if not entity_type or not entity_id:
            return None

        t = str(entity_type).strip().lower()
        eid = str(entity_id).strip()

        if self.__collections_map is None:
            self.__init_collections_map()

        target_collection = self.__collections_map.get(t)
        if not target_collection:
            return None

        for item in target_collection:
            if getattr(item, "id", None) == eid or getattr(item, "unique_code", None) == eid:
                return item

        return None

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
        self.__init_recipes()
        return True

    """
    Очистить все коллекции (для изолированных тестов)
    """
    def clear(self) -> None:
        self.__ranges.clear()
        self.__groups.clear()
        self.__storages.clear()
        self.__nomenclatures.clear()
        self.__recipes.clear()
        self.__collections_map = None
        self.__settings = None

    """
    Генерация базовых и производных единиц измерения через фабричные методы
    """
    def __init_ranges(self) -> None:
        kg = range_model.create_kilogramm()
        gram = kg.base_range
        piece = range_model.create_piece()
        ml = range_model("миллилитр", 1)
        liter = range_model("литр", 1000, ml)

        for unit in [gram, kg, ml, liter, piece]:
            self.add_range(unit)

    """
    Генерация групп номенклатуры через фабричные методы
    """
    def __init_groups(self) -> None:
        group_raw = nomenclature_group_model.create_raw()
        group_ingredients = nomenclature_group_model.create_ingredients()
        group_semi = nomenclature_group_model.create_semi_finished()
        group_products = nomenclature_group_model.create_products()
        group_packaging = nomenclature_group_model.create_packaging()

        for group in [group_raw, group_ingredients, group_semi, group_products, group_packaging]:
            self.add_group(group)

    """
    Генерация складов через фабричные методы
    """
    def __init_storages(self) -> None:
        storage_main = storage_model.create_main()
        storage_cold = storage_model.create_cold()

        for storage in [storage_main, storage_cold]:
            self.add_storage(storage)

    """
    Генерация номенклатуры через фабричные методы
    """
    def __init_nomenclatures(self) -> None:
        group_raw = next((g for g in self.__groups if g.name == "Сырье"), self.__groups[0])
        group_ing = next((g for g in self.__groups if g.name == "Ингредиенты"), self.__groups[1])
        group_semi = next((g for g in self.__groups if g.name == "Полуфабрикаты"), None)
        group_prod = next((g for g in self.__groups if g.name == "Готовая продукция"), None)
        group_pkg = next((g for g in self.__groups if g.name == "Упаковка"), None)

        kg = next((u for u in self.__ranges if u.name == "кг"), self.__ranges[1])
        piece = next((u for u in self.__ranges if u.name == "штука"), self.__ranges[4])

        flour = nomenclature_model.create_flour(group_raw, kg)
        sugar = nomenclature_model.create_sugar(group_raw, kg)
        butter = nomenclature_model.create_butter(group_ing, kg)
        egg = nomenclature_model.create_egg(group_ing, piece)

        items = [flour, sugar, butter, egg]

        if group_semi:
            items.append(nomenclature_model.create_dough(group_semi, kg))
        if group_prod:
            items.append(nomenclature_model.create_cookie(group_prod, piece))
        if group_pkg:
            items.append(nomenclature_model.create_packaging_box(group_pkg, piece))

        for item in items:
            self.add_nomenclature(item)

    """
    Генерация рецептов (технологических карт) согласно docs/recipe.md
    """
    def __init_recipes(self) -> None:
        flour = next((n for n in self.__nomenclatures if n.name == "Мука"), None)
        sugar = next((n for n in self.__nomenclatures if n.name == "Сахар"), None)
        butter = next((n for n in self.__nomenclatures if n.name == "Масло"), None)
        egg = next((n for n in self.__nomenclatures if n.name == "Яйцо"), None)
        dough_nom = next((n for n in self.__nomenclatures if n.name == "Песочное тесто"), None)
        cookie_nom = next((n for n in self.__nomenclatures if n.name == "Печенье Ромашка"), None)
        box_nom = next((n for n in self.__nomenclatures if n.name == "Коробка"), None)

        if not all([flour, sugar, butter, egg, dough_nom, cookie_nom, box_nom]):
            return

        # 1. Рецепт полуфабриката "Песочное тесто"
        dough_recipe = recipe_model.create_dough_recipe(dough_nom, flour, butter, sugar, egg)
        self.add_recipe(dough_recipe)

        # 2. Рецепт готового блюда с полуфабрикатом и упаковкой
        cookie_recipe = recipe_model.create_cookie_recipe(cookie_nom, dough_nom, dough_recipe, box_nom)
        self.add_recipe(cookie_recipe)

    """
    Экспорт всех данных хранилища в JSON с использованием convert_factory
    """
    def save_json(self, file_path: str = "storage_dump.json") -> str:
        factory = convert_factory()
        data = {key: factory.convert(items) for key, items in self.data.items()}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    """
    Загрузка и восстановление всех данных хранилища из JSON с использованием deserializer
    """
    def load_json(self, file_path: str = "storage_dump.json", replace: bool = True) -> bool:
        if replace:
            self.clear()

        service = deserializer()
        raw_data = service.open(file_path)

        if not isinstance(raw_data, dict):
            return False

        for key, target_collection in self.data.items():
            items_data = raw_data.get(key, [])
            restored = service.deserialize(items_data)
            if not isinstance(restored, list):
                raise arguments_exception(field=key, message="Коллекция в JSON должна быть списком")
            target_collection.extend(restored)

        return True
