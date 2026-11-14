from typing import Callable, Iterable

from src.logic.storage_manager import storage_manager


class entity_dependency_checker:
    """
    Проверяет зависимости между доменными сущностями
    """

    """
    Конструктор проверяющего зависимостей
    """
    def __init__(self, storage: storage_manager) -> None:
        self.__storage = storage

        self.__entity_references: dict[str, Callable[[object], Iterable[object]]] = {
            "range_model": self.__get_range_references,
            "nomenclature_model": self.__get_nomenclature_references,
            "recipe_model": self.__get_recipe_references,
        }

        self.__reverse_references: dict[str, tuple[tuple[str, Callable[[object], Iterable[object]]], ...]] = {
            "range_model": (
                ("range_model", self.__get_range_references),
                ("nomenclature_model", self.__get_nomenclature_references),
                ("recipe_model", self.__get_recipe_references),
            ),
            "nomenclature_group_model": (
                ("nomenclature_model", self.__get_nomenclature_references),
            ),
            "nomenclature_model": (
                ("recipe_model", self.__get_recipe_references),
            ),
            "recipe_model": (
                ("recipe_model", self.__get_recipe_references),
            ),
        }

    """
    Получить ссылки единицы измерения
    """
    @staticmethod
    def __get_range_references(entity: object) -> Iterable[object]:
        base_range = getattr(entity, "base_range", None)

        if base_range is None or base_range is entity:
            return ()

        return (base_range,)

    """
    Получить ссылки номенклатуры
    """
    @staticmethod
    def __get_nomenclature_references(entity: object) -> Iterable[object]:
        references = []

        group = getattr(entity, "group", None)
        range_unit = getattr(entity, "range", None)

        if group is not None:
            references.append(group)

        if range_unit is not None:
            references.append(range_unit)

        return tuple(references)

    """
    Получить ссылки рецепта
    """
    @staticmethod
    def __get_recipe_references(entity: object) -> Iterable[object]:
        references = []

        dish = getattr(entity, "dish", None)

        if dish is not None:
            references.append(dish)

        for row in getattr(entity, "rows", []):
            nomenclature = getattr(row, "nomenclature", None)
            range_unit = getattr(row, "range", None)
            sub_recipe = getattr(row, "sub_recipe", None)

            if nomenclature is not None:
                references.append(nomenclature)

            if range_unit is not None:
                references.append(range_unit)

            if sub_recipe is not None:
                references.append(sub_recipe)

        return tuple(references)

    """
    Проверить наличие всех связанных сущностей
    """
    def validate_new_entity(self, entity_type: str, entity: object) -> None:
        extractor = self.__entity_references.get(entity_type)

        if extractor is None:
            return

        for reference in extractor(entity):
            reference_type = type(reference).__name__
            stored_reference = self.__storage.find_by_id(
                reference_type,
                reference.id,
            )

            if stored_reference is None:
                raise LookupError(
                    f"Связанная сущность '{reference_type}' "
                    f"с ID '{reference.id}' отсутствует в хранилище"
                )

    """
    Проверить, используется ли сущность другими объектами
    """
    def is_used(self, entity_type: str, entity: object) -> bool:
        rules = self.__reverse_references.get(entity_type, ())

        for source_type, extractor in rules:
            for source_entity in self.__storage.get_collection(source_type):
                if source_entity is entity:
                    continue

                for reference in extractor(source_entity):
                    if self.__same_entity(reference, entity):
                        return True

        return False

    """
    Сравнить две доменные сущности по типу и ID
    """
    @staticmethod
    def __same_entity(first: object, second: object) -> bool:
        return (
            type(first) is type(second)
            and getattr(first, "id", None) == getattr(second, "id", None)
        )