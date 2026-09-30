import pytest
from src.core.exception import arguments_exception
from src.models import storage_model


def test_storage_model_create_success():
    """Сценарий: Успешное создание склада с валидным именем."""
    # Подготовка
    storage_name = "Основной склад"

    # Действие
    storage = storage_model(name=storage_name)

    # Проверка
    assert storage.name == storage_name
    assert storage.id is not None
    assert len(storage.id) > 0


def test_storage_model_empty_name_raises_error():
    """Сценарий: Попытка создания склада с пустым наименованием."""
    # Подготовка
    empty_name = ""
    whitespace_name = "   "

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        storage_model(name=empty_name)

    with pytest.raises(arguments_exception):
        storage_model(name=whitespace_name)


def test_storage_model_name_too_long_raises_error():
    """Сценарий: Попытка создания склада с именем > 50 символов"""
    # Подготовка
    too_long_name = "С" * 51

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        storage_model(name=too_long_name)