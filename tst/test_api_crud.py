from uuid import uuid4

import pytest

from main import api, storage_mgr
from src.logic.convert_factory import convert_factory

@pytest.fixture
def client():
    """
    Тестовый клиент Flask/Connexion.
    """
    return api.app.test_client()


@pytest.fixture(autouse=True)
def restore_storage():
    """
    Сохранение и восстановление состояния Singleton-хранилища.
    """
    original_data = {
        entity_type: list(collection)
        for entity_type, collection in storage_mgr.data.items()
    }

    yield

    storage_mgr.clear()

    for entity_type, collection in original_data.items():
        storage_mgr.get_collection(entity_type).extend(collection)


def test_get_report_formats(client):
    """
    Получение списка поддерживаемых форматов отчётов.
    """

    # Подготовка
    expected_formats = [
        "TXT",
        "CSV",
        "MARKDOWN",
        "XML",
        "HTML",
    ]

    # Действие
    response = client.get("/api/report-formats")

    # Проверка
    assert response.status_code == 200
    assert response.get_json() == expected_formats


def test_get_entities(client):
    """
    Получение списка доменных сущностей.
    """

    # Подготовка
    expected_keys = [
        "groups",
        "storages",
        "recipes",
        "nomenclatures",
        "ranges",
    ]

    # Действие
    response = client.get("/api/entities")

    # Проверка
    assert response.status_code == 200

    data = response.get_json()

    for key in expected_keys:
        assert key in data


def test_put_create_storage(client):
    """
    Успешное создание склада через PUT.
    """

    # Подготовка
    entity_id = str(uuid4())
    payload = {
        "name": "Тестовый склад",
    }

    # Действие
    response = client.put(
        f"/api/entities/storage_model/{entity_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == entity_id
    assert data["name"] == "Тестовый склад"


def test_put_duplicate_entity_returns_conflict(client):
    """
    Повторное создание сущности с одинаковым ID запрещено.
    """

    # Подготовка
    entity_id = str(uuid4())
    first_payload = {
        "name": "Первый склад",
    }
    second_payload = {
        "name": "Второй склад",
    }

    client.put(
        f"/api/entities/storage_model/{entity_id}",
        json=first_payload,
    )

    # Действие
    response = client.put(
        f"/api/entities/storage_model/{entity_id}",
        json=second_payload,
    )

    # Проверка
    assert response.status_code == 409


def test_put_id_mismatch_returns_bad_request(client):
    """
    ID в URL и JSON должны совпадать.
    """

    # Подготовка
    url_id = str(uuid4())
    json_id = str(uuid4())

    payload = {
        "id": json_id,
        "name": "Несовпадающий ID",
    }

    # Действие
    response = client.put(
        f"/api/entities/storage_model/{url_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 400


def test_put_missing_dependency_returns_server_error(client):
    """
    Создание сущности с отсутствующей связью запрещено.
    """

    # Подготовка
    entity_id = str(uuid4())

    payload = {
        "name": "Килограмм без грамма",
        "conversion_factor": 1000.0,
        "base_range": {
            "id": "missing-base-range-id",
            "name": "Несуществующая база",
            "conversion_factor": 1.0,
        },
    }

    # Действие
    response = client.put(
        f"/api/entities/range_model/{entity_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 500

    data = response.get_json()

    assert "detail" in data
    assert "Связанная" in data["detail"]


def test_get_entity_card(client):
    """
    Получение карточки существующей сущности.
    """

    # Подготовка
    entity = storage_mgr.ranges[0]

    # Действие
    response = client.get(
        f"/api/entities/range_model/{entity.id}",
    )

    # Проверка
    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == entity.id
    assert data["name"] == entity.name


def test_get_missing_entity_returns_not_found(client):
    """
    Получение отсутствующей сущности возвращает 404.
    """

    # Подготовка
    entity_id = "missing-range-id"

    # Действие
    response = client.get(
        f"/api/entities/range_model/{entity_id}",
    )

    # Проверка
    assert response.status_code == 404


def test_get_unknown_entity_type_returns_bad_request(client):
    """
    Неизвестный тип сущности запрещён.
    """

    # Подготовка
    entity_type = "unknown_model"
    entity_id = "some-id"

    # Действие
    response = client.get(
        f"/api/entities/{entity_type}/{entity_id}",
    )

    # Проверка
    assert response.status_code == 400


def test_patch_entity(client):
    """
    Частичное обновление сущности через PATCH.
    """

    # Подготовка
    entity_id = str(uuid4())

    client.put(
        f"/api/entities/storage_model/{entity_id}",
        json={
            "name": "Название до изменения",
        },
    )

    patch_payload = {
        "name": "Название после изменения",
    }

    # Действие
    response = client.patch(
        f"/api/entities/storage_model/{entity_id}",
        json=patch_payload,
    )

    # Проверка
    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == entity_id
    assert data["name"] == "Название после изменения"


def test_patch_id_is_forbidden(client):
    """
    Изменение ID через PATCH запрещено.
    """

    # Подготовка
    entity = storage_mgr.ranges[0]

    patch_payload = {
        "id": "new-forbidden-id",
    }

    # Действие
    response = client.patch(
        f"/api/entities/range_model/{entity.id}",
        json=patch_payload,
    )

    # Проверка
    assert response.status_code == 400


def test_patch_missing_entity_returns_not_found(client):
    """
    PATCH отсутствующей сущности возвращает 404.
    """

    # Подготовка
    entity_id = "missing-storage-id"
    patch_payload = {
        "name": "Новое имя",
    }

    # Действие
    response = client.patch(
        f"/api/entities/storage_model/{entity_id}",
        json=patch_payload,
    )

    # Проверка
    assert response.status_code == 404


def test_delete_free_entity(client):
    """
    Удаление независимой сущности.
    """

    # Подготовка
    entity_id = str(uuid4())

    create_response = client.put(
        f"/api/entities/storage_model/{entity_id}",
        json={
            "name": "Временный склад",
        },
    )

    assert create_response.status_code == 201

    # Действие
    delete_response = client.delete(
        f"/api/entities/storage_model/{entity_id}",
    )

    # Проверка
    assert delete_response.status_code == 200

    get_response = client.get(
        f"/api/entities/storage_model/{entity_id}",
    )

    assert get_response.status_code == 404


def test_delete_used_nomenclature_is_forbidden(client):
    """
    Удаление номенклатуры, используемой в рецепте.
    """

    # Подготовка
    recipe = storage_mgr.recipes[0]
    recipe_row = recipe.rows[0]
    nomenclature = recipe_row.nomenclature

    # Действие
    response = client.delete(
        f"/api/entities/nomenclature_model/{nomenclature.id}",
    )

    # Проверка
    assert response.status_code == 409

    data = response.get_json()

    assert "detail" in data
    assert "используется" in data["detail"]


def test_delete_used_group_is_forbidden(client):
    """
    Удаление группы, используемой номенклатурой.
    """

    # Подготовка
    nomenclature = storage_mgr.nomenclatures[0]
    group = nomenclature.group

    # Действие
    response = client.delete(
        f"/api/entities/nomenclature_group_model/{group.id}",
    )

    # Проверка
    assert response.status_code == 409

    data = response.get_json()

    assert "detail" in data
    assert "используется" in data["detail"]

def test_put_create_group(client):
    """
    Создание новой группы номенклатуры через PUT.
    """

    # Подготовка
    entity_id = str(uuid4())

    payload = {
        "name": "Тестовая группа",
    }

    # Действие
    response = client.put(
        f"/api/entities/nomenclature_group_model/{entity_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == entity_id
    assert data["name"] == "Тестовая группа"


def test_put_create_nomenclature_with_existing_references(client):
    """
    Создание номенклатуры с существующей группой и единицей измерения.
    """

    # Подготовка
    entity_id = str(uuid4())
    group = storage_mgr.groups[0]
    range_unit = storage_mgr.ranges[0]
    converter = convert_factory()

    payload = {
        "name": "Тестовая номенклатура",
        "full_name": "Тестовая номенклатура для API",
        "group": converter.convert(group),
        "range": converter.convert(range_unit),
    }

    # Действие
    response = client.put(
        f"/api/entities/nomenclature_model/{entity_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == entity_id
    assert data["name"] == "Тестовая номенклатура"
    assert data["full_name"] == "Тестовая номенклатура для API"
    assert data["group"]["id"] == group.id
    assert data["range"]["id"] == range_unit.id


def test_put_create_recipe_with_existing_dish(client):
    """
    Создание рецепта с существующей номенклатурой блюда.
    """

    # Подготовка
    entity_id = str(uuid4())
    dish = storage_mgr.nomenclatures[0]
    converter = convert_factory()

    payload = {
        "name": "Тестовый рецепт",
        "dish": converter.convert(dish),
        "cooking_time": 10,
        "instructions": [
            "Подготовить ингредиенты",
            "Выполнить технологическую операцию",
        ],
        "portions": 2,
        "rows": [],
    }

    # Действие
    response = client.put(
        f"/api/entities/recipe_model/{entity_id}",
        json=payload,
    )

    # Проверка
    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == entity_id
    assert data["name"] == "Тестовый рецепт"
    assert data["dish"]["id"] == dish.id
    assert data["cooking_time"] == 10
    assert data["portions"] == 2


def test_patch_nomenclature_reference(client):
    """
    Изменение группы существующей номенклатуры через PATCH.
    """

    # Подготовка
    nomenclature = storage_mgr.nomenclatures[0]
    new_group = storage_mgr.groups[-1]

    patch_payload = {
        "group_id": new_group.id,
    }

    # Действие
    response = client.patch(
        f"/api/entities/nomenclature_model/{nomenclature.id}",
        json=patch_payload,
    )

    # Проверка
    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == nomenclature.id
    assert data["group"]["id"] == new_group.id


def test_patch_missing_reference_returns_server_error(client):
    """
    Изменение связи на отсутствующую сущность запрещено.
    """

    # Подготовка
    nomenclature = storage_mgr.nomenclatures[0]

    patch_payload = {
        "group_id": "missing-group-id",
    }

    # Действие
    response = client.patch(
        f"/api/entities/nomenclature_model/{nomenclature.id}",
        json=patch_payload,
    )

    # Проверка
    assert response.status_code == 500
