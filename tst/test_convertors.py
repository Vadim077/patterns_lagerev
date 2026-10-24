from datetime import datetime
import pytest
import os
import json

from src.core.exception import arguments_exception
from src.logic.convert_factory import convert_factory
from src.logic.convertors.basic_convertor import basic_convertor
from src.logic.convertors.datetime_convertor import datetime_convertor
from src.logic.convertors.reference_convertor import reference_convertor
from src.logic.storage_manager import storage_manager
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    settings_model
)


class dated_stub:
    """Заглушка для проверки datetime_convertor"""

    @property
    def created_at(self) -> datetime:
        return datetime(2026, 10, 24, 15, 30, 0)

    @property
    def title(self) -> str:
        return "Тестовый объект с датой"


@pytest.fixture
def sample_data():
    """Фикстура с базовыми доменными моделями для тестов"""
    group = nomenclature_group_model(name="Сырье")
    kg = range_model.create_kilogramm()
    flour = nomenclature_model.create_flour(group, kg)
    sugar = nomenclature_model.create_sugar(group, kg)

    recipe = recipe_model(name="Песочное тесто", dish=flour)
    row1 = recipe_row_model.create_ingredient(flour, brutto=250.0, netto=240.0)
    row2 = recipe_row_model.create_ingredient(sugar, brutto=100.0, netto=100.0)
    recipe.add_row(row1)
    recipe.add_row(row2)

    return {
        "group": group,
        "kg": kg,
        "flour": flour,
        "sugar": sugar,
        "recipe": recipe,
        "row1": row1,
    }


# 1. Тесты для basic_convertor
def test_basic_convertor_numeric_and_strings(sample_data):
    """Тест 1 (basic_convertor): Числа и строки попадают в словарь, ссылка на базовую единицу пропускается"""
    # Подготовка
    kg = sample_data["kg"]
    convertor = basic_convertor()

    # Действие
    result = convertor.convert(kg)

    # Проверка
    assert result["name"] == "кг"
    assert result["conversion_factor"] == 1000.0
    assert result["id"] == kg.id
    assert "base_range" not in result


def test_basic_convertor_skips_references(sample_data):
    """Тест 2 (basic_convertor): Ссылочные свойства пропускабтся базовым конвертором"""
    # Подготовка
    flour = sample_data["flour"]
    convertor = basic_convertor()

    # Действие
    result = convertor.convert(flour)

    # Проверка
    assert result["name"] == flour.name
    assert result["full_name"] == flour.full_name
    assert result["id"] == flour.id
    assert "group" not in result
    assert "range" not in result


# 2. Тесты для datetime_convertor
def test_datetime_convertor_iso_format():
    """Тест 3 (datetime_convertor): Свойство datetime преобразуется в ISO 8601 строку"""
    # Подготовка
    stub = dated_stub()
    convertor = datetime_convertor()

    # Действие
    result = convertor.convert(stub)

    # Проверка
    assert result == {"created_at": "2026-10-24T15:30:00"}


def test_datetime_convertor_no_dates_returns_empty(sample_data):
    """Тест 4 (datetime_convertor): У модели без дат возвращается пустой словарь"""
    # Подготовка
    flour = sample_data["flour"]
    convertor = datetime_convertor()

    # Действие
    result = convertor.convert(flour)

    # Проверка
    assert result == {}


# 3. Тесты для reference_convertor
def test_reference_convertor_extracts_ids(sample_data):
    """Тест 5 (reference_convertor): Свойства-ссылки преобразуются в id связанных сущностей"""
    # Подготовка
    flour = sample_data["flour"]
    convertor = reference_convertor()

    # Действие
    result = convertor.convert(flour)

    # Проверка
    assert result["group"] == sample_data["group"].id
    assert result["range"] == sample_data["kg"].id
    assert "name" not in result
    assert "id" not in result


def test_reference_convertor_no_references_returns_empty():
    """Тест 6 (reference_convertor): При отсутствии ссылок возвращается пустой словарь"""
    # Подготовка
    group = nomenclature_group_model(name="Сырье")
    convertor = reference_convertor()

    # Действие
    result = convertor.convert(group)

    # Проверка
    assert result == {}


# 4. Тесты валидации (None)
@pytest.mark.parametrize(
    "convertor_instance",
    [basic_convertor(), datetime_convertor(), reference_convertor(), convert_factory()],
)
def test_convertors_none_raises_arguments_exception(convertor_instance):
    """Тест 7: Передача None вызывает arguments_exception во всех конверторах и фабрике"""
    # Подготовка
    invalid_source = None

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        convertor_instance.convert(invalid_source)



# 5. Тесты для convert_factory
def test_convert_factory_merges_all_convertors(sample_data):
    """Тест 8 (convert_factory): Фабрика объединяет базовые свойства и ссылки в единый словарь"""
    # Подготовка
    flour = sample_data["flour"]
    factory = convert_factory()

    # Действие
    result = factory.convert(flour)

    # Проверка
    assert result["id"] == flour.id
    assert result["name"] == flour.name
    assert result["full_name"] == flour.full_name
    assert result["group"] == sample_data["group"].id
    assert result["range"] == sample_data["kg"].id


def test_convert_factory_list_of_objects(sample_data):
    """Тест 9 (convert_factory): Список моделей конвертируется в список словарей"""
    # Подготовка
    items = [sample_data["flour"], sample_data["sugar"]]
    factory = convert_factory()

    # Действие
    result = factory.convert(items)

    # Проверка
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Мука"
    assert result[1]["name"] == "Сахар"


def test_convert_factory_dict_and_datetime_support():
    """Тест 10 (convert_factory): Поддержка словарей и дат"""
    # Подготовка
    data = {
        "event": dated_stub(),
        "metadata": {"source": "manual", "code": 101},
    }
    factory = convert_factory()

    # Действие
    result = factory.convert(data)

    # Проверка
    assert result["event"]["created_at"] == "2026-10-24T15:30:00"
    assert result["metadata"]["source"] == "manual"
    assert result["metadata"]["code"] == 101


def test_convert_factory_composite_recipe_with_nested_rows(sample_data):
    """Тест 11 (convert_factory): Полная сериализация составного рецепта с ингредиентами"""
    # Подготовка
    recipe = sample_data["recipe"]
    factory = convert_factory()

    # Действие
    result = factory.convert(recipe)

    # Проверка
    assert result["name"] == "Песочное тесто"
    assert result["dish"] == sample_data["flour"].id
    assert result["brutto"] == 350.0
    assert result["netto"] == 340.0
    assert isinstance(result["rows"], list)
    assert len(result["rows"]) == 2
    assert result["rows"][0]["nomenclature"] == sample_data["flour"].id
    assert result["rows"][0]["brutto"] == 250.0


def test_storage_manager_json_dump():
    """Тест 12: Выгрузка всех коллекций storage_manager в JSON"""

    # Подготовка
    settings = settings_model()
    settings.is_first_start = True

    storage = storage_manager()
    storage.clear()
    storage.settings = settings
    
    dump_path = "storage_dump.json"

    # Действие
    saved_file = storage.save_json(dump_path)

    # Проверка
    assert os.path.exists(saved_file)
    with open(saved_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert "ranges" in loaded
    assert "groups" in loaded
    assert "storages" in loaded
    assert "nomenclatures" in loaded
    assert "recipes" in loaded
    assert len(loaded["recipes"]) >= 2
    assert len(loaded["nomenclatures"]) >= 4