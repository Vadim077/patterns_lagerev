import pytest
from src.core.abstract_report import abstract_report
from src.core.exception import arguments_exception
from src.dtos.report_result_dto import report_result_dto
from src.dtos.report_type_enum import report_type_enum
from src.logic.text_report import text_report
from src.logic.csv_report import csv_report
from src.logic.markdown_report import markdown_report
from src.logic.xml_report import xml_report
from src.logic.html_report import html_report
from src.logic.report_factory import report_factory
from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    recipe_row_model,
    settings_model,
)


@pytest.fixture
def sample_models_fixture():
    """Фикстура с тестовыми моделями: группа, единица измерения, номенклатура и рецепт."""
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


def test_report_result_dto():
    """Тест 1: Проверка DTO результата отчета (текстовый и бинарный формат)."""
    # Подготовка
    text_data = "Тестовый отчет"
    binary_data = [1, 2, 3]

    # Действие
    dto = report_result_dto(text=text_data)

    # Проверка
    assert dto.text == text_data
    assert dto.binary == []

    # Действие: установка binary очищает text
    dto.binary = binary_data

    # Проверка
    assert dto.binary == binary_data
    assert dto.text == ""

    # Действие: установка text очищает binary
    dto.text = "Новый текст"

    # Проверка
    assert dto.text == "Новый текст"
    assert dto.binary == []


def test_text_report_build(sample_models_fixture):
    """Тест 2: Построение текстового отчета по технологической карте (рецепту)."""
    # Подготовка
    recipe = sample_models_fixture["recipe"]
    row1 = sample_models_fixture["row1"]
    report = text_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert "Код | Наименование | Брутто | Нетто\n" in result.text
    assert "Мука" in result.text
    assert "250.0" in result.text
    assert "240.0" in result.text
    assert "Сахар" in result.text
    assert "100.0" in result.text
    assert row1.unique_code in result.text


def test_csv_report_build_recipe_binary(sample_models_fixture):
    """Тест 3: Формирование CSV отчета с бинарными данными для скачивания."""
    # Подготовка
    recipe = sample_models_fixture["recipe"]
    report = csv_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    assert result.text == ""

    decoded_text = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто\n" in decoded_text
    assert "Мука;250.0;240.0" in decoded_text
    assert "Сахар;100.0;100.0" in decoded_text


def test_markdown_report_build_recipe_binary(sample_models_fixture):
    """Тест 4: Формирование Markdown отчета с бинарными данными для скачивания."""
    # Подготовка
    recipe = sample_models_fixture["recipe"]
    report = markdown_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    assert result.text == ""

    decoded_text = bytes(result.binary).decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in decoded_text
    assert "| Мука | 250.0 | 240.0 |" in decoded_text


def test_xml_report_build_nomenclature(sample_models_fixture):
    """Тест 5: Формирование структурированного XML отчета по номенклатуре."""
    # Подготовка
    flour = sample_models_fixture["flour"]
    report = xml_report()

    # Действие
    result = report.build(flour)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) == 0
    assert '<?xml version="1.0" encoding="utf-8"?>' in result.text
    assert f'<nomenclature id="{flour.unique_code}" name="{flour.name}">' in result.text
    assert f"<full_name>{flour.full_name}</full_name>" in result.text
    assert "<group>Сырье</group>" in result.text


def test_html_report_build_range(sample_models_fixture):
    """Тест 6: Формирование структурированного HTML отчета по единице измерения."""
    # Подготовка
    kg = sample_models_fixture["kg"]
    report = html_report()

    # Действие
    result = report.build(kg)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) == 0
    assert "<!DOCTYPE html>" in result.text
    assert f"<h2>Единица измерения: {kg.name}</h2>" in result.text
    assert f"<td>{kg.unique_code}</td>" in result.text
    assert f"<td>{kg.conversion_factor}</td>" in result.text


def test_report_factory_create():
    """Тест 7: Фабрика создает корректный экземпляр текстового отчета."""
    # Подготовка
    factory = report_factory()

    # Действие
    report = factory.create(report_type_enum.TXT)

    # Проверка
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)


def test_report_factory_create_all_types():
    """Тест 8: Фабрика корректно инстанцирует все форматы отчетов."""
    # Подготовка
    factory = report_factory()

    # Действие и Проверка
    assert isinstance(factory.create(report_type_enum.CSV), csv_report)
    assert isinstance(factory.create(report_type_enum.MARKDOWN), markdown_report)
    assert isinstance(factory.create(report_type_enum.XML), xml_report)
    assert isinstance(factory.create(report_type_enum.HTML), html_report)


def test_report_factory_create_default():
    """Тест 9: Фабрика создает отчет по умолчанию в зависимости от настроек."""
    # Подготовка
    settings = settings_model()
    settings.response_format = report_type_enum.XML
    factory = report_factory(settings=settings)

    # Действие
    default_report = factory.create_default()

    # Проверка
    assert isinstance(default_report, xml_report)


def test_report_factory_unsupported_type_raises_error():
    """Тест 10: Фабрика выбрасывает arguments_exception при неподдерживаемом типе отчета."""
    # Подготовка
    factory = report_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        factory.create("UNKNOWN_TYPE")


def test_report_invalid_source_raises_error():
    """Тест 11: Отчет выбрасывает arguments_exception при некорректном типе источника."""
    # Подготовка
    report = text_report()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        report.build("некорректная_строка_вместо_модели")
