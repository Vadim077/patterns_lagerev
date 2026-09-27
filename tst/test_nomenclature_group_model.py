import pytest
from src.core.exception import arguments_exception
from src.models import nomenclature_group_model


def test_nomenclature_group_model_create_success():
    """Сценарий: Успешное создание группы номенклатуры."""
    # Подготовка
    group_name = "Ингредиенты"

    # Действие
    group = nomenclature_group_model(name=group_name)

    # Проверка
    assert group.name == group_name
    assert group.id is not None


def test_nomenclature_group_model_empty_name_raises_error():
    """Сценарий: Создание группы номенклатуры с пустым именем."""
    # Подготовка
    empty_name = ""

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        nomenclature_group_model(name=empty_name)


def test_nomenclature_group_model_name_too_long_raises_error():
    """Сценарий: Создание группы с наименованием > 50 символов."""
    # Подготовка
    too_long_name = "Г" * 51

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        nomenclature_group_model(name=too_long_name)