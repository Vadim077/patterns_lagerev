import os
import pytest
from datetime import datetime
from src.core.exception import arguments_exception
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.range_deserializer import range_deserializer
from src.logic.deserializers.nomenclature_group_deserializer import nomenclature_group_deserializer
from src.logic.deserializers.storage_deserializer import storage_deserializer
from src.logic.deserializers.nomenclature_deserializer import nomenclature_deserializer
from src.logic.deserializers.recipe_row_deserializer import recipe_row_deserializer
from src.logic.deserializers.recipe_deserializer import recipe_deserializer
from src.logic.deserialize_factory import deserialize_factory
from src.logic.deserializer import deserializer
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
    handler = basic_deserializer()

    # Действие
    val_int = handler.deserialize(42)
    val_float = handler.deserialize(3.14)
    val_str = handler.deserialize("Текст")
    val_bool = handler.deserialize(True)
    val_none = handler.deserialize(None)

    # Проверка
    assert val_int == 42
    assert val_float == 3.14
    assert val_str == "Текст"
    assert val_bool is True
    assert val_none is None


def test_basic_deserializer_type_conversion():
    """Тест 2 (basic_deserializer): Преобразование типов по требованию"""
    # Подготовка
    handler = basic_deserializer()

    # Действие
    int_res = handler.deserialize("100", int)
    bool_res = handler.deserialize("True", bool)

    # Проверка
    assert int_res == 100
    assert bool_res is True


# 2. Тесты datetime_deserializer

def test_datetime_deserializer_iso_format():
    """Тест 3 (datetime_deserializer): Парсинг ISO 8601 строки в datetime"""
    # Подготовка
    handler = datetime_deserializer()
    iso_str = "2026-11-07T12:00:00"

    # Действие
    result = handler.deserialize(iso_str)

    # Проверка
    assert isinstance(result, datetime)
    assert result == datetime(2026, 11, 7, 12, 0, 0)


def test_datetime_deserializer_invalid_raises():
    """Тест 4 (datetime_deserializer): Некорректная дата вызывает ошибку валидации"""
    # Подготовка
    handler = datetime_deserializer()
    invalid_data = "не дата"

    # Действие
    def act():
        handler.deserialize(invalid_data)

    # Проверка
    with pytest.raises(arguments_exception):
        act()


# 3. Тесты специализированных десериализаторов моделей (Extract Class)

def test_range_deserializer_with_nested_base():
    """Тест 5 (range_deserializer): Восстановление единицы измерения с вложенным base_range"""
    # Подготовка
    service = deserializer()
    handler = range_deserializer(service)
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
    result: range_model = handler.deserialize(data, range_model)

    # Проверка
    assert isinstance(result, range_model)
    assert result.id == "11111111-1111-1111-1111-111111111111"
    assert result.name == "кг"
    assert result.conversion_factor == 1000.0
    assert isinstance(result.base_range, range_model)
    assert result.base_range.name == "грамм"
    assert result.base_range.id == "22222222-2222-2222-2222-222222222222"


def test_nomenclature_deserializer():
    """Тест 6 (nomenclature_deserializer): Восстановление номенклатуры со связями"""
    # Подготовка
    service = deserializer()
    handler = nomenclature_deserializer(service)
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
    result: nomenclature_model = handler.deserialize(nom_data, nomenclature_model)

    # Проверка
    assert isinstance(result, nomenclature_model)
    assert result.id == "nom-uuid-123"
    assert result.name == "Мука"
    assert isinstance(result.group, nomenclature_group_model)
    assert result.group.name == "Сырье"
    assert isinstance(result.range, range_model)
    assert result.range.name == "кг"


def test_recipe_row_deserializer_with_sub_recipe():
    """Тест 7 (recipe_row_deserializer): Рекурсивное восстановление строки с полуфабрикатом"""
    # Подготовка
    service = deserializer()
    handler = recipe_row_deserializer(service)
    data = {
        "id": "row-uuid-1",
        "name": "Тесто",
        "nomenclature": {
            "id": "nom-uuid-semi",
            "name": "Песочное тесто",
        },
        "brutto": 500.0,
        "netto": 500.0,
        "sub_recipe": {
            "id": "sub-recipe-uuid-1",
            "name": "Песочное тесто",
            "cooking_time": 20,
            "portions": 1,
            "rows": [],
        },
    }

    # Действие
    result: recipe_row_model = handler.deserialize(data, recipe_row_model)

    # Проверка
    assert isinstance(result, recipe_row_model)
    assert result.sub_recipe is not None
    assert isinstance(result.sub_recipe, recipe_model)
    assert result.sub_recipe.name == "Песочное тесто"


# 4. Тесты чистой фабрики (deserialize_factory)

def test_deserialize_factory_create_picks_correct_deserializer():
    """Тест 8 (deserialize_factory): Фабрика подбирает десериализатор по типу"""
    # Подготовка
    factory = deserialize_factory()

    # Действие
    d_int = factory.create(int)
    d_str = factory.create(str)
    d_dt = factory.create(datetime)
    d_range = factory.create(range_model)
    d_group = factory.create(nomenclature_group_model)
    d_storage = factory.create(storage_model)
    d_nom = factory.create(nomenclature_model)
    d_row = factory.create(recipe_row_model)
    d_recipe = factory.create(recipe_model)

    # Проверка
    assert isinstance(d_int, basic_deserializer)
    assert isinstance(d_str, basic_deserializer)
    assert isinstance(d_dt, datetime_deserializer)
    assert isinstance(d_range, range_deserializer)
    assert isinstance(d_group, nomenclature_group_deserializer)
    assert isinstance(d_storage, storage_deserializer)
    assert isinstance(d_nom, nomenclature_deserializer)
    assert isinstance(d_row, recipe_row_deserializer)
    assert isinstance(d_recipe, recipe_deserializer)


# 5. Тесты координатора десериализации (deserializer)

def test_deserializer_invalid_json_raises():
    """Тест 9 (deserializer): Пустая строка вызывает ошибку валидации"""
    # Подготовка
    service = deserializer()

    # Действие
    def act():
        service.deserialize_json("")

    # Проверка
    with pytest.raises(arguments_exception):
        act()


def test_deserializer_identity_cache():
    """Тест 10 (deserializer): Кэш возвращает тот же объект в памяти (is identity)"""
    # Подготовка
    service = deserializer()
    range_data = {
        "id": "fixed-id-123",
        "name": "кг",
        "conversion_factor": 1000.0,
        "base_range": None,
    }

    # Действие
    obj1 = service.deserialize(range_data, range_model)
    obj2 = service.deserialize(range_data, range_model)

    # Проверка
    assert obj1 is obj2  # Ровно один объект в памяти!


# 6. Главный интеграционный тест хранилища (Универсальный цикл по storage.data.keys)

def test_storage_manager_load_json_matches_original_models(tmp_path):
    """
    Тест 11 (Интеграционный): Сохранение и загрузка storage_manager
    """
    # Подготовка
    settings = settings_model()
    settings.is_first_start = True

    storage = storage_manager()
    storage.clear()
    storage.settings = settings

    # Фиксируем сформированные исходные данные по ключам
    original_data = {key: list(items) for key, items in storage.data.items()}

    temp_file = str(tmp_path / "test_storage_dump.json")
    storage.save_json(temp_file)

    # Действие: загружаем данные обратно в хранилище через load_json
    load_success = storage.load_json(temp_file, replace=True)

    # Проверка 1: успешность загрузки
    assert load_success is True

    # Проверка 2: универсальный обход в цикле по всем ключам данных
    for key in storage.data.keys():
        loaded_items = storage.data[key]
        orig_items = original_data[key]
        assert len(loaded_items) == len(orig_items)
        for loaded_item, orig_item in zip(loaded_items, orig_items):
            assert loaded_item == orig_item
            assert loaded_item.id == orig_item.id
            assert loaded_item.name == orig_item.name

    # Проверка 3: ссылочная целостность в памяти (identity через 'is')
    flour = next(n for n in storage.nomenclatures if n.name == "Мука")
    sugar = next(n for n in storage.nomenclatures if n.name == "Сахар")
    assert flour.range is sugar.range

    # Проверка 4: восстановление полуфабриката (sub_recipe)
    cookie_recipe = next(r for r in storage.recipes if any(row.sub_recipe is not None for row in r.rows))
    dough_row = next(r for r in cookie_recipe.rows if r.sub_recipe is not None)
    assert isinstance(dough_row.sub_recipe, recipe_model)
    assert len(dough_row.sub_recipe.rows) > 0