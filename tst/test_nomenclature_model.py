import pytest
from src.core.exception import arguments_exception
from src.models import (
    nomenclature_model,
    nomenclature_group_model,
    range_model,
)


def test_nomenclature_model_create_full_success():
    """Сценарий: Успешное создание номенклатуры со всеми связями."""
    # Подготовка
    group = nomenclature_group_model(name="Бакалея")
    unit = range_model(name="кг", conversion_factor=1)
    name = "Сахар"
    full_name = "Сахар белый свекловичный кристаллический ГОСТ 33222-2015"

    # Действие
    nom = nomenclature_model(
        name=name,
        full_name=full_name,
        group=group,
        range_unit=unit,
    )

    # Проверка
    assert nom.name == name
    assert nom.full_name == full_name
    assert nom.group == group
    assert nom.range == unit


def test_nomenclature_model_full_name_limit_success_and_error():
    """Сценарий: Полное наименование до 255 символов."""
    # Подготовка
    valid_255 = "Н" * 255
    invalid_256 = "Н" * 256

    # Действие
    nom = nomenclature_model(full_name=valid_255)

    # Проверка
    assert nom.full_name == valid_255

    with pytest.raises(arguments_exception):
        nomenclature_model(full_name=invalid_256)


def test_nomenclature_model_invalid_relations_raises_error():
    """Сценарий: Передача некорректных типов в поля group и range."""
    # Подготовка
    invalid_group = "не_группа_номенклатуры"
    invalid_range = "не_единица_измерения"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        nomenclature_model(group=invalid_group)

    with pytest.raises(arguments_exception):
        nomenclature_model(range_unit=invalid_range)


def test_nomenclature_model_short_name_limit_raises_error():
    """Сценарий: Обычное имя номенклатуры не может быть > 50 символов."""
    # Подготовка
    too_long_name = "Н" * 51

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        nomenclature_model(name=too_long_name)