import json
import pytest
from datetime import datetime
from src.core.exception import arguments_exception
from src.dtos.report_result_dto import report_result_dto
from src.logic.deserializers.basic_deserializer import basic_deserializer
from src.logic.deserializers.datetime_deserializer import datetime_deserializer
from src.logic.deserializers.reference_deserializer import reference_deserializer
from src.logic.deserialize_factory import deserialize_factory
from src.logic.deserializer import deserializer
from src.logic.convert_factory import convert_factory
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

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        handler.deserialize(invalid_data)


# 3. Тесты шаблона 'Фабричный метод' (Factory Method) в доменных моделях и DTO

def test_range_model_factory_method_with_nested_base():
    """Тест 5 (range_model.create): Фабричный метод модели восстанавливает единицу с вложенным base_range"""
    # Подготовка
    service = deserializer()
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
    result: range_model = range_model.create(data, service=service)

    # Проверка
    assert isinstance(result, range_model)
    assert result.id == "11111111-1111-1111-1111-111111111111"
    assert result.name == "кг"
    assert result.conversion_factor == 1000.0
    assert isinstance(result.base_range, range_model)
    assert result.base_range.name == "грамм"
    assert result.base_range.id == "22222222-2222-2222-2222-222222222222"


def test_nomenclature_model_factory_method():
    """Тест 6 (nomenclature_model.create): Фабричный метод номенклатуры восстанавливает связи"""
    # Подготовка
    service = deserializer()
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
    result: nomenclature_model = nomenclature_model.create(nom_data, service=service)

    # Проверка
    assert isinstance(result, nomenclature_model)
    assert result.id == "nom-uuid-123"
    assert result.name == "Мука"
    assert isinstance(result.group, nomenclature_group_model)
    assert result.group.name == "Сырье"
    assert isinstance(result.range, range_model)
    assert result.range.name == "кг"


def test_recipe_row_model_factory_method_with_sub_recipe():
    """Тест 7 (recipe_row_model.create): Фабричный метод строки рецепта восстанавливает полуфабрикат"""
    # Подготовка
    service = deserializer()
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
    result: recipe_row_model = recipe_row_model.create(data, service=service)

    # Проверка
    assert isinstance(result, recipe_row_model)
    assert result.sub_recipe is not None
    assert isinstance(result.sub_recipe, recipe_model)
    assert result.sub_recipe.name == "Песочное тесто"


def test_report_result_dto_factory_method():
    """Тест 8 (report_result_dto.create): Фабричный метод DTO восстанавливает объект передачи данных"""
    # Подготовка
    service = deserializer()
    dto_data = {
        "id": "dto-uuid-999",
        "name": "Отчет по остаткам",
        "text": "Строка отчета 1\nСтрока отчета 2",
        "binary": [],
    }

    # Действие
    result: report_result_dto = report_result_dto.create(dto_data, service=service)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert result.id == "dto-uuid-999"
    assert result.name == "Отчет по остаткам"
    assert result.text == "Строка отчета 1\nСтрока отчета 2"
    assert result.binary == []


# 4. Тесты фабрики десериализаторов (deserialize_factory)

def test_deserialize_factory_create_picks_correct_deserializer():
    """Тест 9 (deserialize_factory): Фабрика подбирает десериализатор по типу"""
    # Подготовка
    factory = deserialize_factory()

    # Действие
    d_int = factory.create(int)
    d_str = factory.create(str)
    d_dt = factory.create(datetime)
    d_range = factory.create(range_model)
    d_nom = factory.create(nomenclature_model)
    d_dto = factory.create(report_result_dto)

    # Проверка
    assert isinstance(d_int, basic_deserializer)
    assert isinstance(d_str, basic_deserializer)
    assert isinstance(d_dt, datetime_deserializer)
    assert isinstance(d_range, reference_deserializer)
    assert isinstance(d_nom, reference_deserializer)
    assert isinstance(d_dto, reference_deserializer)


def test_deserialize_factory_register_new_model_class():
    """Тест 10 (deserialize_factory): OCP - Регистрация нового класса модели без изменения фабрики"""
    # Подготовка
    factory = deserialize_factory()

    class custom_test_model:
        @classmethod
        def create(cls, data: dict, service=None):
            instance = cls()
            instance.title = data.get("title")
            return instance

    factory.register_class(custom_test_model)
    service = deserializer(factory)
    result = service.deserialize({
        "type": "custom_test_model",
        "title": "Проверка",
    })

    assert isinstance(result, custom_test_model)
    assert result.title == "Проверка"


# 5. Тесты координатора десериализации (deserializer)

def test_deserializer_invalid_json_raises():
    """Тест 11 (deserializer): Пустая строка вызывает ошибку валидации"""
    # Подготовка
    service = deserializer()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        service.deserialize_json("")


def test_deserializer_identity_cache():
    """Тест 12 (deserializer): Кэш возвращает тот же объект в памяти (is identity)"""
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


def test_deserializer_cache_separates_model_types():
    service = deserializer()
    shared_id = "same-id"

    range_instance = service.deserialize({
        "id": shared_id,
        "name": "кг",
        "conversion_factor": 1000.0,
        "base_range": None,
    }, range_model)
    storage_instance = service.deserialize({
        "id": shared_id,
        "name": "Основной склад",
    }, storage_model)

    assert isinstance(range_instance, range_model)
    assert isinstance(storage_instance, storage_model)
    assert range_instance is not storage_instance


def test_deserializer_polymorphic_by_type_field():
    """Тест 13 (deserializer): Десериализация по полю 'type' без передачи target_type"""
    # Подготовка
    service = deserializer()
    data = {
        "type": "range_model",
        "id": "auto-type-id-1",
        "name": "литр",
        "conversion_factor": 1000.0,
        "base_range": None,
    }

    # Действие
    result = service.deserialize(data)

    # Проверка
    assert isinstance(result, range_model)
    assert result.name == "литр"
    assert result.id == "auto-type-id-1"


def test_deserializer_unknown_type_raises():
    """Тест 14 (deserializer): Неизвестный type вызывает контролируемое исключение arguments_exception"""
    # Подготовка
    service = deserializer()
    data = {
        "type": "unknown_future_model",
        "id": "unknown-id",
        "name": "тест",
    }

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        service.deserialize(data)


# 6. Главный интеграционный тест хранилища (Round-trip)

def test_storage_manager_load_json_matches_original_models(tmp_path):
    """
    Тест 15 (Интеграционный): Сохранение и загрузка storage_manager с проверкой всех полей и связей
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

    factory = convert_factory()
    for key, original_items in original_data.items():
        assert factory.convert(storage.data[key]) == factory.convert(original_items)

    # Проверка 3: ссылочная целостность в памяти (identity через 'is')
    flour = next(n for n in storage.nomenclatures if n.name == "Мука")
    sugar = next(n for n in storage.nomenclatures if n.name == "Сахар")
    assert flour.range is sugar.range

    # Проверка 4: восстановление полуфабриката (sub_recipe)
    cookie_recipe = next(r for r in storage.recipes if any(row.sub_recipe is not None for row in r.rows))
    dough_row = next(r for r in cookie_recipe.rows if r.sub_recipe is not None)
    assert isinstance(dough_row.sub_recipe, recipe_model)
    assert len(dough_row.sub_recipe.rows) > 0


def test_storage_manager_load_json_rejects_unknown_model_type(tmp_path):
    source = {
        storage_manager.range_key(): [{
            "type": "unknown_model",
            "id": "unknown-id",
            "name": "Неизвестный объект",
        }],
        storage_manager.group_key(): [],
        storage_manager.storage_key(): [],
        storage_manager.nomenclature_key(): [],
        storage_manager.recipe_key(): [],
    }
    file_path = tmp_path / "invalid_storage_dump.json"
    file_path.write_text(json.dumps(source), encoding="utf-8")

    storage = storage_manager()
    storage.clear()

    with pytest.raises(arguments_exception):
        storage.load_json(str(file_path))
