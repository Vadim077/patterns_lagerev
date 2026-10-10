import pytest
from src.core.exception import arguments_exception
from src.models import (
    range_model,
    nomenclature_group_model,
    nomenclature_model,
    recipe_row_model,
    recipe_model,
)


@pytest.fixture
def ingredients_fixture():
    """Фикстура: базовые группы, единицы измерения и номенклатура для тестов."""
    kg = range_model.create_kilogramm()
    gram = kg.base_range
    piece = range_model.create_piece()

    raw_group = nomenclature_group_model.create_raw()
    ing_group = nomenclature_group_model.create_ingredients()
    semi_group = nomenclature_group_model.create_semi_finished()
    prod_group = nomenclature_group_model.create_products()
    pkg_group = nomenclature_group_model.create_packaging()

    flour = nomenclature_model.create_flour(raw_group, kg)
    sugar = nomenclature_model.create_sugar(raw_group, kg)
    butter = nomenclature_model.create_butter(ing_group, kg)
    egg = nomenclature_model.create_egg(ing_group, piece)
    dough_nom = nomenclature_model.create_dough(semi_group, kg)
    cookie_nom = nomenclature_model.create_cookie(prod_group, piece)
    box_nom = nomenclature_model.create_packaging_box(pkg_group, piece)

    return {
        "flour": flour,
        "sugar": sugar,
        "butter": butter,
        "egg": egg,
        "dough_nom": dough_nom,
        "cookie_nom": cookie_nom,
        "box_nom": box_nom,
        "gram": gram,
    }


def test_recipe_row_create_ingredient(ingredients_fixture):
    """Тест 1: Успешное создание строки ингредиента через фабричный метод."""
    # Подготовка
    flour = ingredients_fixture["flour"]
    gram = ingredients_fixture["gram"]

    # Действие
    row = recipe_row_model.create_ingredient(flour, brutto=250.0, netto=240.0, range_unit=gram)

    # Проверка
    assert row.name == "Мука"
    assert row.nomenclature == flour
    assert row.brutto == 250.0
    assert row.netto == 240.0
    assert row.range == gram
    assert row.sub_recipe is None


def test_recipe_row_invalid_negative_weight_raises_error(ingredients_fixture):
    """Тест 2: Отрицательный вес брутто или нетто выбрасывает arguments_exception."""
    # Подготовка
    sugar = ingredients_fixture["sugar"]

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        recipe_row_model(nomenclature=sugar, brutto=-10.0)

    with pytest.raises(arguments_exception):
        recipe_row_model(nomenclature=sugar, brutto=100.0, netto=-5.0)


def test_recipe_model_create(ingredients_fixture):
    """Тест 3: Создание технологической карты и заполнение основных свойств."""
    # Подготовка
    cookie_nom = ingredients_fixture["cookie_nom"]
    instructions = ["Замесить тесто", "Выпекать 15 минут"]

    # Действие
    recipe = recipe_model(
        name="Песочное печенье",
        dish=cookie_nom,
        cooking_time=25,
        instructions=instructions,
        portions=10,
    )

    # Проверка
    assert recipe.name == "Песочное печенье"
    assert recipe.dish == cookie_nom
    assert recipe.cooking_time == 25
    assert recipe.portions == 10
    assert len(recipe.instructions) == 2
    assert len(recipe.rows) == 0


def test_recipe_model_brutto_netto_calculation(ingredients_fixture):
    """Тест 4: Расчет веса брутто и нетто путем сложения веса ингредиентов."""
    # Подготовка
    dough_nom = ingredients_fixture["dough_nom"]
    flour = ingredients_fixture["flour"]
    butter = ingredients_fixture["butter"]
    sugar = ingredients_fixture["sugar"]

    recipe = recipe_model(name="Тесто", dish=dough_nom)
    row_flour = recipe_row_model.create_ingredient(flour, brutto=250.0, netto=250.0)
    row_butter = recipe_row_model.create_ingredient(butter, brutto=150.0, netto=150.0)
    row_sugar = recipe_row_model.create_ingredient(sugar, brutto=100.0, netto=100.0)

    # Действие
    recipe.add_row(row_flour)
    recipe.add_row(row_butter)
    recipe.add_row(row_sugar)

    # Проверка
    assert recipe.brutto == 500.0
    assert recipe.netto == 500.0


def test_recipe_model_dynamic_recalculation_on_add_and_remove_row(ingredients_fixture):
    """Тест 5: Динамический пересчет веса при добавлении и удалении ингредиентов."""
    # Подготовка
    dough_nom = ingredients_fixture["dough_nom"]
    flour = ingredients_fixture["flour"]
    sugar = ingredients_fixture["sugar"]

    recipe = recipe_model(name="Тесто", dish=dough_nom)
    row_flour = recipe_row_model.create_ingredient(flour, brutto=250.0, netto=250.0)
    row_sugar = recipe_row_model.create_ingredient(sugar, brutto=100.0, netto=100.0)
    recipe.add_row(row_flour)

    # Проверка исходного веса
    assert recipe.brutto == 250.0

    # Действие 1: Добавляем сахар
    recipe.add_row(row_sugar)

    # Проверка 1: Вес пересчитался
    assert recipe.brutto == 350.0
    assert recipe.netto == 350.0

    # Действие 2: Удаляем сахар по объекту
    removed_sugar = recipe.remove_row(row_sugar)

    # Проверка 2: Вес вернулся к исходному
    assert removed_sugar is True
    assert recipe.brutto == 250.0

    # Действие 3: Удаляем муку по ID
    removed_flour = recipe.remove_row(row_flour.id)

    # Проверка 3: Список пуст, вес 0
    assert removed_flour is True
    assert recipe.brutto == 0.0
    assert recipe.netto == 0.0


def test_recipe_model_recursive_semi_finished_calculation(ingredients_fixture):
    """Тест 6: Рекурсивный расчет веса полуфабриката в составе готового блюда (блюдо в блюде)."""
    # Подготовка: Создаем рецепт полуфабриката (Песочное тесто)
    dough_nom = ingredients_fixture["dough_nom"]
    cookie_nom = ingredients_fixture["cookie_nom"]
    flour = ingredients_fixture["flour"]
    butter = ingredients_fixture["butter"]
    sugar = ingredients_fixture["sugar"]
    egg = ingredients_fixture["egg"]

    dough_recipe = recipe_model.create_dough_recipe(dough_nom, flour, butter, sugar, egg)
    # Мука 250 + Масло 150 + Сахар 100 + Яйцо 60 (брутто) / 50 (нетто)
    assert dough_recipe.brutto == 560.0
    assert dough_recipe.netto == 550.0

    # Действие: Создаем рецепт готового блюда, куда полуфабрикат включен как строка
    cookie_recipe = recipe_model(name="Печенье Ромашка", dish=cookie_nom)
    semi_finished_row = recipe_row_model.create_semi_finished(dough_nom, sub_recipe=dough_recipe)
    cookie_recipe.add_row(semi_finished_row)

    # Проверка: Вес печенья рекурсивно равен весу теста
    assert cookie_recipe.brutto == 560.0
    assert cookie_recipe.netto == 550.0

    # Действие 2: Динамически добавляем в полуфабрикат еще 50 г муки
    extra_flour = recipe_row_model.create_ingredient(flour, brutto=50.0, netto=50.0)
    dough_recipe.add_row(extra_flour)

    # Проверка 2: Вес готового блюда автоматически и рекурсивно увеличился
    assert dough_recipe.brutto == 610.0
    assert cookie_recipe.brutto == 610.0
    assert cookie_recipe.netto == 600.0


def test_recipe_model_with_packaging(ingredients_fixture):
    """Тест 7: Рецепт с упаковкой — упаковка увеличивает брутто, но нетто остается чистым."""
    # Подготовка
    cookie_nom = ingredients_fixture["cookie_nom"]
    dough_nom = ingredients_fixture["dough_nom"]
    box_nom = ingredients_fixture["box_nom"]
    flour = ingredients_fixture["flour"]
    butter = ingredients_fixture["butter"]
    sugar = ingredients_fixture["sugar"]
    egg = ingredients_fixture["egg"]

    dough_recipe = recipe_model.create_dough_recipe(dough_nom, flour, butter, sugar, egg)

    # Действие
    cookie_recipe = recipe_model.create_cookie_recipe(cookie_nom, dough_nom, dough_recipe, box_nom)

    # Проверка:
    # Брутто = 560 г (тесто) + 20 г (коробка) = 580 г
    # Нетто = 550 г (тесто) + 0 г (коробка) = 550 г
    assert cookie_recipe.brutto == 580.0
    assert cookie_recipe.netto == 550.0