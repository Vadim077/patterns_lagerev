import pytest

flask = pytest.importorskip("flask")
connexion = pytest.importorskip("connexion")

from main import api, storage_mgr


@pytest.fixture
def client():
    """Тестовый HTTP клиент FlaskApp."""
    return api.app.test_client()


def test_api_entities_list(client):
    """Тест API 1: Получение списка доступных сущностей."""
    # Подготовка и Действие
    response = client.get("/api/entities")

    # Проверка
    assert response.status_code == 200
    data = response.get_json()
    assert "recipes" in data
    assert "nomenclatures" in data
    assert "ranges" in data
    assert len(data["recipes"]) > 0


def test_api_get_report_by_format_txt(client):
    """Тест API 2: Получение отчета по рецепту в формате TXT."""
    # Подготовка
    recipe = storage_mgr.recipes[0]

    # Действие
    response = client.get(f"/api/report/txt/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert "text/plain" in response.content_type
    text_content = response.get_data(as_text=True)
    assert f"=== Отчет: {recipe.name} ===" in text_content
    assert recipe.id in text_content


def test_api_get_report_by_format_csv_download(client):
    """Тест API 3: Скачивание CSV отчета в виде бинарных данных."""
    # Подготовка
    recipe = storage_mgr.recipes[0]

    # Действие
    response = client.get(f"/api/report/csv/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert ".csv" in response.headers.get("Content-Disposition", "")
    decoded_text = response.get_data(as_text=True)
    assert "field;value" in decoded_text
    assert recipe.name in decoded_text


def test_api_get_report_by_format_markdown_download(client):
    """Тест API 4: Скачивание Markdown отчета в виде бинарных данных."""
    # Подготовка
    recipe = storage_mgr.recipes[0]

    # Действие
    response = client.get(f"/api/report/markdown/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert "text/markdown" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert ".md" in response.headers.get("Content-Disposition", "")
    decoded_text = response.get_data(as_text=True)
    assert f"# {recipe.name}" in decoded_text


def test_api_get_report_by_format_xml(client):
    """Тест API 5: Получение структурированного XML отчета по номенклатуре."""
    # Подготовка
    nom = storage_mgr.nomenclatures[0]

    # Действие
    response = client.get(f"/api/report/xml/nomenclature/{nom.id}")

    # Проверка
    assert response.status_code == 200
    assert "application/xml" in response.content_type
    xml_content = response.get_data(as_text=True)
    assert "<?xml" in xml_content
    assert f"<id>{nom.id}</id>" in xml_content
    assert f"<name>{nom.name}</name>" in xml_content


def test_api_get_report_by_format_html(client):
    """Тест API 6: Получение структурированного HTML отчета по единице измерения."""
    # Подготовка
    rg = storage_mgr.ranges[0]

    # Действие
    response = client.get(f"/api/report/html/range/{rg.id}")

    # Проверка
    assert response.status_code == 200
    assert "text/html" in response.content_type
    html_content = response.get_data(as_text=True)
    assert "<!DOCTYPE html>" in html_content
    assert f"<h2>Отчет: {rg.name}</h2>" in html_content


def test_api_get_report_default(client):
    """Тест API 7: Получение отчета через метод create_default."""
    # Подготовка
    recipe = storage_mgr.recipes[0]

    # Действие
    response = client.get(f"/api/report/default/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    # В настройках по умолчанию задан Markdown -> возвращает вложение .md
    assert "attachment" in response.headers.get("Content-Disposition", "")


def test_api_get_report_query_params(client):
    """Тест API 8: Получение отчета через query параметры /api/get_report."""
    # Подготовка
    recipe = storage_mgr.recipes[0]

    # Действие
    response = client.get(f"/api/get_report?format=html&type=recipe&id={recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_api_not_found_returns_404(client):
    """Тест API 9: Запрос несуществующей сущности возвращает 404."""
    # Действие
    response = client.get("/api/report/txt/recipe/non-existent-uuid-12345")

    # Проверка
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
