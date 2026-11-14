from copy import copy
from typing import Any, Callable

from src.logic.convert_factory import convert_factory
from src.logic.deserializer import deserializer
from src.logic.entity_dependency_checker import entity_dependency_checker
from src.logic.entity_factory import entity_factory
from src.logic.storage_manager import storage_manager


class entity_service:
    """
    Сервис CRUD-операций над доменными сущностями.
    """

    def __init__(
        self,
        storage: storage_manager,
        factory: entity_factory = None,
        converter: convert_factory = None,
        checker: entity_dependency_checker = None,
    ) -> None:
        self.__storage = storage
        self.__factory = factory or entity_factory()
        self.__converter = converter or convert_factory()
        self.__checker = checker or entity_dependency_checker(storage)

        self.__patch_handlers: dict[
            str,
            dict[str, Callable[[object, Any], None]],
        ] = {
            "range_model": {
                "name": self.__set_name,
                "conversion_factor": self.__set_conversion_factor,
                "base_range_id": self.__set_base_range,
            },
            "nomenclature_group_model": {
                "name": self.__set_name,
            },
            "storage_model": {
                "name": self.__set_name,
            },
            "nomenclature_model": {
                "name": self.__set_name,
                "full_name": self.__set_full_name,
                "group_id": self.__set_group,
                "range_id": self.__set_range,
            },
            "recipe_model": {
                "name": self.__set_name,
                "cooking_time": self.__set_cooking_time,
                "instructions": self.__set_instructions,
                "portions": self.__set_portions,
                "dish_id": self.__set_dish,
            },
        }

    """
    Создать контекст десериализации с объектами из хранилища
    """
    def __create_deserialization_context(self) -> deserializer:
        context = deserializer()

        for entity_type, collection in self.__storage.data.items():
            model_class = self.__factory.get_model_class(entity_type)

            for entity in collection:
                context.set_cache(model_class, entity.id, entity)

        return context

    """
    Найти связанную сущность по типу и идентификатору
    """
    def __get_reference(self, entity_type: str, entity_id: str) -> object:
        self.__factory.get_model_class(entity_type)

        reference = self.__storage.find_by_id(entity_type, entity_id)

        if reference is None:
            raise LookupError(
                f"Связанная сущность '{entity_type}' "
                f"с ID '{entity_id}' не найдена"
            )

        return reference

    """
    Получить сущность по типу и идентификатору
    """
    def get(self, entity_type: str, entity_id: str) -> dict:
        self.__factory.get_model_class(entity_type)

        entity = self.__storage.find_by_id(entity_type, entity_id)

        if entity is None:
            raise LookupError(
                f"Сущность '{entity_type}' с ID '{entity_id}' не найдена"
            )

        return self.__converter.convert(entity)

    """
    Получить все сущности из хранилища
    """
    def list_all(self) -> dict[str, list]:
        result = {}

        for entity_type, collection in self.__storage.data.items():
            result[entity_type] = [
                self.__converter.convert(entity)
                for entity in collection
            ]

        return result

    """
    Создать новую сущность из JSON-данных
    """
    def create(
        self,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
    ) -> dict:
        model_class = self.__factory.get_model_class(entity_type)

        if not isinstance(data, dict):
            raise ValueError("Тело запроса должно быть JSON-объектом")

        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("Идентификатор сущности не может быть пустым")

        normalized_id = entity_id.strip()

        if self.__storage.find_by_id(entity_type, normalized_id) is not None:
            raise FileExistsError(
                f"Сущность '{entity_type}' "
                f"с ID '{normalized_id}' уже существует"
            )

        payload = dict(data)
        payload_id = payload.get("id")

        if payload_id is not None:
            if str(payload_id).strip() != normalized_id:
                raise ValueError(
                    "ID в URL и ID в JSON должны совпадать"
                )

        payload["id"] = normalized_id

        context = self.__create_deserialization_context()
        entity = context.deserialize(payload, model_class)

        if entity is None or not isinstance(entity, model_class):
            raise ValueError("Не удалось создать доменную сущность")

        self.__checker.validate_new_entity(entity_type, entity)

        if not self.__storage.add_entity(entity_type, entity):
            raise ValueError("Сущность не была добавлена в хранилище")

        return self.__converter.convert(entity)

    """
    Частично обновить существующую сущность
    """
    def update(
        self,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
    ) -> dict:
        if not isinstance(data, dict):
            raise ValueError("Тело запроса должно быть JSON-объектом")

        if "id" in data:
            raise ValueError("Изменение ID сущности запрещено")

        entity = self.__storage.find_by_id(entity_type, entity_id)

        if entity is None:
            raise LookupError(
                f"Сущность '{entity_type}' с ID '{entity_id}' не найдена"
            )

        handlers = self.__patch_handlers.get(entity_type)

        if handlers is None:
            self.__factory.get_model_class(entity_type)
            raise ValueError(
                f"Для типа '{entity_type}' не определены поля обновления"
            )

        unknown_fields = set(data) - set(handlers)

        if unknown_fields:
            raise ValueError(
                f"Запрещённые поля обновления: "
                f"{', '.join(sorted(unknown_fields))}"
            )

        candidate = copy(entity)

        for field_name, value in data.items():
            handlers[field_name](candidate, value)

        self.__checker.validate_new_entity(entity_type, candidate)

        for field_name, value in data.items():
            handlers[field_name](entity, value)

        return self.__converter.convert(entity)

    """
    Удалить сущность после проверки зависимостей
    """
    def delete(self, entity_type: str, entity_id: str) -> dict:
        entity = self.__storage.find_by_id(entity_type, entity_id)

        if entity is None:
            raise LookupError(
                f"Сущность '{entity_type}' с ID '{entity_id}' не найдена"
            )

        if self.__checker.is_used(entity_type, entity):
            raise PermissionError(
                f"Нельзя удалить сущность '{entity_type}' "
                f"с ID '{entity_id}', потому что она используется"
            )

        if not self.__storage.remove_entity(entity_type, entity_id):
            raise ValueError("Сущность не была удалена")

        return {
            "deleted": True,
            "entity_type": entity_type,
            "id": entity_id,
        }

    """
    Установить имя сущности
    """
    @staticmethod
    def __set_name(entity: object, value: Any) -> None:
        entity.name = value

    """
    Установить полное имя номенклатуры
    """
    @staticmethod
    def __set_full_name(entity: object, value: Any) -> None:
        entity.full_name = value

    """
    Установить коэффициент единицы измерения
    """
    @staticmethod
    def __set_conversion_factor(entity: object, value: Any) -> None:
        entity.conversion_factor = value

    """
    Установить базовую единицу измерения
    """
    def __set_base_range(self, entity: object, value: Any) -> None:
        entity.base_range = self.__get_reference(
            "range_model",
            value,
        )

    """
    Установить группу номенклатуры
    """
    def __set_group(self, entity: object, value: Any) -> None:
        entity.group = self.__get_reference(
            "nomenclature_group_model",
            value,
        )

    """
    Установить единицу измерения номенклатуры
    """
    def __set_range(self, entity: object, value: Any) -> None:
        entity.range = self.__get_reference(
            "range_model",
            value,
        )

    """
    Установить время приготовления
    """
    @staticmethod
    def __set_cooking_time(entity: object, value: Any) -> None:
        entity.cooking_time = value

    """
    Установить инструкции рецепта
    """
    @staticmethod
    def __set_instructions(entity: object, value: Any) -> None:
        entity.instructions = value

    """
    Установить количество порций
    """
    @staticmethod
    def __set_portions(entity: object, value: Any) -> None:
        entity.portions = value

    """
    Установить блюдо рецепта
    """
    def __set_dish(self, entity: object, value: Any) -> None:
        entity.dish = self.__get_reference(
            "nomenclature_model",
            value,
        )