import pytest
from main import storage_mgr
from src.core.filter_type_enum import filter_type_enum
from src.dtos.filter_dto import filter_dto
from src.dtos.filter_item_dto import filter_item_dto
from src.logic.prototype import prototype
from src.models import settings_model


@pytest.fixture(autouse=True)
def setup_storage():
    """Гарантирует чистое состояние хранилища перед каждым тестом."""
    settings = settings_model()
    settings.is_first_start = True
    storage_mgr.settings = settings


def test_prototype_clone_without_filter_returns_new_instance():
    """Клонирование без фильтра возвращает новый экземпляр прототипа с теми же данными."""
    ranges = storage_mgr.ranges
    pr = prototype(ranges)

    cloned = pr.clone()

    assert isinstance(cloned, prototype)
    assert cloned is not pr
    assert len(cloned.data) == len(ranges)


def test_prototype_filter_equals_name():
    """Фильтрация по наименованию с точным совпадением EQUALS."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    filter_rule = filter_item_dto(
        field_name="name",
        filter_type=filter_type_enum.EQUALS,
        value="Мука",
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) == 1
    assert cloned.data[0].name == "Мука"


def test_prototype_filter_like_name():
    """Фильтрация по наименованию с частичным совпадением LIKE (регистронезависимо)."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    filter_rule = filter_item_dto(
        field_name="name",
        filter_type=filter_type_enum.LIKE,
        value="печ",
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) >= 1
    assert all("печ" in item.name.lower() for item in cloned.data)


def test_prototype_filter_by_unique_code():
    """Фильтрация по уникальному коду (id)."""
    storages = storage_mgr.storages
    target = storages[0]
    pr = prototype(storages)

    filter_rule = filter_item_dto(
        field_name="id",
        filter_type=filter_type_enum.EQUALS,
        value=target.id,
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) == 1
    assert cloned.data[0].id == target.id


def test_prototype_filter_nested_base_range_name():
    """Фильтрация единиц измерения по вложенному свойству base_range.name."""
    ranges = storage_mgr.ranges
    pr = prototype(ranges)

    filter_rule = filter_item_dto(
        field_name="base_range.name",
        filter_type=filter_type_enum.EQUALS,
        value="грамм",
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) >= 1
    assert all(item.base_range and item.base_range.name == "грамм" for item in cloned.data)


def test_prototype_filter_nested_group_name():
    """Фильтрация номенклатуры по вложенной группе group.name."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    filter_rule = filter_item_dto(
        field_name="group.name",
        filter_type=filter_type_enum.EQUALS,
        value="Сырье",
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) >= 1
    assert all(item.group and item.group.name == "Сырье" for item in cloned.data)


def test_prototype_filter_nested_recipe_rows_nomenclature():
    """Фильтрация рецептов по вложенной коллекции rows.nomenclature.name."""
    recipes = storage_mgr.recipes
    pr = prototype(recipes)

    filter_rule = filter_item_dto(
        field_name="rows.nomenclature.name",
        filter_type=filter_type_enum.EQUALS,
        value="Мука",
    )
    cloned = pr.clone(filter_rule)

    assert len(cloned.data) >= 1
    # Рецепты, содержащие муку
    for recipe in cloned.data:
        has_flour = any(row.nomenclature and row.nomenclature.name == "Мука" for row in recipe.rows)
        assert has_flour is True


def test_prototype_chaining_clone():
    """Проверка цепочки клонирований (Method Chaining)."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    f1 = filter_item_dto("group.name", filter_type_enum.EQUALS, "Сырье")
    f2 = filter_item_dto("name", filter_type_enum.LIKE, "Мук")

    chained = pr.clone(f1).clone(f2)

    assert len(chained.data) == 1
    assert chained.data[0].name == "Мука"


def test_prototype_multi_filter_dto():
    """Проверка фильтрации через filter_dto со списком условий."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    composite_filter = filter_dto([
        filter_item_dto("group.name", filter_type_enum.EQUALS, "Сырье"),
        filter_item_dto("name", filter_type_enum.LIKE, "Сах"),
    ])

    cloned = pr.clone(composite_filter)

    assert len(cloned.data) == 1
    assert cloned.data[0].name == "Сахар"


def test_prototype_empty_data_safety():
    """Прототип корректно обрабатывает пустые списки данных."""
    pr = prototype([])
    f1 = filter_item_dto("name", filter_type_enum.EQUALS, "Тест")
    cloned = pr.clone(f1)

    assert isinstance(cloned, prototype)
    assert len(cloned.data) == 0


def test_contains_data_prototype():
    """Проверить работу прототипа при фильтрации транзакций."""
    f = filter_dto()
    item = filter_item_dto()
    item.field_name = "name"
    item.filter_type = filter_type_enum.LIKE
    item.value = "Поступление"
    f.filters = [item]

    transactions = storage_mgr.transactions
    pr = prototype(transactions)

    result = pr.clone(f)

    assert len(result.data) > 0
    assert all("Поступление" in t.name for t in result.data)


def test_prototype_empty_filter_dto_returns_all_data():
    """Пустой список фильтров в filter_dto возвращает все данные без изменений."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    f_empty = filter_dto([])
    res = pr.clone(f_empty)

    assert len(res.data) == len(nomenclatures)


def test_prototype_unknown_field_graceful_handling():
    """Несуществующее имя поля не вызывает исключение, а безопасно возвращает пустую выборку."""
    nomenclatures = storage_mgr.nomenclatures
    pr = prototype(nomenclatures)

    f_unknown = filter_item_dto("nonexistent_field.deep_property", filter_type_enum.EQUALS, "some_value")
    res = pr.clone(f_unknown)

    assert isinstance(res, prototype)
    assert len(res.data) == 0


def test_prototype_enum_and_uuid_matching():
    """Сопоставление Enum и UUID через common.match_value работает универсально."""
    from uuid import UUID
    from src.core.common import common

    # Enum со строкой
    assert common.match_value(filter_type_enum.LIKE, "LIKE", filter_type_enum.EQUALS) is True
    assert common.match_value("LIKE", filter_type_enum.LIKE, filter_type_enum.EQUALS) is True

    # UUID со строковым представлением
    target = storage_mgr.nomenclatures[0]
    uuid_obj = UUID(target.id)
    assert common.match_value(uuid_obj, target.id, filter_type_enum.EQUALS) is True
    assert common.match_value(target.id, uuid_obj, filter_type_enum.EQUALS) is True


def test_prototype_deep_nested_path_3_levels():
    """Фильтрация по глубокой вложенности на 3-4 уровня (rows.nomenclature.group.name)."""
    recipes = storage_mgr.recipes
    pr = prototype(recipes)

    f_deep = filter_item_dto(
        field_name="rows.nomenclature.group.name",
        filter_type=filter_type_enum.EQUALS,
        value="Сырье",
    )
    res = pr.clone(f_deep)

    assert len(res.data) > 0
    for r in res.data:
        assert any(row.nomenclature and row.nomenclature.group and row.nomenclature.group.name == "Сырье" for row in r.rows)
