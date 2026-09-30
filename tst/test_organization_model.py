import pytest
from src.core.exception import arguments_exception
from src.models import organization_model


def test_organization_model_create_legal_entity_success():
    """Сценарий: Успешное создание организации - Юр. лицо (ИНН 10 цифр)."""
    # Подготовка
    name = "ООО Ромашка"
    inn = "7701234567"
    bik = "044525225"
    account = "40702810123456789012"
    ownership_type = "ООО"

    # Действие
    org = organization_model(
        name=name,
        inn=inn,
        bik=bik,
        account=account,
        ownership_type=ownership_type,
    )

    # Проверка
    assert org.name == name
    assert org.inn == inn
    assert org.bik == bik
    assert org.account == account
    assert org.ownership_type == ownership_type


def test_organization_model_create_individual_entrepreneur_success():
    """Сценарий: Успешное создание организации - ИП (ИНН 12 цифр)."""
    # Подготовка
    name = "ИП Иванов"
    inn = "770123456789"
    bik = "044525225"
    account = "40802810123456789012"
    ownership_type = "ИП"

    # Действие
    org = organization_model(
        name=name,
        inn=inn,
        bik=bik,
        account=account,
        ownership_type=ownership_type,
    )

    # Проверка
    assert org.inn == inn


def test_organization_model_invalid_inn_raises_error():
    """Сценарий: Передача некорректного ИНН."""
    # Подготовка
    inn_9_digits = "123456789"
    inn_11_digits = "12345678901"
    inn_with_letter = "123456789A"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        organization_model(inn=inn_9_digits)

    with pytest.raises(arguments_exception):
        organization_model(inn=inn_11_digits)

    with pytest.raises(arguments_exception):
        organization_model(inn=inn_with_letter)


def test_organization_model_invalid_bik_raises_error():
    """Сценарий: Передача некорректного БИК."""
    # Подготовка
    bik_8_digits = "12345678"
    bik_10_digits = "1234567890"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        organization_model(bik=bik_8_digits)

    with pytest.raises(arguments_exception):
        organization_model(bik=bik_10_digits)


def test_organization_model_invalid_account_raises_error():
    """Сценарий: Передача некорректного счета."""
    # Подготовка
    short_account = "40702810"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        organization_model(account=short_account)


def test_organization_model_invalid_ownership_type_raises_error():
    """Сценарий: Пустая форма собственности."""
    # Подготовка
    empty_type = ""
    too_long_type = "СлишкомДлиннаяФорма"

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        organization_model(ownership_type=empty_type)

    with pytest.raises(arguments_exception):
        organization_model(ownership_type=too_long_type)