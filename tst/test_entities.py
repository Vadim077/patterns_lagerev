from src.core.abstract_model import name_id
import pytest
from src.core.exception import arguments_exception

class test_entity(name_id):
    def __init__(self, name: str = None):
        super().__init__(name=name)


# 1. Добавлен префикс test_
def test_abstract_model_get_id_not_null():
    entity = test_entity()

    # Действие
    result = entity.id

    # Проверка
    assert result != ""


# 2. Второй тест
def test_abstract_model_id_is_unique():
    # Действие
    entity1 = test_entity(name="t1")
    entity2 = test_entity(name="t1")

    # Проверка
    assert entity1.id != entity2.id

# 3. Третий тест
def test_abstract_model_id_is_equal():
    entity1 = test_entity(name="t1")
    entity2 = test_entity(name="t2")
    custom_id = "test-uuid-12345"

    # Действие
    entity1.id = custom_id
    entity2.id = custom_id

    # Проверка
    assert entity1 == entity2

# # 4.
# def test_abstract_model_invalid_name_raises_error():
#     with pytest.raises(ValueError):
#         test_entity(name="   ")

#     with pytest.raises(ValueError):
#         test_entity(name="")

#     entity = test_entity(name="Корректное имя")
#     with pytest.raises(ValueError):
#         entity.name = ""

# 4. Четвертый тест
def test_abstract_model_invalid_name_raises_error():
    # Проверка на пробелы
    with pytest.raises(arguments_exception):
        test_entity(name="   ")

    # Проверка на пустую строку
    with pytest.raises(arguments_exception):
        test_entity(name="")

    # Проверка сеттера
    entity = test_entity(name="Корректное имя")
    with pytest.raises(arguments_exception):
        entity.name = ""