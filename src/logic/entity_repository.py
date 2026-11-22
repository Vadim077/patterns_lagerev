from src.logic.storage_manager import storage_manager


class entity_repository:
    """Репозиторий доступа к коллекциям доменных сущностей"""

    def __init__(self, storage: storage_manager) -> None:
        """Инициализирует репозиторий хранилищем данных"""
        self.__storage = storage

    def find(self, entity_type: str, entity_id: str) -> object:
        """Возвращает сущность по типу и идентификатору"""
        return self.__storage.find_by_id(entity_type, entity_id)

    def add(self, entity_type: str, entity: object) -> bool:
        """Добавляет проверенную сущность в коллекцию"""
        collection = self.__storage.get_collection(entity_type)

        if entity is None or entity in collection:
            return False

        collection.append(entity)
        return True

    def replace(self, entity_type: str, entity_id: str, entity: object) -> bool:
        """Заменяет сущность в коллекции по идентификатору"""
        collection = self.__storage.get_collection(entity_type)

        for current in collection:
            if getattr(current, "id", None) == entity_id:
                current.__dict__.clear()
                current.__dict__.update(entity.__dict__)
                return True

        return False

    def remove(self, entity_type: str, entity_id: str) -> bool:
        """Удаляет сущность из коллекции по идентификатору"""
        collection = self.__storage.get_collection(entity_type)

        for index, current in enumerate(collection):
            if getattr(current, "id", None) == entity_id:
                collection.pop(index)
                return True

        return False
