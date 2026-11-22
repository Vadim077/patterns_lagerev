from src.core.common import common
from src.logic.storage_manager import storage_manager


class entity_dependency_checker:
    """
    Проверяет зависимости между доменными сущностями через рефлексию
    """

    """
    Конструктор проверяющего зависимостей
    """
    def __init__(self, storage: storage_manager) -> None:
        self.__storage = storage

    """
    Проверить наличие всех связанных сущностей в хранилище через рефлексию
    """
    def validate_new_entity(self, entity_type: str, entity: object) -> None:
        for reference in common.get_references(entity):
            reference_id = getattr(reference, "unique_code", None) or getattr(reference, "id", None)
            if not reference_id:
                continue

            reference_type = type(reference).__name__
            stored = self.__storage.find_by_id(reference_type, reference_id)
            if stored is None:
                stored = self.__storage.find_in_all_collections(reference_id)

            if stored is None:
                raise LookupError(
                    f"Связанная сущность '{reference_type}' "
                    f"с ID '{reference_id}' отсутствует в хранилище"
                )

    """
    Проверить, используется ли сущность другими объектами
    """
    def is_used(self, entity_type: str, entity: object) -> bool:
        return not self.__storage.repository.can_delete(entity)
