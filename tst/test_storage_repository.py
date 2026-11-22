import pytest

from main import storage_mgr
from src.logic.storage_reposity import storage_repository


def test_repository_counts_incoming_references():
    """Репозиторий считает входящие ссылки на доменную сущность."""

    # Подготовка
    repository = storage_repository()
    repository.rebuild(storage_mgr)
    range_entity = storage_mgr.ranges[0]
    key = (type(range_entity).__name__, range_entity.id)

    # Действие
    reference_count = repository.counts[key]

    # Проверка
    assert reference_count > 0
    assert repository.can_delete(range_entity) is False


def test_repository_allows_unreferenced_entity_deletion():
    """Репозиторий разрешает удаление объекта без входящих ссылок."""

    # Подготовка
    repository = storage_repository()
    repository.rebuild(storage_mgr)
    storage_entity = storage_mgr.storages[0]

    # Действие
    can_delete = repository.can_delete(storage_entity)

    # Проверка
    assert can_delete is True


def test_repository_removes_deleted_entity_from_index():
    """После удаления объект исчезает из индекса репозитория."""

    # Подготовка
    repository = storage_repository()
    repository.rebuild(storage_mgr)
    storage_entity = storage_mgr.storages[0]

    # Действие
    repository.delete(storage_entity)

    # Проверка
    with pytest.raises(ValueError):
        repository.get(storage_entity)


def test_repository_cannot_delete_entity_with_references():
    """Попытка удаления сущности с ненулевым счетчиком вызывает исключение."""

    # Подготовка
    repository = storage_repository()
    repository.rebuild(storage_mgr)
    range_entity = storage_mgr.ranges[0]

    # Действие и проверка
    with pytest.raises(ValueError):
        repository.delete(range_entity)


def test_storage_manager_domains_reflection():
    """Проверка получения списка доменов через рефлексию domains()."""

    # Действие
    domains = storage_mgr.domains()

    # Проверка
    assert isinstance(domains, dict)
    assert len(domains) >= 5
    assert storage_mgr.range_key() in domains
    assert storage_mgr.nomenclature_key() in domains
    assert storage_mgr.storage_key() in domains
    assert storage_mgr.group_key() in domains
    assert storage_mgr.recipe_key() in domains
    assert all(isinstance(v, str) and len(v) > 0 for v in domains.values())


def test_repository_get_by_unique_code_string():
    """Получение сущности из репозитория по строковому коду."""

    # Подготовка
    repository = storage_repository()
    repository.rebuild(storage_mgr)
    storage_entity = storage_mgr.storages[0]

    # Действие
    found = repository.get(storage_entity.id)

    # Проверка
    assert found is not None
    assert found.id == storage_entity.id
