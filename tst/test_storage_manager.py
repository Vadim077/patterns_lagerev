from src.logic.storage_manager import storage_manager
from src.models import settings_model


def test_storage_manager_singleton():
    """Тест 1 (Singleton): Два обращения к storage_manager возвращают один и тот же объект."""
    # Подготовка
    manager1 = storage_manager()
    manager2 = storage_manager()

    # Проверка
    assert manager1 == manager2


def test_storage_manager_first_start_false_empty():
    """Тест 2: При is_first_start = False коллекции не наполняются данными (остаются пустыми)."""
    # Подготовка
    settings = settings_model()
    settings.is_first_start = False
    manager = storage_manager()
    manager.clear()

    # Действие
    manager.settings = settings

    # Проверка
    assert len(manager.ranges) == 0
    assert len(manager.groups) == 0
    assert len(manager.storages) == 0
    assert len(manager.nomenclatures) == 0


def test_storage_manager_first_start_true_populates_data():
    """Тест 3: При is_first_start = True метод convert() генерирует первичные данные."""
    # Подготовка
    settings = settings_model()
    settings.is_first_start = True
    manager = storage_manager()

    # Действие
    manager.settings = settings

    # Проверка
    assert len(manager.ranges) >= 5
    assert len(manager.groups) >= 2
    assert len(manager.storages) >= 2
    assert len(manager.nomenclatures) >= 4


def test_storage_manager_nomenclature_integrity():
    """Тест 4: Проверка корректности связей сформированных данных (единицы измерения и группы)."""
    # Подготовка
    settings = settings_model()
    settings.is_first_start = True
    manager = storage_manager(settings)

    # Действие
    flour = next((item for item in manager.nomenclatures if item.name == "Мука"), None)
    egg = next((item for item in manager.nomenclatures if item.name == "Яйцо"), None)

    # Проверка
    assert flour is not None
    assert flour.group is not None
    assert flour.range is not None
    assert flour.range.name == "кг"
    assert flour.group.name == "Сырье"

    assert egg is not None
    assert egg.range.name == "штука"
    assert egg.group.name == "Ингредиенты"


def test_storage_manager_elements_uniqueness():
    """Тест 5: Каждый элемент уникален. Повторное добавление отклоняется."""
    # Подготовка
    settings = settings_model()
    settings.is_first_start = True
    manager = storage_manager(settings)
    initial_count = len(manager.ranges)
    existing_unit = manager.ranges[0]

    # Действие
    added = manager.add_range(existing_unit)

    # Проверка
    assert added is False
    assert len(manager.ranges) == initial_count