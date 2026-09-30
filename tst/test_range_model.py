import pytest
from src.core.exception import arguments_exception
from src.models import range_model


def test_range_model_base_and_conversion_success():
    """
    Сценарий: Демонстрация работы с моделью единиц измерения.
    """
    # Подготовка
    base_name = "грамм"
    base_factor = 1
    derived_name = "кг"
    derived_factor = 1000

    # Действие
    base_range = range_model(base_name, base_factor)
    new_range = range_model(derived_name, derived_factor, base_range)

    # Проверка
    assert base_range.name == "грамм"
    assert base_range.conversion_factor == 1.0
    assert base_range.base_range == base_range

    assert new_range.name == "кг"
    assert new_range.conversion_factor == 1000.0
    assert new_range.base_range == base_range
    assert new_range.base_range.name == "грамм"


def test_range_model_invalid_conversion_factor_raises_error():
    """Сценарий: Задание недопустимого коэффициента пересчета."""
    # Подготовка
    zero_factor = 0
    negative_factor = -10
    str_factor = "1000"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        range_model("литр", conversion_factor=zero_factor)

    with pytest.raises(arguments_exception):
        range_model("литр", conversion_factor=negative_factor)

    with pytest.raises(arguments_exception):
        range_model("литр", conversion_factor=str_factor)


def test_range_model_invalid_base_range_raises_error():
    """Сценарий: Передача некорректного объекта в base_range."""
    # Подготовка
    invalid_base = "не_range_model"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        range_model("штука", 1, base_range=invalid_base)


def test_range_model_name_too_long_raises_error():
    """Сценарий: Попытка создания единицы измерения с именем > 50 символов."""
    # Подготовка
    too_long_name = "Е" * 51

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        range_model(name=too_long_name)