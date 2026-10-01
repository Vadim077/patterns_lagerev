from src.logic.settings_manager import settings_manager
from src.core.validator import operation_exeption


def test_not_raise_settings_manager_load():
    """Тест 1: Успешная загрузка настроек без исключений."""
    # Подготовка
    manager = settings_manager()

    # Действие и Проверка
    try:
        manager.load()
        assert True
    except operation_exeption:
        assert False
    except:
        assert False


def test_not_empty_settings_manager_load():
    """Тест 2: Настройки после загрузки не None."""
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except:
        assert False

    # Проверка
    assert manager.settings is not None


def test_equals_settings_manager_create():
    """Тест 3 (Singleton): Экземпляры менеджера ссылаются на один объект."""
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Проверка
    assert instance1 == instance2


def test_equals_properties_settings_manager_create():
    """Тест 4 (Singleton): Свойства настроек у обоих экземпляров синглтона идентичны."""
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Действие
    instance1.load()

    # Проверка
    assert instance1.settings == instance2.settings


def test_is_loaded_settings_manager_true():
    """Тест 5: Флаг is_loaded равен True после успешной загрузки."""
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except:
        assert False

    # Проверка
    assert manager.is_loaded