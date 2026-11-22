import pytest
from main import api, storage_mgr
from src.models import settings_model


@pytest.fixture(autouse=True)
def setup_storage():
    """Гарантирует чистое состояние хранилища перед каждым тестом."""
    settings = settings_model()
    settings.is_first_start = True
    storage_mgr.settings = settings


@pytest.fixture
def client():
    """Тестовый клиент API."""
    return api.app.test_client()


def test_api_filter_nomenclature_equals_name(client):
    """POST /api/entities/nomenclature_model/filter с точным совпадением по имени."""
    payload = {
        "filters": [
            {
                "field_name": "name",
                "filter_type": "EQUALS",
                "value": "Мука",
            }
        ]
    }

    response = client.post("/api/entities/nomenclature_model/filter", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Мука"


def test_api_filter_range_like_name(client):
    """POST /api/entities/range_model/filter с нестрогим поиском LIKE."""
    payload = {
        "filters": [
            {
                "field_name": "name",
                "filter_type": "LIKE",
                "value": "литр",
            }
        ]
    }

    response = client.post("/api/entities/range_model/filter", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all("литр" in item["name"].lower() for item in data)


def test_api_filter_recipe_nested_row_nomenclature(client):
    """POST /api/entities/recipe_model/filter с фильтрацией по вложенным ингредиентам."""
    payload = {
        "filters": [
            {
                "field_name": "rows.nomenclature.name",
                "filter_type": "EQUALS",
                "value": "Мука",
            }
        ]
    }

    response = client.post("/api/entities/recipe_model/filter", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_filter_invalid_entity_type_returns_400(client):
    """POST /api/entities/unknown_model/filter возвращает 400."""
    payload = {
        "filters": [
            {
                "field_name": "name",
                "filter_type": "EQUALS",
                "value": "Любое",
            }
        ]
    }

    response = client.post("/api/entities/unknown_model/filter", json=payload)

    assert response.status_code in (400, 404, 500)


def test_api_report_osv_without_filter(client):
    """POST /api/report/osv без фильтров возвращает полную ведомость."""
    response = client.post("/api/report/osv", json={})

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    for row in data:
        assert "storage_id" in row
        assert "nomenclature_name" in row
        assert "start_balance" in row
        assert "receipts" in row
        assert "expenditures" in row
        assert "end_balance" in row


def test_api_report_osv_with_period_filter(client):
    """POST /api/report/osv с фильтрацией по периоду дат."""
    payload = {
        "filters": [
            {
                "field_name": "period",
                "filter_type": "GREATER_EQUAL",
                "value": "2026-11-01",
            },
            {
                "field_name": "period",
                "filter_type": "LESS_EQUAL",
                "value": "2026-11-20",
            },
        ]
    }

    response = client.post("/api/report/osv", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

    flour_row = next((r for r in data if r["nomenclature_name"] == "Мука"), None)
    assert flour_row is not None
    assert flour_row["start_balance"] == 100000.0
    assert flour_row["expenditures"] == 25000.0
    assert flour_row["end_balance"] == 75000.0


def test_api_report_osv_filter_by_nomenclature(client):
    """POST /api/report/osv с фильтрацией по номенклатуре."""
    payload = {
        "filters": [
            {
                "field_name": "nomenclature.name",
                "filter_type": "EQUALS",
                "value": "Сахар",
            }
        ]
    }

    response = client.post("/api/report/osv", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["nomenclature_name"] == "Сахар"
