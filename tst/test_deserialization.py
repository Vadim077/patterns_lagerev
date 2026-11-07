import os
import pytest
from datetime import datetime
from src.core.exception import arguments_exception
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.model_deserializer import model_deserializer
from src.logic.deserialize_factory import deserialize_factory
from src.logic.storage_manager import storage_manager
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    settings_model,
    storage_model,
)


# 1. Тесты basic_deserializer

def test_basic_deserializer_primitives():
    """Тест 1 (basic_deserializer): Простые типы возвращаются корректно"""
    # Подготовка
    deserializer = basic_deserializer()

    # Действие и Проверка
    assert deserializer.deserialize(42) == 42
    assert deserializer.deserialize(3.14) == 3.14
    assert deserializer.deserialize("Текст") == "Текст"
    assert deserializer.deserialize(True) is True
    assert deserializer.deserialize(None) is None


def test_basic_deserializer_type_conversion():
    """Тест 2 (basic_deserializer): Преобразование типов по требованию"""
    # Подготовка
    deserializer = basic_deserializer()

    # Действие
    int_res = deserializer.deserialize("100", int)
    bool_res = deserializer.deserialize("True", bool)

    # Проверка
    assert int_res == 100
    assert bool_res is True


# 2. Тесты datetime_deserializer

def test_datetime_deserializer_iso_format():
    """Тест 3 (datetime_deserializer): Парсинг ISO 8601 строки в datetime"""
    # Подготовка
    deserializer = datetime_deserializer()
    iso_str = "2026-11-07T12:00:00"

    # Действие
    result = deserializer.deserialize(iso_str)

    # Проверка
    assert isinstance(result, datetime)
    assert result == datetime(2026, 11, 7, 12, 0, 0)


def test_datetime_deserializer_invalid_raises():
    """Тест 4 (datetime_deserializer): Некорректная дата вызывает ошибку валидации"""
    # Подготовка
    deserializer = datetime_deserializer()
    invalid_data = "не дата"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(invalid_data)


# 3. Тесты model_deserializer

def test_model_deserializer_range_with_nested_base():
    """Тест 5 (model_deserializer): Восстановление единицы измерения с вложенной базовой единицей"""
    # Подготовка
    deserializer = model_deserializer()
    data = {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "кг",
        "conversion_factor": 1000.0,
        "base_range": {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "грамм",
            "conversion_factor": 1.0,
            "base_range": None,
        },
    }

    # Действие
    result: range_model = deserializer.deserialize(data, range_model)

    # Проверка
    assert isinstance(result, range_model)
    assert result.id == "11111111-1111-1111-1111-111111111111"
    assert result.name == "кг"
    assert result.conversion_factor == 1000.0
    assert isinstance(result.base_range, range_model)
    assert result.base_range.name == "грамм"
    assert result.base_range.id == "22222222-2222-2222-2222-222222222222"


def test_model_deserializer_range_base_null_self_reference():
    """Тест 6 (model_deserializer): Базовая единица с base_range=None ссылается на саму себя"""
    # Подготовка
    deserializer = model_deserializer()
    data = {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "грамм",
        "conversion_factor": 1.0,
        "base_range": None,
    }

    # Действие
    result: range_model = deserializer.deserialize(data, range_model)

    # Проверка
    assert isinstance(result, range_model)
    assert result.id == "33333333-3333-3333-3333-333333333333"
    assert result.base_range == result


def test_model_deserializer_nomenclature_with_nested_models():
    """Тест 7 (model_deserializer): Рекурсивное восстановление номенклатуры с группой и единицей"""
    # Подготовка
    factory = deserialize_factory()
    nom_data = {
        "id": "nom-uuid-123",
        "name": "Мука",
        "full_name": "Мука пшеничная высший сорт",
        "group": {
            "id": "grp-uuid-1",
            "name": "Сырье",
        },
        "range": {
            "id": "rng-uuid-1",
            "name": "кг",
            "conversion_factor": 1000.0,
            "base_range": None,
        },
    }

    # Действие
    result: nomenclature_model = factory.deserialize(nom_data, nomenclature_model)

    # Проверка
    assert isinstance(result, nomenclature_model)
    assert result.id == "nom-uuid-123"
    assert result.name == "Мука"
    assert result.full_name == "Мука пшеничная высший сорт"
    assert isinstance(result.group, nomenclature_group_model)
    assert result.group.name == "Сырье"
    assert result.group.id == "grp-uuid-1"
    assert isinstance(result.range, range_model)
    assert result.range.name == "кг"


# 4. Тесты deserialize_factory

def test_deserialize_factory_create_picks_correct_deserializer():
    """Тест 8 (deserialize_factory): Фабрика подбирает десериализатор по типу"""
    # Подготовка
    factory = deserialize_factory()

    # Действие и Проверка
    assert isinstance(factory.create(int), basic_deserializer)
    assert isinstance(factory.create(str), basic_deserializer)
    assert isinstance(factory.create(datetime), datetime_deserializer)
    assert isinstance(factory.create(range_model), model_deserializer)
    assert isinstance(factory.create({"name": "Тест"}), model_deserializer)


def test_deserialize_factory_invalid_json_raises():
    """Тест 9 (deserialize_factory): Пустая или невалидная JSON строка вызывает ошибку"""
    # Подготовка
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        factory.deserialize_json("")


# 5. Главный интеграционный тест

def test_storage_manager_load_json_matches_original_models(tmp_path):
    """
    Тест 10 (Интеграционный): Сохранение storage_manager в JSON и восстановление
    Сравнивает загруженные модели со сформированными моделями в storage_manager
    """
    # Подготовка
    settings = settings_model()
    settings.is_first_start = True

    storage = storage_manager()
    storage.clear()
    storage.settings = settings

    # Фиксируем сформированные исходные модели
    original_ranges = list(storage.ranges)
    original_groups = list(storage.groups)
    original_storages = list(storage.storages)
    original_nomenclatures = list(storage.nomenclatures)
    original_recipes = list(storage.recipes)

    temp_file = str(tmp_path / "test_storage_dump.json")
    storage.save_json(temp_file)

    # Действие: загружаем данные обратно в хранилище через load_json
    load_success = storage.load_json(temp_file, replace=True)

    # Проверка 1: успешность загрузки и количество элементов
    assert load_success is True
    assert len(storage.ranges) == len(original_ranges)
    assert len(storage.groups) == len(original_groups)
    assert len(storage.storages) == len(original_storages)
    assert len(storage.nomenclatures) == len(original_nomenclatures)
    assert len(storage.recipes) == len(original_recipes)

    # Проверка 2: единицы измерения (совпадение id, наименований и коэффициентов)
    for loaded, orig in zip(storage.ranges, original_ranges):
        assert loaded == orig  # проверка равенства по id
        assert loaded.id == orig.id
        assert loaded.name == orig.name
        assert loaded.conversion_factor == orig.conversion_factor

    # Проверка 3: группы номенклатуры
    for loaded, orig in zip(storage.groups, original_groups):
        assert loaded == orig
        assert loaded.id == orig.id
        assert loaded.name == orig.name

    # Проверка 4: склады
    for loaded, orig in zip(storage.storages, original_storages):
        assert loaded == orig
        assert loaded.id == orig.id
        assert loaded.name == orig.name

    # Проверка 5: номенклатура (включая вложенные связи)
    for loaded, orig in zip(storage.nomenclatures, original_nomenclatures):
        assert loaded == orig
        assert loaded.id == orig.id
        assert loaded.name == orig.name
        assert loaded.full_name == orig.full_name
        assert loaded.group == orig.group
        assert loaded.group.name == orig.group.name
        assert loaded.range == orig.range
        assert loaded.range.name == orig.range.name

    # Проверка 6: рецепты и состав
    for loaded, orig in zip(storage.recipes, original_recipes):
        assert loaded == orig
        assert loaded.id == orig.id
        assert loaded.name == orig.name
        assert loaded.dish == orig.dish
        assert loaded.cooking_time == orig.cooking_time
        assert loaded.portions == orig.portions
        assert len(loaded.rows) == len(orig.rows)
        assert loaded.brutto == orig.brutto
        assert loaded.netto == orig.netto

        for loaded_row, orig_row in zip(loaded.rows, orig.rows):
            assert loaded_row.name == orig_row.name
            assert loaded_row.brutto == orig_row.brutto
            assert loaded_row.netto == orig_row.netto
            assert loaded_row.nomenclature == orig_row.nomenclature