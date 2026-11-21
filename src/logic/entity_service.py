from typing import Any

from src.logic.convert_factory import convert_factory
from src.logic.deserializer import deserializer
from src.logic.entity_dependency_checker import entity_dependency_checker
from src.logic.entity_factory import entity_factory
from src.logic.entity_repository import entity_repository
from src.logic.storage_manager import storage_manager
from src.logic.storage_reposity import storage_repository


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
        repository: entity_repository = None,
        dependency_repository: storage_repository = None,
    ) -> None:
        self.__storage = storage
        self.__factory = factory or entity_factory()
        self.__converter = converter or convert_factory()
        self.__checker = checker or entity_dependency_checker(storage)
        self.__repository = repository or entity_repository(storage)
        self.__dependency_repository = dependency_repository or storage.repository
        self.__dependency_repository.rebuild(storage)

    """
    Создать контекст десериализации с объектами из хранилища
    """
    def __create_deserialization_context(
        self,
        excluded: tuple[tuple[type, str], ...] = (),
    ) -> deserializer:
        context = deserializer()

        for entity_type, collection in self.__storage.data.items():
            model_class = self.__factory.get_model_class(entity_type)

            for entity in collection:
                if (model_class, entity.id) in excluded:
                    continue
                context.set_cache(model_class, entity.id, entity)

        return context

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

        if not self.__repository.add(entity_type, entity):
            raise ValueError("Сущность не была добавлена в хранилище")

        self.__dependency_repository.rebuild(self.__storage)

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

        model_class = self.__factory.get_model_class(entity_type)
        current_data = self.__converter.convert(entity)
        patch_data = self.__normalize_patch_references(entity, data)
        merged_data = {**current_data, **patch_data}

        context = self.__create_deserialization_context(
            excluded=((model_class, entity.id),),
        )
        candidate = context.deserialize(merged_data, model_class)

        if candidate is None or not isinstance(candidate, model_class):
            raise ValueError("Не удалось обновить доменную сущность")

        self.__checker.validate_new_entity(entity_type, candidate)

        if not self.__repository.replace(entity_type, entity_id, candidate):
            raise ValueError("Сущность не была обновлена")

        self.__dependency_repository.rebuild(self.__storage)

        return self.__converter.convert(candidate)

    """
    Удалить сущность после проверки зависимостей
    """
    def delete(self, entity_type: str, entity_id: str) -> dict:
        entity = self.__storage.find_by_id(entity_type, entity_id)

        if entity is None:
            raise LookupError(
                f"Сущность '{entity_type}' с ID '{entity_id}' не найдена"
            )

        if not self.__dependency_repository.can_delete(entity):
            raise PermissionError(
                f"Нельзя удалить сущность '{entity_type}' "
                f"с ID '{entity_id}', потому что она используется"
            )

        if not self.__repository.remove(entity_type, entity_id):
            raise ValueError("Сущность не была удалена")

        self.__dependency_repository.rebuild(self.__storage)

        return {
            "deleted": True,
            "entity_type": entity_type,
            "id": entity_id,
        }

    def __normalize_patch_references(
        self,
        entity: object,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Преобразует идентификаторы ссылок в данные доменных моделей."""
        normalized = dict(data)

        for field_name, value in tuple(data.items()):
            if not field_name.endswith("_id"):
                continue

            property_name = field_name[:-3]
            if not hasattr(entity, property_name):
                raise ValueError(
                    f"Поле '{field_name}' не поддерживается для PATCH"
                )

            reference = self.__find_reference(entity, property_name, value)
            if reference is None:
                raise LookupError(
                    f"Связанная сущность с ID '{value}' не найдена"
                )

            normalized[property_name] = self.__converter.convert(reference)
            normalized.pop(field_name)

        return normalized

    def __find_reference(
        self,
        entity: object,
        property_name: str,
        entity_id: Any,
    ) -> object:
        """Ищет связанную сущность по идентификатору во всех коллекциях."""
        current_reference = getattr(entity, property_name, None)

        if current_reference is not None:
            reference_type = type(current_reference).__name__
            return self.__storage.find_by_id(reference_type, str(entity_id))

        for entity_type in self.__storage.data:
            reference = self.__storage.find_by_id(entity_type, str(entity_id))
            if reference is not None:
                return reference

        return None
