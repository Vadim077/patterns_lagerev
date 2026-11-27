import datetime
import pytest
from main import storage_mgr
from src.core.filter_type_enum import filter_type_enum
from src.dtos.filter_dto import filter_dto
from src.dtos.filter_item_dto import filter_item_dto
from src.dtos.turnover_row_dto import turnover_row_dto
from src.logic.turnover_service import turnover_service
from src.models import settings_model


@pytest.fixture(autouse=True)
def setup_storage():
    """Гарантирует чистое состояние хранилища перед каждым тестом."""
    settings = settings_model()
    settings.is_first_start = True
    storage_mgr.settings = settings


def test_turnover_service_build_all_movements():
    """Формирование ОСВ по всем транзакциям без фильтров."""
    service = turnover_service(storage_mgr)

    rows = service.build()

    assert len(rows) > 0
    assert all(isinstance(r, turnover_row_dto) for r in rows)

    # Проверка формулы баланса: конечное = начальное + приход - расход
    for r in rows:
        expected_closing = round(r.start_balance + r.receipts - r.expenditures, 4)
        assert r.end_balance == expected_closing


def test_turnover_service_period_partitioning_and_opening_balance():
    """Проверка разбиения движений на входящее сальдо и обороты за период."""
    service = turnover_service(storage_mgr)

    # Период: с 1 ноября 2026 по 20 ноября 2026
    date_from = datetime.datetime(2026, 11, 1, 0, 0)
    date_to = datetime.datetime(2026, 11, 20, 23, 59)

    rows = service.build(date_from=date_from, date_to=date_to)

    flour_row = next((r for r in rows if r.nomenclature_name == "Мука"), None)
    assert flour_row is not None

    # Поступление муки было 15 октября 2026 (100 кг = 100 000 г) -> это начальный остаток
    assert flour_row.start_balance == 100000.0

    # Расход был 10 и 15 ноября (20 кг + 5 кг = 25 кг = 25 000 г) -> это расход за период
    assert flour_row.expenditures == 25000.0
    assert flour_row.receipts == 0.0

    # Конечный остаток: 100 000 - 25 000 = 75 000 г
    assert flour_row.end_balance == 75000.0


def test_turnover_service_filter_by_nomenclature():
    """Фильтрация ОСВ по конкретной номенклатуре через DTO."""
    service = turnover_service(storage_mgr)

    f = filter_dto([
        filter_item_dto("nomenclature.name", filter_type_enum.EQUALS, "Сахар")
    ])

    rows = service.build(filter_instance=f)

    assert len(rows) == 1
    assert rows[0].nomenclature_name == "Сахар"
    assert rows[0].start_balance + rows[0].receipts - rows[0].expenditures == rows[0].end_balance


def test_turnover_service_filter_by_storage():
    """Фильтрация ОСВ по наименованию склада через LIKE."""
    service = turnover_service(storage_mgr)

    f = filter_dto([
        filter_item_dto("storage.name", filter_type_enum.LIKE, "Основн")
    ])

    rows = service.build(filter_instance=f)

    assert len(rows) > 0
    assert all("Основн" in r.storage_name for r in rows)


def test_turnover_service_period_passed_inside_filter_dto():
    """Передача диапазона дат внутри filter_dto."""
    service = turnover_service(storage_mgr)

    f = filter_dto([
        filter_item_dto("period", filter_type_enum.GREATER_EQUAL, "2026-11-01"),
        filter_item_dto("period", filter_type_enum.LESS_EQUAL, "2026-11-20"),
        filter_item_dto("nomenclature.name", filter_type_enum.EQUALS, "Мука"),
    ])

    rows = service.build(filter_instance=f)

    assert len(rows) == 1
    flour_row = rows[0]
    assert flour_row.start_balance == 100000.0
    assert flour_row.expenditures == 25000.0
    assert flour_row.end_balance == 75000.0


def test_turnover_service_opening_balance_with_no_movements_in_period():
    """Если за период движений не было, но был остаток до date_from, строка формируется с сальдо."""
    service = turnover_service(storage_mgr)

    # Период с 15 по 20 ноября: по сахару списание (-10 кг) было 12 ноября, поступление (+50 кг) 20 октября.
    # В самом периоде 15..20 ноября движений нет.
    date_from = datetime.datetime(2026, 11, 15, 0, 0)
    date_to = datetime.datetime(2026, 11, 20, 23, 59)

    f = filter_dto([
        filter_item_dto("nomenclature.name", filter_type_enum.EQUALS, "Сахар")
    ])

    rows = service.build(filter_instance=f, date_from=date_from, date_to=date_to)

    assert len(rows) == 1
    sugar_row = rows[0]
    # Начальный остаток: 50 кг - 10 кг = 40 кг = 40 000 г
    assert sugar_row.start_balance == 40000.0
    assert sugar_row.receipts == 0.0
    assert sugar_row.expenditures == 0.0
    assert sugar_row.end_balance == 40000.0
    # Единица измерения - именно базовая (грамм), а не производная (кг)
    assert sugar_row.range_name == "грамм"


def test_turnover_service_mixed_units_conversion_to_base_range():
    """Транзакции в разных единицах (кг и грамм) приводятся к базовой единице номенклатуры (грамм)."""
    from src.models import transaction_model

    service = turnover_service(storage_mgr)

    flour = next(n for n in storage_mgr.nomenclatures if n.name == "Мука")
    storage = storage_mgr.storages[0]
    gram = flour.range.base_range

    # Добавляем транзакцию списания непосредственно в базовой единице (граммах)
    tx_gram = transaction_model("Расход муки в граммах")
    tx_gram.storage = storage
    tx_gram.nomenclature = flour
    tx_gram.range = gram
    tx_gram.period = datetime.datetime(2026, 11, 16, 12, 0)
    tx_gram.value = -500.0  # -500 грамм
    storage_mgr.add_transaction(tx_gram)

    # Период: ноябрь 2026
    date_from = datetime.datetime(2026, 11, 1, 0, 0)
    date_to = datetime.datetime(2026, 11, 20, 23, 59)

    f = filter_dto([
        filter_item_dto("nomenclature.name", filter_type_enum.EQUALS, "Мука")
    ])

    rows = service.build(filter_instance=f, date_from=date_from, date_to=date_to)

    assert len(rows) == 1
    flour_row = rows[0]
    assert flour_row.range_name == "грамм"
    assert flour_row.start_balance == 100000.0
    # Расход: 20 кг (20 000 г) + 5 кг (5 000 г) + 500 г = 25 500 г
    assert flour_row.expenditures == 25500.0
    assert flour_row.end_balance == 74500.0
